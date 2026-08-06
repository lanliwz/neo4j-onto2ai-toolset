#!/usr/bin/env python3
"""Verify generated schema artifacts and, optionally, live stagingdb content."""

from __future__ import annotations

import argparse
import json
import py_compile
import re
from pathlib import Path

from harness_config import DOMAINS, DomainSpec, selected_domains
from harness_log import append_harness_log


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run schema-mode verification.")
    parser.add_argument("--domain", action="append", choices=sorted(DOMAINS))
    parser.add_argument("--live", action="store_true", help="Verify ontology classes in stagingdb.")
    parser.add_argument("--database", default="stagingdb")
    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify_artifact(path: Path) -> None:
    require(path.is_file() and path.stat().st_size > 0, f"Missing or empty schema artifact: {path}")
    if path.suffix == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        require(isinstance(value, dict), f"Schema JSON must contain an object: {path}")
    elif path.suffix == ".cypher":
        text = path.read_text(encoding="utf-8")
        require(bool(re.search(r"CREATE\s+CONSTRAINT", text, re.IGNORECASE)), f"No constraints found in {path}")
    elif path.suffix == ".md":
        require("#" in path.read_text(encoding="utf-8"), f"Schema context has no headings: {path}")


def verify_static(spec: DomainSpec) -> None:
    for canonical, packaged in zip(spec.canonical_ontologies, spec.packaged_ontologies, strict=True):
        require(canonical.read_bytes() == packaged.read_bytes(), f"Ontology mirror drift: {canonical} != {packaged}")
    for artifact in spec.schema_artifacts:
        verify_artifact(artifact)
    for module in spec.model_modules:
        py_compile.compile(str(module), doraise=True)
    require(spec.smoke_test.is_file(), f"Missing dataset smoke test: {spec.smoke_test}")


def ontology_class_uris(paths: tuple[Path, ...]) -> set[str]:
    from rdflib import Graph, OWL, RDF

    graph = Graph()
    for path in paths:
        graph.parse(path)
    return {str(subject) for subject in graph.subjects(RDF.type, OWL.Class)}


def verify_live(specs: list[DomainSpec], database: str) -> None:
    import os
    from neo4j import GraphDatabase
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    password = os.getenv("NEO4J_MODEL_DB_PASSWORD")
    require(bool(password), "NEO4J_MODEL_DB_PASSWORD is required for live schema verification")
    uri = os.getenv("NEO4J_MODEL_DB_URL", "bolt://localhost:7687")
    username = os.getenv("NEO4J_MODEL_DB_USERNAME", "neo4j")
    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        with driver.session(database=database) as session:
            for spec in specs:
                expected = ontology_class_uris(spec.canonical_ontologies)
                row = session.run(
                    "MATCH (c:owl__Class) WHERE c.uri IN $uris RETURN collect(c.uri) AS uris",
                    uris=sorted(expected),
                ).single()
                actual = set(row["uris"] if row else [])
                missing = expected - actual
                require(not missing, f"{spec.name}: {len(missing)} ontology classes missing from {database}")
    finally:
        driver.close()


def main() -> int:
    args = parse_args()
    specs = selected_domains(args.domain)
    try:
        for spec in specs:
            verify_static(spec)
        if args.live:
            verify_live(specs, args.database)
        status = "passed" if args.live else "checked"
        append_harness_log(
            script="harness_verify_schema.py",
            mode="schema",
            status=status,
            domains=[spec.name for spec in specs],
            live=args.live,
            database=args.database if args.live else None,
        )
        print("Harness schema verification passed." if args.live else "Harness schema artifact checks completed; stagingdb was not queried.")
        print(f"domains: {', '.join(spec.name for spec in specs)}")
        print(f"stagingdb: {'verified' if args.live else 'not requested'}")
        return 0
    except Exception as exc:
        append_harness_log(script="harness_verify_schema.py", mode="schema", status="failed", error=str(exc))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
