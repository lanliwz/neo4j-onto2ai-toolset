#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


NS = {
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}
RDF_ABOUT = f"{{{NS['rdf']}}}about"
RDF_RESOURCE = f"{{{NS['rdf']}}}resource"

ROLE_HINTS = (
    "advisor",
    "agent",
    "analyst",
    "attorney",
    "beneficiary",
    "broker",
    "buyer",
    "client",
    "counterparty",
    "custodian",
    "dealer",
    "depositor",
    "entity",
    "executor",
    "grantor",
    "guardian",
    "guarantor",
    "holder",
    "individual",
    "institution",
    "issuer",
    "landlord",
    "lender",
    "legal entity",
    "manager",
    "obligor",
    "officer",
    "owner",
    "party",
    "person",
    "provider",
    "representative",
    "seller",
    "settlor",
    "signatory",
    "sole proprietor",
    "tenant",
    "third party",
    "trustee",
    "trustor",
    "underwriter",
)
ACCOUNT_HINTS = (
    "account",
    "cash account",
    "shadow account",
)


@dataclass
class Finding:
    level: str
    path: Path
    line: int
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate RDF/XML ontology files.")
    parser.add_argument(
        "paths",
        nargs="+",
        help="RDF/XML file or directory to validate.",
    )
    return parser.parse_args()


def iter_rdf_files(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.rdf")))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"{path} does not exist")
    return files


def build_line_map(path: Path) -> dict[str, int]:
    line_map: dict[str, int] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        marker = 'rdf:about="'
        if marker not in line:
            continue
        start = line.find(marker) + len(marker)
        end = line.find('"', start)
        if end != -1:
            line_map.setdefault(line[start:end], line_no)
    return line_map


def local_name(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def local_base(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[0]
    return iri.rsplit("/", 1)[0]


def looks_like_party_role(label: str, definition: str) -> bool:
    text = f"{label} {definition}".lower()
    has_role_hint = any(hint in text for hint in ROLE_HINTS)
    has_account_hint = any(hint in text for hint in ACCOUNT_HINTS)
    return has_role_hint and not text.startswith("a technical or operational banking relationship linking") and not (
        has_account_hint and "party" not in text and "person" not in text and "entity" not in text
    )


def validate_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    line_map = build_line_map(path)

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        findings.append(Finding("ERROR", path, getattr(exc, "position", (1, 1))[0], f"XML parse error: {exc}"))
        return findings

    root = tree.getroot()
    local_entities = {
        el.attrib[RDF_ABOUT]
        for kind in ("Class", "ObjectProperty")
        for el in root.findall(f"owl:{kind}", NS)
        if RDF_ABOUT in el.attrib
    }

    entity_kinds: Counter[str] = Counter()
    for kind in ("Class", "ObjectProperty"):
        for el in root.findall(f"owl:{kind}", NS):
            about = el.attrib.get(RDF_ABOUT)
            if not about:
                continue
            entity_kinds[about] += 1
            if any(ord(ch) > 127 for ch in local_name(about)):
                findings.append(
                    Finding("ERROR", path, line_map.get(about, 1), f"Non-ASCII characters in identifier: {about}")
                )

    for about, count in entity_kinds.items():
        if count > 1:
            findings.append(Finding("ERROR", path, line_map.get(about, 1), f"IRI reused across entities: {about}"))

    for cls in root.findall("owl:Class", NS):
        about = cls.attrib.get(RDF_ABOUT)
        if not about:
            continue
        for parent in cls.findall("rdfs:subClassOf", NS):
            resource = parent.attrib.get(RDF_RESOURCE)
            if not resource:
                continue
            if local_name(resource) != local_name(about):
                if local_base(resource) == local_base(about) and resource not in local_entities:
                    findings.append(
                        Finding(
                            "ERROR",
                            path,
                            line_map.get(about, 1),
                            f"Broken local superclass reference: {about} -> {resource}",
                        )
                    )

    for prop in root.findall("owl:ObjectProperty", NS):
        about = prop.attrib.get(RDF_ABOUT)
        if not about:
            continue
        label = prop.findtext("rdfs:label", default="", namespaces=NS)
        definition = prop.findtext("skos:definition", default="", namespaces=NS)
        domain = prop.find("rdfs:domain", NS)
        range_ = prop.find("rdfs:range", NS)
        if domain is None or range_ is None:
            continue
        domain_ref = domain.attrib.get(RDF_RESOURCE, "")
        range_ref = range_.attrib.get(RDF_RESOURCE, "")
        if local_name(domain_ref) == "Account" and local_name(range_ref) == "Account" and looks_like_party_role(
            label, definition
        ):
            findings.append(
                Finding(
                    "ERROR",
                    path,
                    line_map.get(about, 1),
                    f"Suspicious Account->Account role property: {about} ({label})",
                )
            )

    return findings


def main() -> int:
    args = parse_args()
    try:
        files = iter_rdf_files(args.paths)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if not files:
        print("No RDF files found.", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    for path in files:
        findings.extend(validate_file(path))

    if findings:
        for finding in findings:
            print(f"{finding.level}: {finding.path}:{finding.line}: {finding.message}")
        print(f"\nValidation failed with {len(findings)} finding(s).", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} RDF file(s) with no findings.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
