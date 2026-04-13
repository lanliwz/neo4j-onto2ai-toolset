#!/usr/bin/env python3
"""Print the harness checklist for a selected operating mode.

This is a lightweight feedforward control for the generic toolset. It helps
contributors and agents classify work before making changes and keeps the
repo's ontology, schema, dataset, and release boundaries visible at runtime.
"""

from __future__ import annotations

import argparse
import sys

from harness_log import append_harness_log


MODE_DATA = {
    "ontology": {
        "title": "Ontology Mode",
        "entry_checks": [
            "Confirm the task changes ontology meaning rather than only implementation artifacts.",
            "Identify the RDF source-of-truth file under resource/ontology/... or the canonical packaged ontology path.",
            "Confirm the ontology base URI, namespace, and file path follow repo conventions.",
            "Identify any downstream Cypher or documentation that will need alignment.",
        ],
        "allowed_files": [
            "resource/ontology/...",
            "packaged ontology files such as onto2ai_<domain>/ontology/...",
            "matching ontology Cypher artifacts when alignment is required",
            "documentation that references ontology path, URI, or semantics",
        ],
        "allowed_databases": [
            "none required for pure ontology editing",
            "stagingdb if ontology/schema validation is part of the task",
        ],
        "required_validators": [
            "xmllint --noout <rdf_file>",
            "cross-check ontology URI, namespace, and RDF header values",
            "verify downstream Cypher still matches ontology fragments and intent when applicable",
        ],
        "exit_criteria": [
            "RDF is the final source of truth for the change.",
            "RDF syntax passes validation.",
            "Ontology URI/path references are consistent.",
            "Affected downstream schema artifacts are updated or explicitly queued for schema mode.",
        ],
    },
    "schema": {
        "title": "Schema Mode",
        "entry_checks": [
            "Confirm the ontology source is already updated.",
            "Identify which artifacts are in scope: Cypher, query context, constraints, Pydantic models, or schema validation scripts.",
            "Identify the canonical schema package or workspace location.",
            "Confirm stagingdb is the target database for validation.",
        ],
        "allowed_files": [
            "ontology-aligned Cypher files",
            "neo4j_query_context.md",
            "neo4j_constraint.cypher",
            "Pydantic model files",
            "schema validation scripts",
            "package-local staging artifacts such as onto2ai_<domain>/staging/...",
            "transient staging/ files only when explicitly workspace-local and not release sources",
        ],
        "allowed_databases": [
            "stagingdb",
        ],
        "required_validators": [
            "schema validation against stagingdb",
            "cross-check query context, constraints, and Pydantic models for drift",
            "verify schema artifacts still reflect ontology intent and naming",
        ],
        "exit_criteria": [
            "Schema artifacts are aligned to the ontology source.",
            "Validation passes in stagingdb.",
            "Query context, constraints, and models are mutually consistent.",
            "No schema artifact acts as a competing source of truth.",
        ],
    },
    "dataset": {
        "title": "Dataset Mode",
        "entry_checks": [
            "Confirm schema validation has already been completed separately.",
            "Identify the dataset smoke test or sample-data load path.",
            "Confirm testdb is the target runtime-style database.",
            "Confirm the test is instance-oriented, not ontology/schema-oriented.",
        ],
        "allowed_files": [
            "smoke test scripts",
            "sample data loaders",
            "dataset-oriented Pydantic usage",
            "package-local staging test artifacts",
            "runtime validation helpers",
        ],
        "allowed_databases": [
            "testdb",
        ],
        "required_validators": [
            "smoke test execution in testdb",
            "checks that no ontology schema nodes are loaded into testdb",
            "checks that no ontology-only edges such as rdf__type or rdfs__subClassOf are used in testdb",
            "checks that constraints reject invalid runtime data where applicable",
        ],
        "exit_criteria": [
            "Smoke tests pass in testdb.",
            "Runtime graph is dataset-only.",
            "Major entity, enumeration, and relationship paths are exercised.",
            "Ontology/schema validation remains separated from runtime data validation.",
        ],
    },
    "release": {
        "title": "Release Mode",
        "entry_checks": [
            "Confirm ontology, schema, and dataset validation are already complete for the scoped release.",
            "Identify the canonical package path for the deliverable.",
            "Identify the version files, milestone docs, or release notes that must stay aligned.",
            "Confirm the package is complete enough for release.",
        ],
        "allowed_files": [
            "package metadata",
            "version markers",
            "milestone and release notes",
            "package-local artifacts",
            "build configuration files",
        ],
        "allowed_databases": [
            "none by default",
            "only use databases if a release check explicitly reruns validation",
        ],
        "required_validators": [
            "version consistency checks",
            "package build",
            "artifact presence checks in the built package",
            "verification that released artifacts come from canonical package paths, not transient root staging/",
        ],
        "exit_criteria": [
            "Version metadata is aligned.",
            "Release notes or milestone notes match the shipped scope.",
            "Build succeeds.",
            "Released package contains only intended, finalized artifacts.",
        ],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show the harness checklist for a toolset operating mode.")
    parser.add_argument(
        "mode",
        choices=sorted(MODE_DATA.keys()),
        help="Operating mode to review before starting work.",
    )
    return parser.parse_args()


def print_section(title: str, items: list[str]) -> None:
    print(f"{title}:")
    for item in items:
        print(f"- {item}")
    print()


def main() -> int:
    args = parse_args()
    try:
        data = MODE_DATA[args.mode]

        print(data["title"])
        print("=" * len(data["title"]))
        print()
        print_section("Entry Checks", data["entry_checks"])
        print_section("Allowed Files", data["allowed_files"])
        print_section("Allowed Databases", data["allowed_databases"])
        print_section("Required Validators", data["required_validators"])
        print_section("Exit Criteria", data["exit_criteria"])

        append_harness_log(
            script="harness_preflight.py",
            mode=args.mode,
            status="passed",
            checklist_sections=5,
        )
        return 0
    except Exception as exc:
        append_harness_log(
            script="harness_preflight.py",
            mode=args.mode,
            status="failed",
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
