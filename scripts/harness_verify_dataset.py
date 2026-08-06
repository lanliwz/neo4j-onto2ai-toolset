#!/usr/bin/env python3
"""Verify dataset smoke-test boundaries and optionally execute them."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import uuid

from harness_config import DOMAINS, DomainSpec, selected_domains
from harness_log import append_harness_log


WRITE_ONTOLOGY_PATTERN = re.compile(
    r"(?:CREATE|MERGE)\s*\([^)]*:(?:owl__Class|owl__Ontology|owl__Restriction)|"
    r"(?:CREATE|MERGE)\s*[^\n]*\[:(?:rdf__type|rdfs__subClassOf)",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run dataset-mode verification.")
    parser.add_argument("--domain", action="append", choices=sorted(DOMAINS))
    parser.add_argument("--live", action="store_true", help="Execute smoke tests against isolated databases.")
    return parser.parse_args()


def verify_contract(spec: DomainSpec) -> None:
    source = spec.smoke_test.read_text(encoding="utf-8")
    if WRITE_ONTOLOGY_PATTERN.search(source):
        raise RuntimeError(f"Dataset smoke test writes ontology-only graph content: {spec.smoke_test}")
    if "owl__Class" not in source or "rdf__type" not in source:
        raise RuntimeError(f"Dataset smoke test does not assert ontology-node and edge absence: {spec.smoke_test}")


def run_live(spec: DomainSpec) -> None:
    database = f"{spec.name}-smoke-{uuid.uuid4().hex[:8]}"
    command = [sys.executable, str(spec.smoke_test), "--database", database, "--drop-database-after"]
    if spec.name == "entitlement":
        command.extend(["--reset-database", "--cleanup"])
    subprocess.run(command, check=True)


def main() -> int:
    args = parse_args()
    specs = selected_domains(args.domain)
    try:
        for spec in specs:
            verify_contract(spec)
            if args.live:
                run_live(spec)
        status = "passed" if args.live else "checked"
        append_harness_log(
            script="harness_verify_dataset.py",
            mode="dataset",
            status=status,
            domains=[spec.name for spec in specs],
            live=args.live,
        )
        print("Harness dataset verification passed." if args.live else "Harness dataset contracts checked; smoke tests were not executed.")
        print(f"domains: {', '.join(spec.name for spec in specs)}")
        print(f"smoke_tests: {'executed' if args.live else 'contracts verified'}")
        return 0
    except Exception as exc:
        append_harness_log(script="harness_verify_dataset.py", mode="dataset", status="failed", error=str(exc))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
