#!/usr/bin/env python3
"""Package-aware release-mode verification for Onto2AI distributions."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tarfile
import tomllib
import zipfile
from pathlib import Path

from rdflib import Graph, OWL

from harness_config import RELEASES, ReleaseSpec, selected_releases
from harness_log import append_harness_log


REPO_ROOT = Path(__file__).resolve().parent.parent
README_MD = REPO_ROOT / "README.md"
MODELLER_MAIN = REPO_ROOT / "onto2ai_modeller" / "main.py"
GENERIC_DOCS = [
    README_MD,
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
    parser = argparse.ArgumentParser(description="Run package-aware release verification.")
    parser.add_argument("--package", action="append", choices=[*sorted(RELEASES), "all"])
    parser.add_argument("--build", action="store_true", help="Build and inspect selected distributions.")
    return parser.parse_args()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def extract(text: str, pattern: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"Could not find {label}")
    return match.group(1)


def core_version() -> str:
    setup_text = (REPO_ROOT / "setup.py").read_text(encoding="utf-8")
    version = extract(setup_text, r'version="([^"]+)"', "setup.py version")
    modeller = extract(MODELLER_MAIN.read_text(encoding="utf-8"), r'version="([^"]+)"', "Modeller version")
    readme = extract(README_MD.read_text(encoding="utf-8"), r"onto2ai_engineer-([0-9.]+)-py3", "README wheel version")
    require(len({version, modeller, readme}) == 1, f"Core version mismatch: setup={version}, modeller={modeller}, README={readme}")
    return version


def domain_version(spec: ReleaseSpec) -> str:
    metadata = tomllib.loads(spec.version_file.read_text(encoding="utf-8"))
    version = str(metadata["project"]["version"])
    init_version = extract(
        (spec.package_dir / "__init__.py").read_text(encoding="utf-8"),
        r'__version__\s*=\s*"([^"]+)"',
        f"{spec.name} __version__",
    )
    ontology_versions: set[str] = set()
    for ontology in spec.ontology_files:
        graph = Graph().parse(ontology)
        ontology_versions.update(str(value) for value in graph.objects(None, OWL.versionInfo))
    require(init_version == version, f"{spec.name} version mismatch: pyproject={version}, __init__={init_version}")
    require(not ontology_versions or ontology_versions == {version}, f"{spec.name} ontology versions do not match {version}: {sorted(ontology_versions)}")
    return version


def check_core_boundaries() -> None:
    setup_text = (REPO_ROOT / "setup.py").read_text(encoding="utf-8")
    manifest_text = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    require("recursive-include staging " not in manifest_text, "Root distribution must not package transient staging/")
    for token in ("onto2ai_entitlement", "onto2ai_parcel"):
        require(f"prune {token}" in manifest_text, f"MANIFEST.in must prune {token}")
    require(
        'exclude=["onto2ai_entitlement*", "onto2ai_parcel*"]' in setup_text,
        "Core setup.py must exclude domain packages",
    )
    for path in GENERIC_DOCS:
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_GENERIC_DOC_PATTERNS:
            require(pattern not in text, f"Stale generic-doc reference {pattern!r} in {path}")


def build_distribution(spec: ReleaseSpec, version: str) -> tuple[Path, Path]:
    uv = shutil.which("uv")
    require(bool(uv), "uv is required for release builds")
    dist_dir = spec.package_dir / "dist"
    subprocess.run([uv, "build", "--out-dir", str(dist_dir)], check=True, cwd=spec.package_dir)
    normalized = spec.distribution_name.replace("-", "_")
    wheel = dist_dir / f"{normalized}-{version}-py3-none-any.whl"
    sdist = dist_dir / f"{normalized}-{version}.tar.gz"
    require(wheel.is_file(), f"Missing built wheel: {wheel}")
    require(sdist.is_file(), f"Missing built source distribution: {sdist}")
    return wheel, sdist


def inspect_distribution(spec: ReleaseSpec, wheel: Path, sdist: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        wheel_names = archive.namelist()
    with tarfile.open(sdist) as archive:
        sdist_names = archive.getnames()
    if spec.name == "core":
        for prefix in ("onto2ai_entitlement/", "onto2ai_parcel/"):
            require(not any(name.startswith(prefix) for name in wheel_names), f"Core wheel contains {prefix}")
            require(not any(f"/{prefix}" in name for name in sdist_names), f"Core sdist contains {prefix}")
    else:
        package_prefix = spec.package_dir.name + "/"
        require(any(name.startswith(package_prefix + "ontology/") for name in wheel_names), f"{spec.name} wheel lacks ontology files")
        require(any(name.startswith(package_prefix + "staging/") for name in wheel_names), f"{spec.name} wheel lacks schema artifacts")


def main() -> int:
    args = parse_args()
    specs = selected_releases(args.package)
    try:
        versions: dict[str, str] = {}
        for spec in specs:
            version = core_version() if spec.name == "core" else domain_version(spec)
            versions[spec.name] = version
            if spec.name == "core":
                check_core_boundaries()
            if args.build:
                inspect_distribution(spec, *build_distribution(spec, version))

        status = "passed" if args.build else "checked"
        append_harness_log(
            script="harness_verify_release.py",
            mode="release",
            status=status,
            packages=[spec.name for spec in specs],
            versions=versions,
            build_enabled=args.build,
        )
        if args.build:
            print("Harness release verification passed.")
        else:
            print("Harness release readiness checks completed; build was not run.")
        for name, version in versions.items():
            print(f"{name}: {version}")
        return 0
    except Exception as exc:
        append_harness_log(script="harness_verify_release.py", mode="release", status="failed", error=str(exc))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
