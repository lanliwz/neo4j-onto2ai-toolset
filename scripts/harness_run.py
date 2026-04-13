#!/usr/bin/env python3
"""Run the generic Onto2AI toolset harness flow in sequence."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the generic toolset harness flow.")
    parser.add_argument(
        "profile",
        choices=("verify", "release"),
        help="Flow to run. 'verify' runs the generic checks; 'release' also performs a package build.",
    )
    parser.add_argument(
        "--skip-xmllint",
        action="store_true",
        help="Pass through to ontology verification.",
    )
    return parser.parse_args()


def run_step(name: str, cmd: list[str]) -> None:
    print(f"==> {name}")
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main() -> int:
    args = parse_args()

    flow: list[tuple[str, list[str]]] = [
        ("Preflight: ontology", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "ontology"]),
        ("Preflight: schema", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "schema"]),
        ("Ontology verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_ontology.py")]),
        ("Mode boundary verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_mode_boundaries.py")]),
        ("Preflight: release", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "release"]),
        ("Release verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_release.py")]),
    ]

    if args.skip_xmllint:
        flow[2][1].append("--skip-xmllint")

    if args.profile == "release":
        flow[-1][1].append("--build")

    try:
        for step_name, cmd in flow:
            run_step(step_name, cmd)

        append_harness_log(
            script="harness_run.py",
            mode="release" if args.profile == "release" else "schema",
            status="passed",
            profile=args.profile,
            step_count=len(flow),
            xmllint_enabled=not args.skip_xmllint,
            build_enabled=args.profile == "release",
        )
        print("Harness run completed.")
        print(f"profile: {args.profile}")
        print(f"step_count: {len(flow)}")
        return 0
    except Exception as exc:
        append_harness_log(
            script="harness_run.py",
            mode="release" if args.profile == "release" else "schema",
            status="failed",
            profile=args.profile,
            step_count=len(flow),
            xmllint_enabled=not args.skip_xmllint,
            build_enabled=args.profile == "release",
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
