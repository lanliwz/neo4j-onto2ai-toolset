#!/usr/bin/env python3
"""Fail-fast checks for generic toolset harness boundaries."""

from __future__ import annotations

import re
from pathlib import Path

from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DOC_TOKENS = {
    REPO_ROOT / "AGENTS.md": ["stagingdb", "testdb", "owl__Class", "rdf__type", "rdfs__subClassOf"],
    REPO_ROOT / "docs" / "harness" / "modes.md": ["stagingdb", "testdb", "ontology mode", "schema mode", "dataset mode", "release mode"],
    REPO_ROOT / "docs" / "harness" / "checklists.md": ["Entry Checks", "Allowed Files", "Allowed Databases", "Required Validators", "Exit Criteria"],
    REPO_ROOT / "README.md": ["Harness Modes", "Harness Checklists", "harness_preflight.py"],
}

GENERIC_CODE_ROOTS = [
    REPO_ROOT / "neo4j_onto2ai_toolset",
    REPO_ROOT / "onto2ai_modeller",
]

FORBIDDEN_DATASET_SCHEMA_TOKENS = ("owl__Class", "owl__Ontology", "owl__Restriction", "rdf__type", "rdfs__subClassOf")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_required_docs() -> None:
    for path, tokens in REQUIRED_DOC_TOKENS.items():
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            require(token in text, f"Missing required token {token!r} in {path}")


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in GENERIC_CODE_ROOTS:
        files.extend(sorted(root.rglob("*.py")))
    return [path for path in files if "__pycache__" not in str(path)]


def check_generic_dataset_boundary() -> int:
    flagged = 0
    testdb_pattern = re.compile(r"\btestdb\b")
    for path in iter_python_files():
        text = path.read_text(encoding="utf-8")
        if not testdb_pattern.search(text):
            continue
        if any(token in text for token in FORBIDDEN_DATASET_SCHEMA_TOKENS):
            raise AssertionError(
                f"Generic toolset file mixes testdb with ontology-only tokens and should be split by mode: {path}"
            )
        flagged += 1
    return flagged


def main() -> int:
    try:
        check_required_docs()
        python_files = iter_python_files()
        scanned_testdb_files = check_generic_dataset_boundary()

        print("Harness mode boundary verification passed.")
        print(f"generic_python_files_scanned: {len(python_files)}")
        print(f"generic_testdb_files_scanned: {scanned_testdb_files}")

        append_harness_log(
            script="harness_verify_mode_boundaries.py",
            mode="schema",
            status="passed",
            generic_python_files_scanned=len(python_files),
            generic_testdb_files_scanned=scanned_testdb_files,
        )
        return 0
    except Exception as exc:
        append_harness_log(
            script="harness_verify_mode_boundaries.py",
            mode="schema",
            status="failed",
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
