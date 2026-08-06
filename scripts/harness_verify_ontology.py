#!/usr/bin/env python3
"""Generic ontology-mode verification for the Onto2AI toolset."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from harness_config import DOMAINS, CANONICAL_ONTOLOGY_ROOT
from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATE_SCRIPT = REPO_ROOT / "scripts" / "validate_ontology.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ontology-mode verification for the toolset.")
    parser.add_argument(
        "path",
        nargs="?",
        help="RDF file or directory to validate. Defaults to canonical and packaged Onto2AI ontologies.",
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
        if args.path:
            targets = [Path(args.path).resolve()]
        else:
            targets = [CANONICAL_ONTOLOGY_ROOT]
            targets.extend(spec.package_dir / "ontology" for spec in DOMAINS.values())
        for target in targets:
            if not target.exists():
                raise FileNotFoundError(f"{target} does not exist")
            run([sys.executable, str(VALIDATE_SCRIPT), str(target)])

        rdf_files = sorted({rdf for target in targets for rdf in iter_rdf_files(target)})
        if not args.path:
            for spec in DOMAINS.values():
                for canonical, packaged in zip(spec.canonical_ontologies, spec.packaged_ontologies, strict=True):
                    if canonical.read_bytes() != packaged.read_bytes():
                        raise RuntimeError(f"Ontology mirror drift: {canonical} != {packaged}")
        if not args.skip_xmllint:
            xmllint = shutil.which("xmllint")
            if xmllint is None:
                raise RuntimeError("xmllint is required for ontology-mode verification. Use --skip-xmllint to bypass.")
            for rdf_file in rdf_files:
                run([xmllint, "--noout", str(rdf_file)])

        print("Harness ontology verification passed.")
        print(f"targets: {len(targets)}")
        print(f"rdf_file_count: {len(rdf_files)}")
        print(f"xmllint: {'skipped' if args.skip_xmllint else 'enabled'}")

        append_harness_log(
            script="harness_verify_ontology.py",
            mode="ontology",
            status="passed",
            targets=[str(target) for target in targets],
            rdf_file_count=len(rdf_files),
            xmllint_enabled=not args.skip_xmllint,
        )
        return 0
    except Exception as exc:
        append_harness_log(
            script="harness_verify_ontology.py",
            mode="ontology",
            status="failed",
            targets=[str(Path(args.path).resolve())] if args.path else ["default"],
            error=str(exc),
            xmllint_enabled=not args.skip_xmllint,
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
