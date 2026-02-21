#!/usr/bin/env python3
"""End-to-end schema workflow test for staging models.

Workflow:
1. Optionally create/use a test Neo4j database.
2. Apply generated constraints from staging/stagingdb_constraints_mcp.cypher.
3. Load sample data using Pydantic models from staging/schema_models.py.
4. Validate inserted data against staging/schema_description.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

from neo4j import GraphDatabase
from neo4j.exceptions import ClientError

# Local generated models (support both direct script execution and package import)
try:
    import staging.schema_models as schema_models
except ModuleNotFoundError:
    import schema_models as schema_models


@dataclass
class Neo4jConfig:
    uri: str
    username: str
    password: str


def get_neo4j_config() -> Neo4jConfig:
    uri = os.getenv("NEO4J_MODEL_DB_URL", "bolt://localhost:7687")
    username = os.getenv("NEO4J_MODEL_DB_USERNAME", "neo4j")
    password = os.getenv("NEO4J_MODEL_DB_PASSWORD")
    if not password:
        raise RuntimeError("NEO4J_MODEL_DB_PASSWORD is required")
    return Neo4jConfig(uri=uri, username=username, password=password)


def build_subclass_map(data_model_path: Path) -> Dict[str, str]:
    """Read full_schema_data_model.json and return {child_pascal -> parent_pascal} map."""
    def _pascal(label: str) -> str:
        """Mirror _to_pascal_case_label: leading numeric tokens become a suffix."""
        tokens = re.findall(r"[A-Za-z0-9]+", str(label or ""))
        if not tokens:
            return "Model"
        if tokens[0].isdigit():
            suffix = tokens[0]
            head = "".join(t.capitalize() for t in tokens[1:]) or "Model"
            return f"{head}_{suffix}"
        return "".join(t.capitalize() for t in tokens) or "Model"

    if not data_model_path.exists():
        return {}
    raw = json.loads(data_model_path.read_text(encoding="utf-8"))
    subclass_map: Dict[str, str] = {}
    for rel in raw.get("relationships", []):
        if rel.get("type") == "rdfs__subClassOf":
            child = _pascal(rel["start_node_label"])
            parent = _pascal(rel["end_node_label"])
            subclass_map.setdefault(child, parent)
    return subclass_map


def _label_chain(label: str, subclass_map: Dict[str, str]) -> str:
    """Return a Cypher multi-label string for a class and all its ancestors.

    e.g. 'TaxPayer' -> '`TaxPayer`:`Person`'
    """
    parts = [f"`{label}`"]
    cur = label
    while cur in subclass_map:
        cur = subclass_map[cur]
        parts.append(f"`{cur}`")
    return ":".join(parts)


def parse_constraints_file(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    stmts: List[str] = []
    current: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt:
                stmts.append(stmt)
            current = []
    if current:
        stmt = "\n".join(current).strip()
        if stmt:
            stmts.append(stmt)
    return stmts


def parse_schema_description(path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Dict[str, Dict[str, Set[str]]]]:
    """Parse schema_description.md.

    Returns:
    - mandatory_props_by_class: {ClassLabel -> {prop aliases}}
    - enum_members_by_class: {EnumClassLabel -> {member labels}}
    - topology_map: {SourceClassLabel -> {rel_type -> {TargetClassLabel}}}
    """
    lines = path.read_text(encoding="utf-8").splitlines()

    mandatory_props_by_class: Dict[str, Set[str]] = {}
    enum_members_by_class: Dict[str, Set[str]] = {}
    topology_map: Dict[str, Dict[str, Set[str]]] = {}

    section = None
    for line in lines:
        if line.startswith("## Section 3:"):
            section = 3
            continue
        if line.startswith("## Section 4:"):
            section = 4
            continue
        if line.startswith("## Section 5:"):
            section = 5
            continue
        if line.startswith("## Section "):
            section = None
            continue

        if section == 3 and line.startswith("|") and not line.startswith("| ---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4 and parts[0] != "Node Label":
                node_label, prop, _, mandatory = parts[:4]
                if mandatory.lower() == "yes":
                    mandatory_props_by_class.setdefault(node_label, set()).add(prop)

        elif section == 4 and line.startswith("- `(:"):
            m = re.match(r"- `\(:([^\)]+)\)-\[:([^\]]+)\]->\(:([^\)]+)\)`", line)
            if m:
                src, rel, tgt = m.groups()
                topology_map.setdefault(src, {}).setdefault(rel, set()).add(tgt)

        elif section == 5 and line.startswith("|") and not line.startswith("| ---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0] != "Enum Class":
                enum_class, member_label, _ = parts[:3]
                enum_members_by_class.setdefault(enum_class, set()).add(member_label)

    return mandatory_props_by_class, enum_members_by_class, topology_map


def ensure_test_database(driver, db_name: str) -> None:
    """Attempt to create test DB if server supports it and credentials allow."""
    try:
        with driver.session(database="system") as session:
            session.run(f"CREATE DATABASE `{db_name}` IF NOT EXISTS")
    except Exception:
        # Community edition or limited privileges; continue with existing DB.
        pass


def resolve_database_with_fallback(driver, preferred_db: str) -> str:
    """Return a usable database name, falling back when preferred DB is unavailable."""
    try:
        with driver.session(database=preferred_db) as session:
            session.run("RETURN 1 AS ok").consume()
        return preferred_db
    except ClientError as exc:
        if "DatabaseNotFound" not in str(exc):
            raise

    fallback_db = os.getenv("NEO4J_STAGING_DB_NAME", "stagingdb")
    with driver.session(database=fallback_db) as session:
        session.run("RETURN 1 AS ok").consume()
    print(
        f"Warning: database '{preferred_db}' not found; using fallback database '{fallback_db}'"
    )
    return fallback_db


def apply_constraints(driver, db_name: str, constraints_path: Path) -> int:
    statements = parse_constraints_file(constraints_path)
    applied = 0
    with driver.session(database=db_name) as session:
        for stmt in statements:
            # File includes comment-only lines; apply executable Cypher only.
            if not stmt.upper().startswith("CREATE CONSTRAINT"):
                continue
            session.run(stmt)
            applied += 1
    return applied


def _to_neo4j_props(data: Dict[str, object]) -> Dict[str, object]:
    """Keep only Neo4j property-compatible values."""
    out: Dict[str, object] = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            out[key] = value
            continue
        if isinstance(value, list) and all(isinstance(v, (str, int, float, bool)) for v in value):
            out[key] = value
    return out


def load_sample_data(
    driver,
    db_name: str,
    test_run: str,
    enum_members_by_class: Dict[str, Set[str]],
    subclass_map: Dict[str, str],
) -> Set[str]:
    """Load sample entities for each class using generated schema_models classes.

    Subclass nodes receive multi-labels so a TaxPayer node is (:TaxPayer:Person).
    """

    employer = schema_models.Employer(
        has_address=["1 Main St, New York, NY 10001"],
        has_ein="12-3456789",
        has_employer_name="Acme Corp",
        has_phone_number=["+1-212-555-0101"],
    )
    person = schema_models.Person(
        has_age=["37"],
        has_citizenship=["United States"],
        has_date_of_birth="1988-06-15",
        has_date_of_death=None,
        has_name=["Alex Doe"],
        has_place_of_birth="New York",
        has_residence=["101 Main St, New York, NY 10001"],
        has_tax_id=["999-88-7777"],
        is_employed_by=[employer],
    )
    money = schema_models.MonetaryAmount(
        has_amount="1234.56",
        is_denominated_in=schema_models.Currency.US_DOLLAR,
    )
    exchange = schema_models.Exchange()
    organization = schema_models.Organization(
        has_ein="98-7654321",
        has_tax_id="98-7654321",
    )
    taxpayer = schema_models.TaxPayer(
        has_age=["35"],
        has_citizenship=["United States"],
        has_date_of_birth="1990-01-01",
        has_date_of_death=None,
        has_name=["Jamie Taxpayer"],
        has_place_of_birth="Boston",
        has_residence=["101 Main St, New York, NY 10001"],
        has_tax_id=["123-45-6789"],
        is_employed_by=[employer],
    )
    w2_form = schema_models.W2Form(
        has_allocated_tips="0.00",
        has_box12_codes=["D"],
        has_dependent_care_benefits="0.00",
        has_federal_income_tax_withheld="2000.00",
        has_medicare_tax_withheld="725.00",
        has_medicare_wages_and_tips="50000.00",
        has_nonqualified_plans="0.00",
        has_other_info=["State wages included"],
        has_report_date_time=[datetime(2026, 1, 31, 12, 0, tzinfo=timezone.utc)],
        has_retirement_plan="true",
        has_social_security_tax_withheld="3100.00",
        has_social_security_tips="0.00",
        has_social_security_wages="50000.00",
        has_tax_year="2025",
        has_third_party_sick_pay="0.00",
        has_wages_tips_other_comp="50000.00",
        is_provided_by=["Acme Corp Payroll"],
        is_statutory_employee="false",
        is_submitted_by=["Acme Corp Payroll"],
        has_report_status=schema_models.Reportstatus.SUBMITTED,
        issued_by=employer,
        issued_to=person,
    )
    crypto_asset = schema_models.CryptoAsset(
        has_token_symbol="BTC",
        is_traded_on=[exchange],
    )
    individual_return = schema_models.IndividualTaxReturn(
        has_report_date_time=[datetime(2026, 2, 1, 10, 15, tzinfo=timezone.utc)],
        is_provided_by=["Tax Software Inc"],
        is_submitted_by=["Jamie Taxpayer"],
        is_submitted_to=schema_models.TaxAuthority.INTERNAL_REVENUE_SERVICE,
        has_taxable_income=money,
        has_report_status=schema_models.Reportstatus.SUBMITTED,
        has_agi=money,
        has_total_tax=money,
        has_total_payments=money,
        has_refund_amount=money,
        has_amount_owed=money,
        has_line1a_wages=money,
        has_line2b_taxable_interest=money,
        has_line3b_ordinary_dividends=money,
        has_line6b_taxable_social_security=money,
        has_line12_standard_deduction=money,
        has_line16_tax_value=money,
        has_line19_child_tax_credit=money,
        has_line24_total_tax=money,
        has_line33_total_payments=money,
    )
    form_1040 = schema_models.Form1040_2025(
        has_report_date_time=[datetime(2026, 2, 1, 10, 20, tzinfo=timezone.utc)],
        is_provided_by=["Tax Software Inc"],
        is_submitted_by=["Jamie Taxpayer"],
        is_submitted_to=schema_models.TaxAuthority.INTERNAL_REVENUE_SERVICE,
        has_taxable_income=money,
        has_report_status=schema_models.Reportstatus.SUBMITTED,
        has_agi=money,
        has_total_tax=money,
        has_total_payments=money,
        has_refund_amount=money,
        has_amount_owed=money,
        has_line1a_wages=money,
        has_line2b_taxable_interest=money,
        has_line3b_ordinary_dividends=money,
        has_line6b_taxable_social_security=money,
        has_line12_standard_deduction=money,
        has_line16_tax_value=money,
        has_line19_child_tax_credit=money,
        has_line24_total_tax=money,
        has_line33_total_payments=money,
    )
    model_instances = {
        "Organization": organization,
        "Exchange": exchange,
        "W2Form": w2_form,
        "CryptoAsset": crypto_asset,
        "Person": person,
        "PhysicalAddress": schema_models.PhysicalAddress(),
        "Form1120USCorporationIncomeTaxReturn": schema_models.Form1120USCorporationIncomeTaxReturn(),
        "IndividualTaxReturn": individual_return,
        "MonetaryAmount": money,
        "Form1040_2025": form_1040,
        "TaxPayer": taxpayer,
        "Employer": employer,
    }

    created_labels: Set[str] = set()
    model_node_ids: Dict[str, str] = {}
    enum_node_ids: Dict[Tuple[str, str], str] = {}

    with driver.session(database=db_name) as session:
        # Clean previous data for idempotent reruns.
        session.run("MATCH (n {testRun: $run}) DETACH DELETE n", run=test_run)

        # Create sample enum/named individual nodes for enum classes.
        for enum_class, members in sorted(enum_members_by_class.items()):
            for member_label in sorted(members):
                node_id = str(uuid.uuid4())
                session.run(
                    f"""
                    CREATE (n:`{enum_class}`:owl__NamedIndividual {{
                      id: $id,
                      rdfs__label: $label,
                      testRun: $run,
                      sampleTag: 'schema_workflow',
                      sampleCreatedAt: $ts
                    }})
                    """,
                    id=node_id,
                    label=member_label,
                    run=test_run,
                    ts=datetime.now(timezone.utc).isoformat(),
                )
                enum_node_ids[(enum_class, member_label)] = node_id
                created_labels.add(enum_class)

        # Create one sample node for each model class, applying multi-labels for subclasses.
        for label, instance in model_instances.items():
            node_id = str(uuid.uuid4())
            dumped = instance.model_dump(by_alias=True, exclude_none=True, mode="json")
            props = _to_neo4j_props(dumped)
            props.update({"testRun": test_run, "sampleTag": "schema_workflow"})
            label_expr = _label_chain(label, subclass_map)  # e.g. `TaxPayer`:`Person`
            session.run(
                f"CREATE (n:{label_expr} {{id: $id}}) SET n += $props",
                id=node_id,
                props=props,
            )
            model_node_ids[label] = node_id
            created_labels.add(label)

        # Build a core set of relationships for validation and topology smoke-testing.
        session.run(
            """
            MATCH (m:MonetaryAmount {id: $money_id, testRun: $run})
            MATCH (c:Currency {id: $currency_id, testRun: $run})
            CREATE (m)-[:isDenominatedIn]->(c)
            """,
            money_id=model_node_ids["MonetaryAmount"],
            currency_id=enum_node_ids[("Currency", schema_models.Currency.US_DOLLAR.value)],
            run=test_run,
        )
        session.run(
            """
            MATCH (w:W2Form {id: $w2_id, testRun: $run})
            MATCH (e:Employer {id: $emp_id, testRun: $run})
            MATCH (o:Organization {id: $org_id, testRun: $run})
            MATCH (p:Person {id: $person_id, testRun: $run})
            MATCH (s:Reportstatus {rdfs__label: $status, testRun: $run})
            CREATE (w)-[:issuedBy]->(e)
            CREATE (w)-[:issuedBy]->(o)
            CREATE (w)-[:issuedTo]->(p)
            CREATE (w)-[:hasReportStatus]->(s)
            """,
            w2_id=model_node_ids["W2Form"],
            emp_id=model_node_ids["Employer"],
            org_id=model_node_ids["Organization"],
            person_id=model_node_ids["Person"],
            status=schema_models.Reportstatus.SUBMITTED.value,
            run=test_run,
        )
        session.run(
            """
            MATCH (p:Person {id: $person_id, testRun: $run})
            MATCH (t:TaxPayer {id: $taxpayer_id, testRun: $run})
            MATCH (e:Employer {id: $emp_id, testRun: $run})
            MATCH (a:PhysicalAddress {id: $address_id, testRun: $run})
            CREATE (p)-[:isEmployedBy]->(e)
            CREATE (t)-[:isEmployedBy]->(e)
            CREATE (p)-[:hasResidence]->(a)
            CREATE (t)-[:hasResidence]->(a)
            """,
            person_id=model_node_ids["Person"],
            taxpayer_id=model_node_ids["TaxPayer"],
            emp_id=model_node_ids["Employer"],
            address_id=model_node_ids["PhysicalAddress"],
            run=test_run,
        )
        session.run(
            """
            MATCH (c:CryptoAsset {id: $crypto_id, testRun: $run})
            MATCH (x:Exchange {id: $exchange_id, testRun: $run})
            CREATE (c)-[:isTradedOn]->(x)
            """,
            crypto_id=model_node_ids["CryptoAsset"],
            exchange_id=model_node_ids["Exchange"],
            run=test_run,
        )
        session.run(
            """
            MATCH (r1:IndividualTaxReturn {id: $itr_id, testRun: $run})
            MATCH (r2:Form1040_2025 {id: $f1040_id, testRun: $run})
            MATCH (m:MonetaryAmount {id: $money_id, testRun: $run})
            MATCH (t:TaxPayer {id: $taxpayer_id, testRun: $run})
            MATCH (ta:TaxAuthority {rdfs__label: $irs_label, testRun: $run})
            MATCH (status:Reportstatus {rdfs__label: $status_label, testRun: $run})
            CREATE (r1)-[:isSubmittedTo]->(ta)
            CREATE (r2)-[:isSubmittedTo]->(ta)
            CREATE (r1)-[:isSubmittedBy]->(t)
            CREATE (r2)-[:isSubmittedBy]->(t)
            CREATE (r1)-[:hasReportStatus]->(status)
            CREATE (r2)-[:hasReportStatus]->(status)
            CREATE (r1)-[:hasTaxableIncome]->(m)
            CREATE (r2)-[:hasTaxableIncome]->(m)
            """,
            itr_id=model_node_ids["IndividualTaxReturn"],
            f1040_id=model_node_ids["Form1040_2025"],
            money_id=model_node_ids["MonetaryAmount"],
            taxpayer_id=model_node_ids["TaxPayer"],
            irs_label=schema_models.TaxAuthority.INTERNAL_REVENUE_SERVICE.value,
            status_label=schema_models.Reportstatus.SUBMITTED.value,
            run=test_run,
        )

    return created_labels


def validate_sample_data(
    driver,
    db_name: str,
    test_run: str,
    mandatory_props_by_class: Dict[str, Set[str]],
    enum_members_by_class: Dict[str, Set[str]],
    topology_map: Dict[str, Dict[str, Set[str]]],
    expected_labels: Set[str],
) -> List[str]:
    """Validate loaded sample data against schema description artifacts."""

    target_classes = sorted(expected_labels)

    with driver.session(database=db_name) as session:
        rows = session.run(
            """
            MATCH (n {testRun: $run})
            RETURN labels(n) AS labels, properties(n) AS props
            """,
            run=test_run,
        ).data()

    props_by_class: Dict[str, Dict[str, object]] = {}
    present_labels: Set[str] = set()
    for row in rows:
        labels = row.get("labels") or []
        props = row.get("props") or {}
        for lbl in labels:
            if lbl in target_classes:
                props_by_class[lbl] = props
                present_labels.add(lbl)

    missing_labels = [lbl for lbl in target_classes if lbl not in present_labels]
    if missing_labels:
        raise AssertionError(f"Missing sample nodes for labels: {missing_labels}")

    # Validate mandatory properties for our sample classes.
    for cls in target_classes:
        required = mandatory_props_by_class.get(cls, set())
        if not required:
            continue
        if cls not in props_by_class:
            raise AssertionError(f"Missing sample node for class {cls}")
        node_props = props_by_class[cls]
        missing = [p for p in required if p not in node_props or node_props[p] in (None, "", [])]
        if missing:
            raise AssertionError(f"Class {cls} missing mandatory properties: {missing}")

    # Validate mandatory enum relationships for MonetaryAmount based on topology + enum members.
    money_rels = topology_map.get("MonetaryAmount", {})
    enum_targets = []
    for rel_type, targets in money_rels.items():
        for tgt in targets:
            if tgt in enum_members_by_class:
                enum_targets.append((rel_type, tgt))

    with driver.session(database=db_name) as session:
        for rel_type, enum_cls in enum_targets:
            rows = session.run(
                f"""
                MATCH (m:MonetaryAmount {{testRun: $run}})-[:`{rel_type}`]->(e:`{enum_cls}`)
                RETURN e.rdfs__label AS label
                """,
                run=test_run,
            ).data()
            if not rows:
                raise AssertionError(
                    f"Missing mandatory enum relationship MonetaryAmount-[:{rel_type}]->{enum_cls}"
                )
            allowed = enum_members_by_class.get(enum_cls, set())
            for row in rows:
                label = row.get("label")
                if label not in allowed:
                    raise AssertionError(
                        f"Enum value '{label}' is not allowed for {enum_cls}; allowed={sorted(allowed)}"
                    )

    # Validate the workflow scenario:
    # taxpayer/person receives W-2 from organization and submits 1040.
    with driver.session(database=db_name) as session:
        scenario_checks = [
            (
                """
                MATCH (w:W2Form {testRun: $run})-[:issuedTo]->(p:Person {testRun: $run})
                RETURN count(*) AS c
                """,
                "Missing W2Form -> issuedTo -> Person relationship",
            ),
            (
                """
                MATCH (w:W2Form {testRun: $run})-[:issuedBy]->(o:Organization {testRun: $run})
                RETURN count(*) AS c
                """,
                "Missing W2Form -> issuedBy -> Organization relationship",
            ),
            (
                """
                MATCH (f:Form1040_2025 {testRun: $run})-[:isSubmittedBy]->(t:TaxPayer {testRun: $run})
                RETURN count(*) AS c
                """,
                "Missing Form1040_2025 -> isSubmittedBy -> TaxPayer relationship",
            ),
            (
                """
                MATCH (p:Person {testRun: $run})-[:hasResidence]->(:PhysicalAddress {testRun: $run})
                RETURN count(*) AS c
                """,
                "Missing Person -> hasResidence -> PhysicalAddress relationship",
            ),
        ]
        for query, message in scenario_checks:
            count = session.run(query, run=test_run).single()["c"]
            if count < 1:
                raise AssertionError(message)
    return target_classes


def main() -> int:
    parser = argparse.ArgumentParser(description="Run staging schema workflow test")
    parser.add_argument(
        "--test-db",
        default=os.getenv("NEO4J_TEST_DB_NAME", "test"),
        help="Neo4j database name for test execution",
    )
    parser.add_argument(
        "--constraints",
        default="staging/stagingdb_constraints_mcp.cypher",
        help="Path to generated constraints Cypher file",
    )
    parser.add_argument(
        "--schema-description",
        default="staging/schema_description.md",
        help="Path to generated schema description markdown",
    )
    parser.add_argument(
        "--test-run",
        default=f"schema_workflow_{uuid.uuid4().hex[:8]}",
        help="Unique test run identifier",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        default=False,
        help="Keep test data in the database after the test (useful for manual inspection). Default: delete after test.",
    )
    args = parser.parse_args()

    cfg = get_neo4j_config()
    constraints_path = Path(args.constraints)
    schema_desc_path = Path(args.schema_description)
    if not constraints_path.exists():
        raise FileNotFoundError(f"Constraints file not found: {constraints_path}")
    if not schema_desc_path.exists():
        raise FileNotFoundError(f"Schema description file not found: {schema_desc_path}")

    mandatory_props_by_class, enum_members_by_class, topology_map = parse_schema_description(schema_desc_path)

    data_model_path = Path("staging/full_schema_data_model.json")
    subclass_map = build_subclass_map(data_model_path)
    if subclass_map:
        print(f"Subclass map loaded: {subclass_map}")

    driver = GraphDatabase.driver(cfg.uri, auth=(cfg.username, cfg.password))
    try:
        ensure_test_database(driver, args.test_db)
        active_db = resolve_database_with_fallback(driver, args.test_db)
        applied = apply_constraints(driver, active_db, constraints_path)
        created_labels = load_sample_data(
            driver, active_db, args.test_run, enum_members_by_class, subclass_map
        )
        validated_labels = validate_sample_data(
            driver,
            active_db,
            args.test_run,
            mandatory_props_by_class,
            enum_members_by_class,
            topology_map,
            created_labels,
        )

        print("Schema workflow test passed")
        print(f"Database: {active_db}")
        print(f"Test run: {args.test_run}")
        print(f"Constraints applied: {applied}")
        print(f"Sample labels validated ({len(validated_labels)}): {', '.join(validated_labels)}")
        if args.keep_data:
            print(f"Test data retained (sampleTag='schema_workflow', testRun='{args.test_run}')")
            print("  To inspect:  MATCH (n {sampleTag: 'schema_workflow'}) RETURN labels(n), n")
            print("  To clean up: MATCH (n {sampleTag: 'schema_workflow'}) DETACH DELETE n")
        else:
            with driver.session(database=active_db) as session:
                session.run("MATCH (n {sampleTag: 'schema_workflow'}) DETACH DELETE n")
            print("Test data cleaned up.")
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Schema workflow test failed: {exc}", file=sys.stderr)
        raise
