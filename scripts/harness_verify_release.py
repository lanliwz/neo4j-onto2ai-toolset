#!/usr/bin/env python3
"""Generic release-mode verification for the Onto2AI toolset."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent
SETUP_PY = REPO_ROOT / "setup.py"
MANIFEST_IN = REPO_ROOT / "MANIFEST.in"
README_MD = REPO_ROOT / "README.md"
MODELLER_MAIN = REPO_ROOT / "onto2ai_modeller" / "main.py"
DIST_DIR = REPO_ROOT / "dist"

GENERIC_DOCS = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "docs" / "quickstart.md",
    REPO_ROOT / "docs" / "operator-runbook.md",
    REPO_ROOT / "docs" / "harness" / "modes.md",
    REPO_ROOT / "docs" / "harness" / "checklists.md",
]

FORBIDDEN_GENERIC_DOC_PATTERNS = (
    "python -m onto2ai_entitlement.staging.schema_to_data_flow_smoke_test",
    "python staging/schema_to_data_flow_smoke_test.py",
    "Build and publish the ontology package from `onto2ai_entitlement/`",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run release-mode verification for the toolset.")
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build source and wheel artifacts after version checks pass.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_version(text: str, pattern: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find {label}")
    return match.group(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def check_generic_docs() -> None:
    for path in GENERIC_DOCS:
        text = read_text(path)
        for pattern in FORBIDDEN_GENERIC_DOC_PATTERNS:
            require(pattern not in text, f"Found stale generic-doc reference {pattern!r} in {path}")


def check_no_root_staging_packaging() -> None:
    setup_lines = SETUP_PY.read_text(encoding="utf-8").splitlines()
    manifest_lines = MANIFEST_IN.read_text(encoding="utf-8").splitlines()

    for line in setup_lines:
        stripped = line.strip()
        require(
            not re.match(r'"staging"\s*:', stripped),
            "setup.py must not define package_data for a root staging package",
        )

    for line in manifest_lines:
        stripped = line.strip()
        require(
            not stripped.startswith("recursive-include staging "),
            "MANIFEST.in must not package transient root staging artifacts",
        )


def expected_dist_paths(version: str) -> tuple[Path, Path]:
    return (
        DIST_DIR / f"onto2ai_engineer-{version}-py3-none-any.whl",
        DIST_DIR / f"onto2ai_engineer-{version}.tar.gz",
    )


def check_dist_artifacts(version: str) -> None:
    wheel_path, sdist_path = expected_dist_paths(version)
    require(wheel_path.exists(), f"Missing built wheel artifact: {wheel_path}")
    require(sdist_path.exists(), f"Missing built source artifact: {sdist_path}")


def main() -> int:
    args = parse_args()
    try:
        setup_version = extract_version(read_text(SETUP_PY), r'version="([^"]+)"', "setup.py version")
        modeller_version = extract_version(read_text(MODELLER_MAIN), r'version="([^"]+)"', "Onto2AI Modeller version")
        readme_wheel_version = extract_version(
            read_text(README_MD),
            r"onto2ai_engineer-([0-9]+\.[0-9]+\.[0-9]+)-py3-none-any\.whl",
            "README wheel version example",
        )

        versions = {
            "setup.py": setup_version,
            "onto2ai_modeller/main.py": modeller_version,
            "README.md wheel example": readme_wheel_version,
        }
        unique_versions = sorted(set(versions.values()))
        if len(unique_versions) != 1:
            details = ", ".join(f"{name}={value}" for name, value in versions.items())
            raise RuntimeError(f"Release version mismatch detected: {details}")

        check_generic_docs()
        check_no_root_staging_packaging()

        if args.build:
            subprocess.run([sys.executable, "-m", "build", "--no-isolation"], check=True, cwd=REPO_ROOT)
            check_dist_artifacts(unique_versions[0])

        print("Harness release verification passed.")
        print(f"version: {unique_versions[0]}")
        print(f"build: {'enabled' if args.build else 'skipped'}")

        append_harness_log(
            script="harness_verify_release.py",
            mode="release",
            status="passed",
            version=unique_versions[0],
            build_enabled=args.build,
            dist_checked=args.build,
        )
        return 0
    except Exception as exc:
        append_harness_log(
            script="harness_verify_release.py",
            mode="release",
            status="failed",
            build_enabled=args.build,
            dist_checked=args.build,
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
