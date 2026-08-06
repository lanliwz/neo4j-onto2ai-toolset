#!/usr/bin/env python3
"""Shared package and domain definitions for the repository harness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_ONTOLOGY_ROOT = (
    REPO_ROOT / "resource" / "ontology" / "www_onto2ai-toolset_com" / "ontology"
)


@dataclass(frozen=True)
class DomainSpec:
    name: str
    package_dir: Path
    canonical_ontologies: tuple[Path, ...]
    packaged_ontologies: tuple[Path, ...]
    schema_artifacts: tuple[Path, ...]
    model_modules: tuple[Path, ...]
    smoke_test: Path


@dataclass(frozen=True)
class ReleaseSpec:
    name: str
    package_dir: Path
    distribution_name: str
    version_file: Path
    ontology_files: tuple[Path, ...] = ()


ENTITLEMENT = DomainSpec(
    name="entitlement",
    package_dir=REPO_ROOT / "onto2ai_entitlement",
    canonical_ontologies=(CANONICAL_ONTOLOGY_ROOT / "entitlement" / "Onto2AIEntitlement.rdf",),
    packaged_ontologies=(REPO_ROOT / "onto2ai_entitlement" / "ontology" / "Onto2AIEntitlement.rdf",),
    schema_artifacts=(
        REPO_ROOT / "onto2ai_entitlement" / "staging" / "full_schema_model.json",
        REPO_ROOT / "onto2ai_entitlement" / "staging" / "neo4j_constraint.cypher",
        REPO_ROOT / "onto2ai_entitlement" / "staging" / "neo4j_query_context.md",
    ),
    model_modules=(REPO_ROOT / "onto2ai_entitlement" / "staging" / "pydantic_schema_model.py",),
    smoke_test=REPO_ROOT / "onto2ai_entitlement" / "staging" / "schema_to_data_flow_smoke_test.py",
)

PARCEL = DomainSpec(
    name="parcel",
    package_dir=REPO_ROOT / "onto2ai_parcel",
    canonical_ontologies=(
        CANONICAL_ONTOLOGY_ROOT / "parcel" / "Parcel.rdf",
        CANONICAL_ONTOLOGY_ROOT / "house" / "House.rdf",
        CANONICAL_ONTOLOGY_ROOT / "landscape" / "Landscape.rdf",
    ),
    packaged_ontologies=(
        REPO_ROOT / "onto2ai_parcel" / "ontology" / "Parcel.rdf",
        REPO_ROOT / "onto2ai_parcel" / "ontology" / "House.rdf",
        REPO_ROOT / "onto2ai_parcel" / "ontology" / "Landscape.rdf",
    ),
    schema_artifacts=(
        REPO_ROOT / "onto2ai_parcel" / "staging" / "neo4j_constraint.cypher",
        REPO_ROOT / "onto2ai_parcel" / "staging" / "neo4j_query_context.md",
    ),
    model_modules=(REPO_ROOT / "onto2ai_parcel" / "staging" / "pydantic_parcel_model.py",),
    smoke_test=REPO_ROOT / "onto2ai_parcel" / "staging" / "parcel_schema_smoke_test.py",
)

DOMAINS = {spec.name: spec for spec in (ENTITLEMENT, PARCEL)}

RELEASES = {
    "core": ReleaseSpec(
        name="core",
        package_dir=REPO_ROOT,
        distribution_name="onto2ai-engineer",
        version_file=REPO_ROOT / "setup.py",
    ),
    "entitlement": ReleaseSpec(
        name="entitlement",
        package_dir=ENTITLEMENT.package_dir,
        distribution_name="onto2ai-entitlement",
        version_file=ENTITLEMENT.package_dir / "pyproject.toml",
        ontology_files=ENTITLEMENT.packaged_ontologies,
    ),
    "parcel": ReleaseSpec(
        name="parcel",
        package_dir=PARCEL.package_dir,
        distribution_name="onto2ai-parcel",
        version_file=PARCEL.package_dir / "pyproject.toml",
        ontology_files=PARCEL.packaged_ontologies,
    ),
}


def selected_domains(names: list[str] | None) -> list[DomainSpec]:
    return [DOMAINS[name] for name in (names or sorted(DOMAINS))]


def selected_releases(names: list[str] | None) -> list[ReleaseSpec]:
    selected = names or ["core"]
    if "all" in selected:
        return [RELEASES[name] for name in sorted(RELEASES)]
    return [RELEASES[name] for name in selected]
