#!/usr/bin/env python3
"""Validate the executable Northstar custodian client demo case."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = CASE_DIR.parents[2]
CASE_PATH = CASE_DIR / "case-definition.json"
SCENARIO_PATH = CASE_DIR / "northstar-client-scenario.json"
DEFAULT_DATASET_DATABASE = "northstar-demo"
FORBIDDEN_DATASET_LABELS = {
    "owl__Class",
    "owl__Ontology",
    "owl__Restriction",
    "owl__NamedIndividual",
    "rdfs__Datatype",
}
FORBIDDEN_DATASET_RELATIONSHIPS = {"rdf__type", "rdfs__subClassOf"}
TOKEN_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
DATABASE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9.-]*$")


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_static_case(case: dict[str, Any], scenario: dict[str, Any]) -> dict[str, int]:
    require(case["institution"]["fictional"] is True, "The institution must be marked fictional")
    require(len(case["source_selections"]) == 5, "Expected five primary FIBO/Commons selections")
    require(len(case["target_model"]["classes"]) == 12, "Expected 12 target classes")

    nodes = scenario["nodes"]
    relationships = scenario["relationships"]
    node_ids = [node["id"] for node in nodes]
    require(len(node_ids) == len(set(node_ids)), "Scenario node IDs must be unique")

    known_ids = set(node_ids)
    for node in nodes:
        require(node["labels"], f"Node {node['id']} has no application label")
        for label in node["labels"]:
            require(label not in FORBIDDEN_DATASET_LABELS, f"Forbidden schema label in dataset: {label}")
            require(bool(TOKEN_PATTERN.fullmatch(label)), f"Unsafe application label: {label}")

    relationship_keys: set[tuple[str, str, str]] = set()
    for relationship in relationships:
        source = relationship["from"]
        target = relationship["to"]
        rel_type = relationship["type"]
        require(source in known_ids, f"Unknown relationship source: {source}")
        require(target in known_ids, f"Unknown relationship target: {target}")
        require(rel_type not in FORBIDDEN_DATASET_RELATIONSHIPS, f"Forbidden ontology relationship: {rel_type}")
        require(bool(TOKEN_PATTERN.fullmatch(rel_type)), f"Unsafe relationship type: {rel_type}")
        relationship_keys.add((source, rel_type, target))

    required_links = {
        ("client-hrfo", "hasCustodyAccount", "account-usd-4218"),
        ("account-usd-4218", "hasCustodyPortfolio", "portfolio-income"),
        ("portfolio-income", "hasCustodyHolding", "holding-treasury"),
        ("holding-treasury", "isHoldingOfFinancialInstrument", "instrument-demo-note"),
        ("account-usd-4218", "hasSettlementInstruction", "settlement-731"),
        ("settlement-731", "instructsCashMovement", "cash-movement-731"),
    }
    require(required_links <= relationship_keys, "Scenario is missing the required business trace")

    node_by_id = {node["id"]: node for node in nodes}
    require(
        node_by_id["client-status-active"]["properties"]["name"] == "client active",
        "Client must be active",
    )
    require(
        node_by_id["settlement-status-completed"]["properties"]["name"] == "settlement completed",
        "Settlement must be completed",
    )
    require(
        node_by_id["account-usd-4218"]["properties"]["hasCustodyAccountId"],
        "Custody account ID is mandatory",
    )
    require(
        node_by_id["cash-movement-731"]["properties"]["hasPaymentReference"],
        "Payment reference is mandatory",
    )
    return {"nodes": len(nodes), "relationships": len(relationships)}


def neo4j_driver():
    try:
        from neo4j import GraphDatabase
    except ImportError as exc:
        raise RuntimeError("Install project dependencies before running live checks") from exc

    uri = os.getenv("NEO4J_MODEL_DB_URL", "bolt://localhost:7687")
    username = os.getenv("NEO4J_MODEL_DB_USERNAME", "neo4j")
    password = os.getenv("NEO4J_MODEL_DB_PASSWORD")
    if not password:
        raise RuntimeError("NEO4J_MODEL_DB_PASSWORD is required for live checks")
    return GraphDatabase.driver(uri, auth=(username, password))


def validate_live_schema(driver, case: dict[str, Any], database: str) -> dict[str, int]:
    expected_classes = case["target_model"]["classes"]
    base_uri = case["target_model"]["base_uri"]
    source_uris = [selection["uri"] for selection in case["source_selections"]]
    with driver.session(database=database) as session:
        class_rows = session.run(
            """
            MATCH (c:owl__Class)
            WHERE c.rdfs__label IN $labels
            RETURN collect(DISTINCT c.rdfs__label) AS labels,
                   count(DISTINCT c) AS classCount,
                   count(DISTINCT CASE
                     WHEN c.skos__definition IS NOT NULL AND c.uri IS NOT NULL THEN c
                   END) AS documentedCount
            """,
            labels=expected_classes,
        ).single()
        require(class_rows is not None, "Unable to read target classes from stagingdb")
        require(class_rows["classCount"] == len(expected_classes), "Not all target classes exist in stagingdb")
        require(class_rows["documentedCount"] == len(expected_classes), "Target class documentation is incomplete")

        source_count = session.run(
            "MATCH (n) WHERE n.uri IN $uris RETURN count(DISTINCT n) AS count",
            uris=source_uris,
        ).single()["count"]
        require(source_count == len(source_uris), "One or more selected source URIs are missing")

        property_rows = session.run(
            """
            MATCH ()-[r]->()
            WHERE r.uri STARTS WITH $baseUri
            RETURN r.property_type AS kind,
                   count(r) AS count,
                   count(CASE WHEN r.uri IS NOT NULL
                                  AND r.skos__definition IS NOT NULL
                                  AND r.cardinality IS NOT NULL
                                  AND r.requirement IS NOT NULL
                                  AND r.materialized IS NOT NULL
                              THEN 1 END) AS completeCount
            """,
            baseUri=base_uri,
        ).data()
        counts = {row["kind"]: row["count"] for row in property_rows}
        require(
            counts.get("owl__DatatypeProperty") == case["target_model"]["expected_custom_datatype_properties"],
            "Unexpected custom datatype-property count",
        )
        require(
            counts.get("owl__ObjectProperty") == case["target_model"]["expected_custom_object_properties"],
            "Unexpected custom object-property count",
        )
        require(all(row["count"] == row["completeCount"] for row in property_rows), "Property metadata is incomplete")

        duplicate_count = session.run(
            """
            MATCH (n) WHERE n.uri IS NOT NULL
            WITH n.uri AS uri, count(*) AS copies
            WHERE copies > 1
            RETURN count(*) AS count
            """
        ).single()["count"]
        require(duplicate_count == 0, "Duplicate resource URIs found in stagingdb")

    return {
        "classes": len(expected_classes),
        "datatype_properties": counts["owl__DatatypeProperty"],
        "object_properties": counts["owl__ObjectProperty"],
    }


def ensure_database(driver, database: str, reset: bool) -> None:
    require(bool(DATABASE_PATTERN.fullmatch(database)), f"Unsafe database name: {database}")
    with driver.session(database="system") as session:
        if reset:
            session.run(f"DROP DATABASE `{database}` IF EXISTS").consume()
        session.run(f"CREATE DATABASE `{database}` IF NOT EXISTS").consume()
        for _ in range(40):
            status = session.run(
                "SHOW DATABASES YIELD name, currentStatus WHERE name = $name RETURN currentStatus",
                name=database,
            ).single()
            if status and str(status["currentStatus"]).lower() == "online":
                return
            time.sleep(0.5)
    raise RuntimeError(f"Database did not become available: {database}")


def drop_database(driver, database: str) -> None:
    require(bool(DATABASE_PATTERN.fullmatch(database)), f"Unsafe database name: {database}")
    with driver.session(database="system") as session:
        session.run(f"DROP DATABASE `{database}` IF EXISTS").consume()


def load_and_validate_dataset(driver, database: str, scenario: dict[str, Any]) -> dict[str, int]:
    with driver.session(database=database) as session:
        session.run("CREATE CONSTRAINT northstar_demo_id IF NOT EXISTS FOR (n:NorthstarDemo) REQUIRE n.demoId IS UNIQUE").consume()
        for node in scenario["nodes"]:
            labels = ":".join(f"`{label}`" for label in ["NorthstarDemo", *node["labels"]])
            session.run(
                f"MERGE (n:{labels} {{demoId: $demoId}}) SET n += $properties",
                demoId=node["id"],
                properties=node.get("properties", {}),
            ).consume()
        for relationship in scenario["relationships"]:
            session.run(
                f"""
                MATCH (source:NorthstarDemo {{demoId: $sourceId}})
                MATCH (target:NorthstarDemo {{demoId: $targetId}})
                MERGE (source)-[r:`{relationship['type']}`]->(target)
                SET r.demoCase = $scenarioId
                """,
                sourceId=relationship["from"],
                targetId=relationship["to"],
                scenarioId=scenario["scenario_id"],
            ).consume()

        counts = session.run(
            """
            MATCH (n:NorthstarDemo)
            WITH count(n) AS nodeCount
            MATCH (:NorthstarDemo)-[r]->(:NorthstarDemo)
            RETURN nodeCount, count(r) AS relationshipCount
            """
        ).single()
        require(counts["nodeCount"] == len(scenario["nodes"]), "Dataset node count mismatch")
        require(counts["relationshipCount"] == len(scenario["relationships"]), "Dataset relationship count mismatch")

        forbidden = session.run(
            """
            MATCH (n:NorthstarDemo)
            WITH collect(DISTINCT labels(n)) AS labelSets
            MATCH (:NorthstarDemo)-[r]->(:NorthstarDemo)
            RETURN labelSets, collect(DISTINCT type(r)) AS relationshipTypes
            """
        ).single()
        flat_labels = {label for label_set in forbidden["labelSets"] for label in label_set}
        require(not (flat_labels & FORBIDDEN_DATASET_LABELS), "Ontology schema labels leaked into dataset")
        require(
            not (set(forbidden["relationshipTypes"]) & FORBIDDEN_DATASET_RELATIONSHIPS),
            "Ontology-only relationships leaked into dataset",
        )

        trace = session.run(
            """
            MATCH (client:CustodianClient {demoId: 'client-hrfo'})
                  -[:hasCustodyAccount]->(account:CustodyAccount)
                  -[:hasSettlementInstruction]->(instruction:SettlementInstruction)
                  -[:instructsCashMovement]->(movement:CashMovement)
            RETURN client.hasClientDisplayName AS client,
                   account.hasCustodyAccountId AS account,
                   instruction.hasSettlementInstructionId AS instruction,
                   movement.hasPaymentReference AS paymentReference
            """
        ).single()
        require(trace is not None, "Client-to-cash-movement trace was not found")
        require(trace["paymentReference"] == "PAY-2026-000731", "Unexpected payment reference")

    return {"nodes": counts["nodeCount"], "relationships": counts["relationshipCount"], "traces": 1}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live-schema", action="store_true", help="Validate the target ontology in stagingdb")
    parser.add_argument("--live-data", action="store_true", help="Load and validate instance data in an isolated database")
    parser.add_argument("--schema-database", default="stagingdb")
    parser.add_argument("--database", default=DEFAULT_DATASET_DATABASE)
    parser.add_argument("--reset-database", action="store_true")
    parser.add_argument("--cleanup", action="store_true", help="Drop the isolated dataset database and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv_if_available()
    case = load_json(CASE_PATH)
    scenario = load_json(SCENARIO_PATH)

    static_result = validate_static_case(case, scenario)
    print(f"Static case validation passed: {static_result}")

    if not (args.live_schema or args.live_data or args.cleanup):
        print("Live Neo4j checks not requested.")
        return 0

    driver = neo4j_driver()
    try:
        if args.cleanup:
            drop_database(driver, args.database)
            print(f"Dropped disposable dataset database: {args.database}")
            return 0
        if args.live_schema:
            schema_result = validate_live_schema(driver, case, args.schema_database)
            print(f"Live staging schema validation passed: {schema_result}")
        if args.live_data:
            ensure_database(driver, args.database, args.reset_database)
            data_result = load_and_validate_dataset(driver, args.database, scenario)
            print(f"Live dataset flow passed in {args.database}: {data_result}")
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
