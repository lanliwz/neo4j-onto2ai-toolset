#!/usr/bin/env python3
"""Generic ontology-mode verification for the Onto2AI toolset."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ONTOLOGY_ROOT = REPO_ROOT / "resource" / "ontology" / "www_onto2ai-toolset_com" / "ontology"
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "validate_ontology.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ontology-mode verification for the toolset.")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(DEFAULT_ONTOLOGY_ROOT),
        help="RDF file or directory to validate. Defaults to the repo ontology root.",
    )
    parser.add_argument(
        "--skip-xmllint",
        action="store_true",
        help="Skip xmllint syntax validation.",
    )
    return parser.parse_args()


def iter_rdf_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.rdf"))


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main() -> int:
    args = parse_args()
    try:
        target = Path(args.path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"{target} does not exist")

        run([sys.executable, str(VALIDATE_SCRIPT), str(target)])

        rdf_files = iter_rdf_files(target)
        if not args.skip_xmllint:
            xmllint = shutil.which("xmllint")
            if xmllint is None:
                raise RuntimeError("xmllint is required for ontology-mode verification. Use --skip-xmllint to bypass.")
            for rdf_file in rdf_files:
                run([xmllint, "--noout", str(rdf_file)])

        print("Harness ontology verification passed.")
        print(f"target: {target}")
        print(f"rdf_file_count: {len(rdf_files)}")
        print(f"xmllint: {'skipped' if args.skip_xmllint else 'enabled'}")

        append_harness_log(
            script="harness_verify_ontology.py",
            mode="ontology",
            status="passed",
            target=str(target),
            rdf_file_count=len(rdf_files),
            xmllint_enabled=not args.skip_xmllint,
        )
        return 0
    except Exception as exc:
        append_harness_log(
            script="harness_verify_ontology.py",
            mode="ontology",
            status="failed",
            target=str(Path(args.path).resolve()),
            error=str(exc),
            xmllint_enabled=not args.skip_xmllint,
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
