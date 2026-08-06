#!/usr/bin/env python3
"""End-to-end schema workflow test for the packaged entitlement schema.

Workflow:
1. Optionally create/use a test Neo4j database.
2. Apply generated constraints from the packaged entitlement artifacts.
3. Load sample data using the packaged Pydantic models.
4. Validate inserted data against the packaged schema description.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

from neo4j import GraphDatabase

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from onto2ai_entitlement.staging import pydantic_schema_model

DEFAULT_TEST_DB_NAME = f"entitlement-smoke-{uuid.uuid4().hex[:8]}"
THIS_DIR = Path(__file__).resolve().parent
ONTOLOGY_RELATIONSHIPS = {"rdf__type", "rdfs__subClassOf"}
DATABASE_NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9.-]*$")


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
    """Read full_schema_model.json and return {child_pascal -> parent_pascal} map."""
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
    """Parse neo4j_query_context.md.

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


def prepare_test_database(driver, db_name: str, reset_database: bool) -> None:
    """Create the smoke-test database, optionally resetting it first."""
    with driver.session(database="system") as session:
        if reset_database:
            session.run(f"DROP DATABASE `{db_name}` IF EXISTS").consume()
        session.run(f"CREATE DATABASE `{db_name}` IF NOT EXISTS").consume()
        for _ in range(30):
            row = session.run(
                "SHOW DATABASES YIELD name, currentStatus WHERE name = $name RETURN currentStatus AS status",
                name=db_name,
            ).single()
            if row and str(row["status"]).lower() == "online":
                break
            time.sleep(0.5)

    with driver.session(database=db_name) as session:
        session.run("RETURN 1 AS ok").consume()


def drop_test_database(driver, db_name: str) -> None:
    with driver.session(database="system") as session:
        session.run(f"DROP DATABASE `{db_name}` IF EXISTS").consume()


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


def _is_entitlement_model() -> bool:
    return all(
        hasattr(pydantic_schema_model, name)
        for name in (
            "User",
            "PolicyGroup",
            "Policy",
            "RowFilterRule",
            "ColumnMaskRule",
            "RelationalDatabase",
            "JdbcConnectionProfile",
        )
    )


def _require_entitlement_model() -> None:
    if not _is_entitlement_model():
        raise RuntimeError(
            "Packaged pydantic_schema_model is not an entitlement model; "
            "regenerate onto2ai_entitlement/staging artifacts from the entitlement ontology."
        )


def _add_label_with_ancestors(labels: Set[str], label: str, subclass_map: Dict[str, str]) -> None:
    cur = label
    labels.add(cur)
    while cur in subclass_map:
        cur = subclass_map[cur]
        labels.add(cur)


