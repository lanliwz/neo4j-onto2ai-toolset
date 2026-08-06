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
        help="Flow to run. 'verify' runs repository checks; 'release' forces live checks and package builds.",
    )
    parser.add_argument(
        "--skip-xmllint",
        action="store_true",
        help="Pass through to ontology verification.",
    )
    parser.add_argument("--domain", action="append", choices=["entitlement", "parcel"])
    parser.add_argument("--live", action="store_true", help="Run live stagingdb and isolated dataset checks.")
    parser.add_argument(
        "--package",
        action="append",
        choices=["core", "entitlement", "parcel", "all"],
        help="Release package to build. Defaults to core.",
    )
    return parser.parse_args()


def run_step(name: str, cmd: list[str]) -> None:
    print(f"==> {name}")
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def main() -> int:
    args = parse_args()

    live = args.live or args.profile == "release"
    domains = args.domain or ["entitlement", "parcel"]
    domain_args = [value for domain in domains for value in ("--domain", domain)]

    flow: list[tuple[str, list[str]]] = [
        ("Preflight: ontology", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "ontology"]),
        ("Ontology verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_ontology.py")]),
        ("Preflight: schema", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "schema"]),
        ("Schema verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_schema.py"), *domain_args]),
        ("Preflight: dataset", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "dataset"]),
        ("Dataset verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_dataset.py"), *domain_args]),
        ("Mode boundary verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_mode_boundaries.py")]),
    ]

    if args.skip_xmllint:
        flow[1][1].append("--skip-xmllint")

    if live:
        flow[3][1].append("--live")
        flow[5][1].append("--live")

    if args.profile == "release":
        packages = args.package or ["core"]
        package_args = [value for package in packages for value in ("--package", package)]
        flow.extend(
            [
                ("Preflight: release", [sys.executable, str(SCRIPT_DIR / "harness_preflight.py"), "release"]),
                ("Release verification", [sys.executable, str(SCRIPT_DIR / "harness_verify_release.py"), "--build", *package_args]),
            ]
        )

    try:
        for step_name, cmd in flow:
            run_step(step_name, cmd)

        append_harness_log(
            script="harness_run.py",
            mode="release" if args.profile == "release" else "schema",
            status="passed" if live else "checked",
            profile=args.profile,
            step_count=len(flow),
            xmllint_enabled=not args.skip_xmllint,
            live_enabled=live,
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
            live_enabled=live,
            build_enabled=args.profile == "release",
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
