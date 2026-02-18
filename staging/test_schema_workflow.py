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
import os
import re
import sys
import uuid
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


def load_sample_data(driver, db_name: str, test_run: str) -> Dict[str, str]:
    """Load sample entities using generated schema_models classes."""

    employer = schema_models.Employer(
        has_address=["1 Main St, New York, NY 10001"],
        has_ein="12-3456789",
        has_employer_name="Acme Corp",
        has_phone_number=["+1-212-555-0101"],
    )
    person = schema_models.Person(
        has_date_of_birth="1988-06-15",
        has_place_of_birth="New York",
        has_name=["Alex Doe"],
        has_tax_id=["999-88-7777"],
    )
    money = schema_models.MonetaryAmount(
        is_denominated_in=schema_models.Currency.US_DOLLAR,
    )

    employer_props = employer.model_dump(by_alias=True, exclude_none=True, mode="json")
    person_props = person.model_dump(by_alias=True, exclude_none=True, mode="json")

    # MonetaryAmount has only relationship-based enum field in this model.
    money_props = {
        "testRun": test_run,
        "sampleTag": "schema_workflow",
    }
    employer_props.update({"testRun": test_run, "sampleTag": "schema_workflow"})
    person_props.update({"testRun": test_run, "sampleTag": "schema_workflow"})

    ids = {
        "employer": str(uuid.uuid4()),
        "person": str(uuid.uuid4()),
        "money": str(uuid.uuid4()),
        "currency_member": str(uuid.uuid4()),
    }

    with driver.session(database=db_name) as session:
        # Clean previous data for idempotent reruns.
        session.run(
            "MATCH (n {testRun: $run}) DETACH DELETE n",
            run=test_run,
        )

        session.run(
            "CREATE (n:Employer {id: $id}) SET n += $props",
            id=ids["employer"],
            props=employer_props,
        )
        session.run(
            "CREATE (n:Person {id: $id}) SET n += $props",
            id=ids["person"],
            props=person_props,
        )
        session.run(
            "CREATE (n:MonetaryAmount {id: $id}) SET n += $props",
            id=ids["money"],
            props=money_props,
        )

        # Enum member node for Currency (as a test data instance-like node).
        session.run(
            """
            CREATE (c:Currency:owl__NamedIndividual {
              id: $id,
              rdfs__label: $label,
              testRun: $run,
              sampleTag: 'schema_workflow'
            })
            """,
            id=ids["currency_member"],
            label=schema_models.Currency.US_DOLLAR.value,
            run=test_run,
        )

        session.run(
            """
            MATCH (m:MonetaryAmount {id: $mid, testRun: $run})
            MATCH (c:Currency {id: $cid, testRun: $run})
            CREATE (m)-[:isDenominatedIn]->(c)
            """,
            mid=ids["money"],
            cid=ids["currency_member"],
            run=test_run,
        )

    return ids


def validate_sample_data(
    driver,
    db_name: str,
    test_run: str,
    mandatory_props_by_class: Dict[str, Set[str]],
    enum_members_by_class: Dict[str, Set[str]],
    topology_map: Dict[str, Dict[str, Set[str]]],
) -> None:
    """Validate loaded sample data against schema description artifacts."""

    target_classes = ["Employer", "Person", "MonetaryAmount"]

    with driver.session(database=db_name) as session:
        rows = session.run(
            """
            MATCH (n {testRun: $run})
            RETURN labels(n) AS labels, properties(n) AS props
            """,
            run=test_run,
        ).data()

    props_by_class: Dict[str, Dict[str, object]] = {}
    for row in rows:
        labels = row.get("labels") or []
        props = row.get("props") or {}
        for lbl in labels:
            if lbl in target_classes:
                props_by_class[lbl] = props

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
    args = parser.parse_args()

    cfg = get_neo4j_config()
    constraints_path = Path(args.constraints)
    schema_desc_path = Path(args.schema_description)
    if not constraints_path.exists():
        raise FileNotFoundError(f"Constraints file not found: {constraints_path}")
    if not schema_desc_path.exists():
        raise FileNotFoundError(f"Schema description file not found: {schema_desc_path}")

    mandatory_props_by_class, enum_members_by_class, topology_map = parse_schema_description(schema_desc_path)

    driver = GraphDatabase.driver(cfg.uri, auth=(cfg.username, cfg.password))
    try:
        ensure_test_database(driver, args.test_db)
        active_db = resolve_database_with_fallback(driver, args.test_db)
        applied = apply_constraints(driver, active_db, constraints_path)
        load_sample_data(driver, active_db, args.test_run)
        validate_sample_data(
            driver,
            active_db,
            args.test_run,
            mandatory_props_by_class,
            enum_members_by_class,
            topology_map,
        )

        print("Schema workflow test passed")
        print(f"Database: {active_db}")
        print(f"Test run: {args.test_run}")
        print(f"Constraints applied: {applied}")
        print("Sample classes validated: Employer, Person, MonetaryAmount")
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Schema workflow test failed: {exc}", file=sys.stderr)
        raise