def load_sample_data(
    driver,
    db_name: str,
    test_run: str,
    enum_members_by_class: Dict[str, Set[str]],
    subclass_map: Dict[str, str],
) -> Set[str]:
    """Load sample entities for each entitlement class."""
    _require_entitlement_model()

    relational_database = pydantic_schema_model.RelationalDatabase(
        relationalDatabaseId=f"db-{test_run}",
        databaseName="warehouse",
        databaseVendor="postgresql",
        databaseVersion="16",
        databaseEdition="community",
        hostName="db.internal.local",
        portNumber=5432,
    )
    jdbc_profile = pydantic_schema_model.JdbcConnectionProfile(
        jdbcConnectionProfileId=f"jdbc-{test_run}",
        jdbcUrl="jdbc:postgresql://db.internal.local:5432/warehouse",
        jdbcDriver="org.postgresql.Driver",
        jdbcUserName="entitlement_app",
        connectionTimeoutSeconds=30,
        sslMode="require",
        connectsTo=relational_database,
    )
    schema = pydantic_schema_model.Schema(
        schemaId=f"schema-{test_run}",
        schemaName="analytics",
        schemaOwner="data_platform",
        schemaType="application",
        schemaDescription="Analytics schema protected by entitlement rules.",
        isDefaultSchema=True,
        belongsToDatabase=relational_database,
    )
    table = pydantic_schema_model.Table(
        tableId=f"table-{test_run}",
        tableName="customer_account",
        tableType="base table",
        tableOwner="data_platform",
        tableDescription="Customer account table.",
        rowCountEstimate=125000,
        isTemporaryTable=False,
        belongsToSchema=schema,
    )
    column = pydantic_schema_model.Column(
        columnId=f"column-{test_run}",
        columnName="region_code",
        columnDataType="varchar",
        columnLength=20,
        isNullable=False,
        ordinalPosition=3,
        belongsToTable=table,
        hasSensitivityClassification=pydantic_schema_model.SensitivityClassification.CONFIDENTIAL,
    )
    row_filter_rule = pydantic_schema_model.RowFilterRule(
        rowFilterRuleId=f"rfr-{test_run}",
        hasFilterAction=pydantic_schema_model.FilterAction.ALLOW,
        hasMatchMode=pydantic_schema_model.MatchMode.MULTIPLE_VALUES,
        hasComparisonOperator=pydantic_schema_model.ComparisonOperator.IN_LIST,
        hasValueSourceType=pydantic_schema_model.ValueSourceType.SUBJECT_ATTRIBUTE,
        valueSourceExpression="user.allowed_regions",
        hasDenyBehavior=pydantic_schema_model.DenyBehavior.RETURN_NO_ROWS,
        llmRewriteInstruction="Rewrite the WHERE clause to restrict region_code to the allowed values.",
        rewriteTemplate="WHERE region_code IN ({values})",
        ruleExpression="region_code IN allowed_regions",
        hasPriority=pydantic_schema_model.RulePriority.HIGH_PRIORITY,
        targetsFilteredColumn=[column],
    )
    column_mask_rule = pydantic_schema_model.ColumnMaskRule(
        columnMaskRuleId=f"cmr-{test_run}",
        hasMaskAction=pydantic_schema_model.MaskAction.REDACT,
        hasMaskingMethod=pydantic_schema_model.MaskingMethod.STATIC_SUBSTITUTION,
        maskValueExpression="'***'",
        hasFallbackBehavior=pydantic_schema_model.FallbackBehavior.BLOCK_QUERY,
        llmRewriteInstruction="Rewrite the SELECT projection to mask region_code when access is denied.",
        rewriteTemplate="CASE WHEN {condition} THEN region_code ELSE '***' END",
        ruleExpression="mask region_code when unauthorized",
        hasValueSourceType=pydantic_schema_model.ValueSourceType.SESSION_CONTEXT,
        valueSourceExpression="user.masking_scope",
        hasPriority=pydantic_schema_model.RulePriority.MEDIUM_PRIORITY,
        targetsMaskedColumn=[column],
    )
    policy = pydantic_schema_model.Policy(
        policyId=f"policy-{test_run}",
        policyName=["Regional access policy"],
        policyDescription=["Applies row filtering and masking to regional account data."],
    )
    policy_group = pydantic_schema_model.PolicyGroup(
        policyGroupId=f"pg-{test_run}",
        policyGroupName=["regional analysts"],
        includesPolicy=[policy],
    )
    user = pydantic_schema_model.User(
        userId=f"user-{test_run}",
        hasUserType=pydantic_schema_model.UserType.HUMAN_USER,
        isMemberOf=[policy_group],
    )

    model_instances = {
        "RelationalDatabase": relational_database,
        "JdbcConnectionProfile": jdbc_profile,
        "Schema": schema,
        "Table": table,
        "Column": column,
        "RowFilterRule": row_filter_rule,
        "ColumnMaskRule": column_mask_rule,
        "Policy": policy,
        "PolicyGroup": policy_group,
        "User": user,
    }

    created_labels: Set[str] = set()
    model_node_ids: Dict[str, str] = {}
    enum_node_ids: Dict[Tuple[str, str], str] = {}

    with driver.session(database=db_name) as session:
        # Clean previous data for idempotent reruns.
        session.run("MATCH (n {testRun: $run}) DETACH DELETE n", run=test_run)

        # Create sample enum/reference nodes for enum classes.
        for enum_class, members in sorted(enum_members_by_class.items()):
            for member_label in sorted(members):
                node_id = str(uuid.uuid4())
                session.run(
                    f"""
                    CREATE (n:`{enum_class}` {{
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
            _add_label_with_ancestors(created_labels, label, subclass_map)

        session.run(
            """
            MATCH (j:JdbcConnectionProfile {id: $jdbc_id, testRun: $run})
            MATCH (d:RelationalDatabase {id: $db_id, testRun: $run})
            MATCH (s:Schema {id: $schema_id, testRun: $run})
            MATCH (t:Table {id: $table_id, testRun: $run})
            MATCH (c:Column {id: $column_id, testRun: $run})
            MATCH (rf:RowFilterRule {id: $row_rule_id, testRun: $run})
            MATCH (cm:ColumnMaskRule {id: $mask_rule_id, testRun: $run})
            MATCH (p:Policy {id: $policy_id, testRun: $run})
            MATCH (pg:PolicyGroup {id: $policy_group_id, testRun: $run})
            MATCH (u:User {id: $user_id, testRun: $run})
            MATCH (ut:UserType {rdfs__label: $user_type, testRun: $run})
            MATCH (classification:SensitivityClassification {rdfs__label: $sensitivity_classification, testRun: $run})
            MATCH (high:RulePriority {rdfs__label: $high_priority, testRun: $run})
            MATCH (medium:RulePriority {rdfs__label: $medium_priority, testRun: $run})
            MATCH (filter_action:FilterAction {rdfs__label: $filter_action, testRun: $run})
            MATCH (match_mode:MatchMode {rdfs__label: $match_mode, testRun: $run})
            MATCH (comparison_operator:ComparisonOperator {rdfs__label: $comparison_operator, testRun: $run})
            MATCH (deny_behavior:DenyBehavior {rdfs__label: $deny_behavior, testRun: $run})
            MATCH (rf_value_source_type:ValueSourceType {rdfs__label: $rf_value_source_type, testRun: $run})
            MATCH (mask_action:MaskAction {rdfs__label: $mask_action, testRun: $run})
            MATCH (masking_method:MaskingMethod {rdfs__label: $masking_method, testRun: $run})
            MATCH (fallback_behavior:FallbackBehavior {rdfs__label: $fallback_behavior, testRun: $run})
            MATCH (cm_value_source_type:ValueSourceType {rdfs__label: $cm_value_source_type, testRun: $run})
            CREATE (j)-[:connectsTo]->(d)
            CREATE (s)-[:belongsToDatabase]->(d)
            CREATE (t)-[:belongsToSchema]->(s)
            CREATE (c)-[:belongsToTable]->(t)
            CREATE (c)-[:hasSensitivityClassification]->(classification)
            CREATE (rf)-[:targetsFilteredColumn]->(c)
            CREATE (rf)-[:hasPriority]->(high)
            CREATE (rf)-[:hasFilterAction]->(filter_action)
            CREATE (rf)-[:hasMatchMode]->(match_mode)
            CREATE (rf)-[:hasComparisonOperator]->(comparison_operator)
            CREATE (rf)-[:hasDenyBehavior]->(deny_behavior)
            CREATE (rf)-[:hasValueSourceType]->(rf_value_source_type)
            CREATE (cm)-[:targetsMaskedColumn]->(c)
            CREATE (cm)-[:hasPriority]->(medium)
            CREATE (cm)-[:hasMaskAction]->(mask_action)
            CREATE (cm)-[:hasMaskingMethod]->(masking_method)
            CREATE (cm)-[:hasFallbackBehavior]->(fallback_behavior)
            CREATE (cm)-[:hasValueSourceType]->(cm_value_source_type)
            CREATE (p)-[:hasRowFilterRule]->(rf)
            CREATE (p)-[:hasColumnMaskRule]->(cm)
            CREATE (pg)-[:includesPolicy]->(p)
            CREATE (u)-[:isMemberOf]->(pg)
            CREATE (u)-[:hasUserType]->(ut)
            """,
            jdbc_id=model_node_ids["JdbcConnectionProfile"],
            db_id=model_node_ids["RelationalDatabase"],
            schema_id=model_node_ids["Schema"],
            table_id=model_node_ids["Table"],
            column_id=model_node_ids["Column"],
            row_rule_id=model_node_ids["RowFilterRule"],
            mask_rule_id=model_node_ids["ColumnMaskRule"],
            policy_id=model_node_ids["Policy"],
            policy_group_id=model_node_ids["PolicyGroup"],
            user_id=model_node_ids["User"],
            user_type=pydantic_schema_model.UserType.HUMAN_USER.value,
            sensitivity_classification=pydantic_schema_model.SensitivityClassification.CONFIDENTIAL.value,
            high_priority=pydantic_schema_model.RulePriority.HIGH_PRIORITY.value,
            medium_priority=pydantic_schema_model.RulePriority.MEDIUM_PRIORITY.value,
            filter_action=pydantic_schema_model.FilterAction.ALLOW.value,
            match_mode=pydantic_schema_model.MatchMode.MULTIPLE_VALUES.value,
            comparison_operator=pydantic_schema_model.ComparisonOperator.IN_LIST.value,
            deny_behavior=pydantic_schema_model.DenyBehavior.RETURN_NO_ROWS.value,
            rf_value_source_type=pydantic_schema_model.ValueSourceType.SUBJECT_ATTRIBUTE.value,
            mask_action=pydantic_schema_model.MaskAction.REDACT.value,
            masking_method=pydantic_schema_model.MaskingMethod.STATIC_SUBSTITUTION.value,
            fallback_behavior=pydantic_schema_model.FallbackBehavior.BLOCK_QUERY.value,
            cm_value_source_type=pydantic_schema_model.ValueSourceType.SESSION_CONTEXT.value,
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

    with driver.session(database=db_name) as session:
        ontology_node_count = session.run(
            """
            MATCH (n)
            WHERE any(label IN labels(n) WHERE label IN ['owl__Class', 'owl__Ontology', 'owl__Restriction'])
            RETURN count(n) AS count
            """
        ).single()["count"]
        if ontology_node_count:
            raise AssertionError(f"Dataset database contains {ontology_node_count} ontology schema nodes")

        ontology_relationship_count = session.run(
            """
            MATCH ()-[r]->()
            WHERE type(r) IN ['rdf__type', 'rdfs__subClassOf']
            RETURN count(r) AS count
            """
        ).single()["count"]
        if ontology_relationship_count:
            raise AssertionError(
                f"Dataset database contains {ontology_relationship_count} ontology-only relationships"
            )

        for src, relationships in sorted(topology_map.items()):
            if src not in target_classes:
                continue
            for rel_type, targets in sorted(relationships.items()):
                if rel_type in ONTOLOGY_RELATIONSHIPS:
                    continue
                for tgt in sorted(targets):
                    if tgt not in target_classes:
                        continue
                    count = session.run(
                        f"""
                        MATCH (:`{src}` {{testRun: $run}})-[:`{rel_type}`]->(:`{tgt}` {{testRun: $run}})
                        RETURN count(*) AS c
                        """,
                        run=test_run,
                    ).single()["c"]
                    if count < 1:
                        raise AssertionError(f"Missing {src} -[:{rel_type}]-> {tgt} relationship")

                    if tgt in enum_members_by_class:
                        rows = session.run(
                            f"""
                            MATCH (:`{src}` {{testRun: $run}})-[:`{rel_type}`]->(e:`{tgt}` {{testRun: $run}})
                            RETURN e.rdfs__label AS label
                            """,
                            run=test_run,
                        ).data()
                        allowed = enum_members_by_class.get(tgt, set())
                        for row in rows:
                            label = row.get("label")
                            if label not in allowed:
                                raise AssertionError(
                                    f"Enum value '{label}' is not allowed for {tgt}; allowed={sorted(allowed)}"
                                )
    return target_classes


def main() -> int:
    parser = argparse.ArgumentParser(description="Run staging schema workflow test")
    parser.add_argument(
        "--constraints",
        default=str(THIS_DIR / "neo4j_constraint.cypher"),
        help="Path to generated constraints Cypher file",
    )
    parser.add_argument(
        "--schema-description",
        default=str(THIS_DIR / "neo4j_query_context.md"),
        help="Path to generated schema description markdown",
    )
    parser.add_argument(
        "--test-run",
        default=f"schema_workflow_{uuid.uuid4().hex[:8]}",
        help="Unique test run identifier",
    )
    parser.add_argument(
        "--database",
        default=DEFAULT_TEST_DB_NAME,
        help=(
            "Neo4j database to use. Defaults to a generated entitlement smoke-test "
            "database so existing testdb content is not overwritten."
        ),
    )
    parser.add_argument(
        "--reset-database",
        action="store_true",
        help="Drop and recreate the selected database before the smoke test.",
    )
    parser.add_argument(
        "--keep-data",
        action="store_true",
        default=True,
        help="Keep test data in the database after the test for manual inspection. Default: keep data.",
    )
    parser.add_argument(
        "--cleanup",
        dest="keep_data",
        action="store_false",
        help="Delete smoke-test sample data after validation.",
    )
    parser.add_argument(
        "--drop-database-after",
        action="store_true",
        help="Drop the isolated smoke-test database after validation.",
    )
    args = parser.parse_args()
    if not DATABASE_NAME_PATTERN.fullmatch(args.database):
        raise ValueError(f"Invalid Neo4j database name: {args.database!r}")

    cfg = get_neo4j_config()
    constraints_path = Path(args.constraints)
    schema_desc_path = Path(args.schema_description)
    if not constraints_path.exists():
        raise FileNotFoundError(f"Constraints file not found: {constraints_path}")
    if not schema_desc_path.exists():
        raise FileNotFoundError(f"Schema description file not found: {schema_desc_path}")

    mandatory_props_by_class, enum_members_by_class, topology_map = parse_schema_description(schema_desc_path)

    data_model_path = THIS_DIR / "full_schema_model.json"
    subclass_map = build_subclass_map(data_model_path)
    if subclass_map:
        print(f"Subclass map loaded: {subclass_map}")

    driver = GraphDatabase.driver(cfg.uri, auth=(cfg.username, cfg.password))
    try:
        prepare_test_database(driver, args.database, args.reset_database)
        applied = apply_constraints(driver, args.database, constraints_path)
        created_labels = load_sample_data(
            driver, args.database, args.test_run, enum_members_by_class, subclass_map
        )
        validated_labels = validate_sample_data(
            driver,
            args.database,
            args.test_run,
            mandatory_props_by_class,
            enum_members_by_class,
            topology_map,
            created_labels,
        )

        print("Schema workflow test passed")
        print(f"Database: {args.database}")
        print(f"Test run: {args.test_run}")
        print(f"Constraints applied: {applied}")
        print(f"Sample labels validated ({len(validated_labels)}): {', '.join(validated_labels)}")
        if args.keep_data:
            reset_note = "recreated" if args.reset_database else "created or reused"
            print(f"Summary: database was {reset_note}, constraints were applied, sample data loaded, validated, and retained for review.")
            print(f"Test data retained (sampleTag='schema_workflow', testRun='{args.test_run}')")
            print(f"  To inspect:  MATCH (n {{testRun: '{args.test_run}'}}) RETURN labels(n), n")
            print(f"  To clean up: MATCH (n {{testRun: '{args.test_run}'}}) DETACH DELETE n")
        else:
            reset_note = "recreated" if args.reset_database else "created or reused"
            print(f"Summary: database was {reset_note}, constraints were applied, sample data loaded, validated, and cleaned up.")
            with driver.session(database=args.database) as session:
                session.run("MATCH (n {testRun: $run}) DETACH DELETE n", run=args.test_run)
            print("Test data cleaned up.")
        return 0
    finally:
        if args.drop_database_after:
            drop_test_database(driver, args.database)
        driver.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Schema workflow test failed: {exc}", file=sys.stderr)
        raise
