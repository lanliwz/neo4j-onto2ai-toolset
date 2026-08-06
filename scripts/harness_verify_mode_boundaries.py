#!/usr/bin/env python3
"""Fail-fast checks for generic toolset harness boundaries."""

from __future__ import annotations

import re
from pathlib import Path

from harness_config import DOMAINS
from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DOC_TOKENS = {
    REPO_ROOT / "AGENTS.md": ["stagingdb", "isolated disposable dataset database", "owl__Class", "rdf__type", "rdfs__subClassOf"],
    REPO_ROOT / "docs" / "harness" / "modes.md": ["stagingdb", "isolated disposable database", "ontology mode", "schema mode", "dataset mode", "release mode"],
    REPO_ROOT / "docs" / "harness" / "checklists.md": ["Entry Checks", "Allowed Files", "Allowed Databases", "Required Validators", "Exit Criteria"],
    REPO_ROOT / "README.md": ["Harness Modes", "Harness Checklists", "harness_preflight.py"],
}

CODE_ROOTS = [
    REPO_ROOT / "neo4j_onto2ai_toolset",
    REPO_ROOT / "onto2ai_modeller",
    *(spec.package_dir for spec in DOMAINS.values()),
]

WRITE_ONTOLOGY_PATTERN = re.compile(
    r"(?:CREATE|MERGE)\s*\([^)]*:(?:owl__Class|owl__Ontology|owl__Restriction)|"
    r"(?:CREATE|MERGE)\s*[^\n]*\[:(?:rdf__type|rdfs__subClassOf)",
    re.IGNORECASE,
)


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
    for root in CODE_ROOTS:
        files.extend(sorted(root.rglob("*.py")))
    return [path for path in files if "__pycache__" not in str(path)]


def check_dataset_boundary() -> int:
    smoke_tests = [spec.smoke_test for spec in DOMAINS.values()]
    require(smoke_tests, "No dataset smoke tests are registered")
    for path in smoke_tests:
        require(path.is_file(), f"Registered smoke test does not exist: {path}")
        text = path.read_text(encoding="utf-8")
        require(not WRITE_ONTOLOGY_PATTERN.search(text), f"Dataset smoke test writes ontology-only graph content: {path}")
        require("owl__Class" in text and "rdf__type" in text, f"Dataset smoke test lacks ontology-boundary assertions: {path}")
    return len(smoke_tests)


def main() -> int:
    try:
        check_required_docs()
        python_files = iter_python_files()
        smoke_tests_checked = check_dataset_boundary()

        print("Harness mode boundary verification passed.")
        print(f"python_files_scanned: {len(python_files)}")
        print(f"dataset_smoke_tests_checked: {smoke_tests_checked}")

        append_harness_log(
            script="harness_verify_mode_boundaries.py",
            mode="schema",
            status="passed",
            python_files_scanned=len(python_files),
            dataset_smoke_tests_checked=smoke_tests_checked,
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
