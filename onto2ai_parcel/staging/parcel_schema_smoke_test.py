#!/usr/bin/env python3
"""Dataset-only smoke test for the staged parcel slice in testdb.

Workflow:
1. Recreate the dedicated `testdb` database.
2. Apply dataset constraints derived from staging artifacts.
3. Load enum/reference data plus sample parcel instances into `testdb`.
4. Verify dataset topology and constraint behavior in `testdb`.

This test must not load ontology/schema nodes such as `owl__Class` into `testdb`.
"""

from __future__ import annotations

import os
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path

from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError
from pydantic import ValidationError

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from onto2ai_parcel.staging.pydantic_parcel_model import (
    Address,
    BoundaryVertex,
    CountryEnum,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GPSCoordinate,
    Parcel,
    PolygonGeometry,
    USPostalAddress,
    USStateEnum,
)

TEST_DB_NAME = "testdb"
STAGING_DB_NAME = os.getenv("NEO4J_STAGING_DB_NAME", "stagingdb")
US_POSTAL_ADDRESS_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#USPostalAddress"
ADDRESS_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Address"
PARCEL_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Parcel"
COUNTRY_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Country"
COUNTRY_SUBDIVISION_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#CountrySubdivision"
GPS_COORDINATE_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GPSCoordinate"
BOUNDARY_VERTEX_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#BoundaryVertex"
GEOMETRY_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#Geometry"
POLYGON_GEOMETRY_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#PolygonGeometry"
GEOJSON_FEATURE_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GeoJSONFeature"
GEOJSON_FEATURE_COLLECTION_URI = "http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#GeoJSONFeatureCollection"
XSD_STRING_URI = "http://www.w3.org/2001/XMLSchema#string"
USA_URI = "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/UnitedStatesOfAmerica"
CANADA_URI = "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/Canada"
QUERY_CONTEXT_PATH = THIS_DIR / "neo4j_query_context.md"
CONSTRAINT_PATH = THIS_DIR / "neo4j_constraint.cypher"


@dataclass(frozen=True)
class Neo4jConfig:
    uri: str
    username: str
    password: str


def get_neo4j_config() -> Neo4jConfig:
    uri = os.getenv("NEO4J_MODEL_DB_URL", "bolt://localhost:7687")
    username = os.getenv("NEO4J_MODEL_DB_USERNAME", "neo4j")
    password = os.getenv("NEO4J_MODEL_DB_PASSWORD")
    if not password:
        raise RuntimeError("NEO4J_MODEL_DB_PASSWORD is required")
    return Neo4jConfig(uri=uri, username=username, password=password)


def recreate_test_database(driver, db_name: str) -> None:
    with driver.session(database="system") as session:
        session.run(f"DROP DATABASE `{db_name}` IF EXISTS").consume()
        session.run(f"CREATE DATABASE `{db_name}` IF NOT EXISTS").consume()
        for _ in range(30):
            row = session.run(
                "SHOW DATABASES YIELD name, currentStatus "
                "WHERE name = $name RETURN currentStatus AS status",
                name=db_name,
            ).single()
            if row and str(row["status"]).lower() == "online":
                break
            time.sleep(0.5)


def parse_constraints_file(path: Path) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        current.append(line)
        if stripped.endswith(";"):
            stmt = "\n".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
    if current:
        stmt = "\n".join(current).strip()
        if stmt:
            statements.append(stmt)
    return statements


def parse_required_constraints(path: Path) -> dict[str, set[str]]:
    required_by_label: dict[str, set[str]] = {}
    pattern = re.compile(
        r"FOR \(n:`(?P<label>[^`]+)`\) REQUIRE n.`(?P<prop>[^`]+)` IS NOT NULL",
        re.IGNORECASE,
    )
    for stmt in parse_constraints_file(path):
        match = pattern.search(stmt)
        if match:
            required_by_label.setdefault(match.group("label"), set()).add(match.group("prop"))
    return required_by_label


def apply_constraints(driver, db_name: str, path: Path) -> int:
    statements = parse_constraints_file(path)
    applied = 0
    with driver.session(database=db_name) as session:
        for stmt in statements:
            if stmt.upper().startswith("CREATE CONSTRAINT"):
                session.run(stmt).consume()
                applied += 1
    return applied


def parse_query_context(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8").splitlines()

    section = None
    properties: dict[str, set[str]] = {}
    topology: set[tuple[str, str, str]] = set()
    enum_members: dict[str, list[tuple[str, str]]] = {}
    label_to_uri: dict[str, str] = {}

    for line in text:
        if line.startswith("## Section 1:"):
            section = 1
            continue
        if line.startswith("## Section 3:"):
            section = 3
            continue
        if line.startswith("## Section 4:"):
            section = 4
            continue
        if line.startswith("## Section 5:"):
            section = 5
            continue
        if line.startswith("## Section "):
            section = None
            continue

        if section == 1 and line.startswith("|") and not line.startswith("| ---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4 and parts[0] != "Label":
                label, _, uri, _ = parts[:4]
                label_to_uri[label] = uri

        elif section == 3 and line.startswith("|") and not line.startswith("| ---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 4 and parts[0] != "Node Label":
                node_label, prop, _, mandatory = parts[:4]
                if mandatory.lower() == "yes":
                    properties.setdefault(node_label, set()).add(prop)

        elif section == 4 and line.startswith("- `(:"):
            match = re.match(r"- `\(:([^\)]+)\)-\[:([^\]]+)\]->\(:([^\)]+)\)`", line)
            if match:
                topology.add(match.groups())

        elif section == 5 and line.startswith("|") and not line.startswith("| ---"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 3 and parts[0] != "Enum Class":
                enum_class, member_label, member_uri = parts[:3]
                enum_members.setdefault(enum_class, []).append((member_label, member_uri))

    return {
        "label_to_uri": label_to_uri,
        "mandatory_properties": properties,
        "topology": topology,
        "enum_members": enum_members,
    }


def build_sample_address() -> USPostalAddress:
    return USPostalAddress(
        addressId="addr-1",
        streetAddressLine1="1 Main St",
        addressLine2="Unit 2A",
        cityName="Jersey City",
        subdivision=USStateEnum.NJ,
        postalCode="07302",
        country=CountryEnum.UNITED_STATES_OF_AMERICA,
    )


def build_sample_boundary_vertices() -> list[BoundaryVertex]:
    return [
        BoundaryVertex(
            gpsCoordinateId="vtx-1",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
            vertexSequenceNumber=1,
        ),
        BoundaryVertex(
            gpsCoordinateId="vtx-2",
            latitude=Decimal("40.7130"),
            longitude=Decimal("-74.0055"),
            vertexSequenceNumber=2,
        ),
    ]


def build_sample_polygon_geometry(vertices: list[BoundaryVertex]) -> PolygonGeometry:
    return PolygonGeometry(
        geometryId="geom-1",
        coordinateSequenceText="40.7128,-74.0060 40.7130,-74.0055",
        hasBoundaryVertex=vertices,
    )


def build_sample_parcel(address: USPostalAddress, geometry: PolygonGeometry) -> Parcel:
    return Parcel(
        parcelId="parcel-1",
        parcelIdentifier="P-0001",
        fullAddressText="1 Main St, Unit 2A, Jersey City, NJ 07302",
        hasParcelAddress=[address],
        hasParcelGeometry=[geometry],
    )


def build_sample_feature(parcel: Parcel) -> GeoJSONFeature:
    return GeoJSONFeature(
        featureId="feature-1",
        geometryTypeName="Polygon",
        sourceObjectId="source-1",
        representsParcel=[parcel],
    )


def build_sample_feature_collection(feature: GeoJSONFeature) -> GeoJSONFeatureCollection:
    return GeoJSONFeatureCollection(
        featureCollectionId="fc-1",
        hasFeature=[feature],
    )

def neo4j_compatible(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: neo4j_compatible(v) for k, v in value.items()}
    if isinstance(value, list):
        return [neo4j_compatible(v) for v in value]
    return value


def load_enum_reference_data(driver, query_context: dict[str, object]) -> None:
    country_members = query_context["enum_members"].get("Country", [])
    subdivision_members = query_context["enum_members"].get("CountrySubdivision", [])
    with driver.session(database=TEST_DB_NAME) as session:
        for label, uri in country_members:
            session.run(
                """
                MERGE (country:Country:Resource {uri: $uri})
                SET country.rdfs__label = $label
                """,
                uri=uri,
                label=label,
            ).consume()
        for label, uri in subdivision_members:
            session.run(
                """
                MERGE (subdivision:CountrySubdivision:Resource {uri: $uri})
                SET subdivision.rdfs__label = $label,
                    subdivision.fnd_utl_av__preferredDesignation = $code
                """,
                uri=uri,
                label=label,
                code=uri.rsplit("-", 1)[-1],
            ).consume()


def load_sample_instance_data(driver) -> None:
    address = build_sample_address()
    vertices = build_sample_boundary_vertices()
    geometry = build_sample_polygon_geometry(vertices)
    parcel = build_sample_parcel(address, geometry)
    feature = build_sample_feature(parcel)
    collection = build_sample_feature_collection(feature)

    address_props = neo4j_compatible(address.model_dump(by_alias=True))
    geometry_props = neo4j_compatible(
        geometry.model_dump(by_alias=True, exclude={"has_boundary_vertex"})
    )
    parcel_props = neo4j_compatible(
        parcel.model_dump(by_alias=True, exclude={"has_parcel_address", "has_parcel_geometry"})
    )
    feature_props = neo4j_compatible(
        feature.model_dump(by_alias=True, exclude={"represents_parcel"})
    )
    collection_props = neo4j_compatible(
        collection.model_dump(by_alias=True, exclude={"has_feature"})
    )
    with driver.session(database=TEST_DB_NAME) as session:
        session.run(
            """
            MERGE (parcel:Parcel:Resource {uri: $parcel_instance_uri})
            SET parcel += $parcel_props,
                parcel.rdfs__label = 'sample parcel'
            MERGE (address:USPostalAddress:Address:Resource {uri: $address_instance_uri})
            SET address += $address_props,
                address.rdfs__label = 'sample US postal address'
            MERGE (geometry:PolygonGeometry:Geometry:Resource {uri: $geometry_instance_uri})
            SET geometry += $geometry_props,
                geometry.rdfs__label = 'sample polygon geometry'
            MERGE (feature:GeoJSONFeature:Resource {uri: $feature_instance_uri})
            SET feature += $feature_props,
                feature.rdfs__label = 'sample GeoJSON feature'
            MERGE (collection:GeoJSONFeatureCollection:Resource {uri: $collection_instance_uri})
            SET collection += $collection_props,
                collection.rdfs__label = 'sample GeoJSON feature collection'
            WITH parcel, address, geometry, feature, collection
            MATCH (country:Country:Resource {uri: $country_uri})
            MATCH (subdivision:CountrySubdivision:Resource {uri: $subdivision_uri})
            MERGE (parcel)-[:hasParcelAddress {
                uri: $has_parcel_address_uri,
                rdfs__label: 'has parcel address',
                materialized: true
            }]->(address)
            MERGE (parcel)-[:hasParcelGeometry {
                uri: $has_parcel_geometry_uri,
                rdfs__label: 'has parcel geometry',
                materialized: true
            }]->(geometry)
            MERGE (feature)-[:representsParcel {
                uri: $represents_parcel_uri,
                rdfs__label: 'represents parcel',
                materialized: true
            }]->(parcel)
            MERGE (collection)-[:hasFeature {
                uri: $has_feature_uri,
                rdfs__label: 'has feature',
                materialized: true
            }]->(feature)
            MERGE (address)-[:hasCountry {
                uri: $has_country_uri,
                rdfs__label: 'has country',
                materialized: true
            }]->(country)
            MERGE (address)-[:hasSubdivision {
                uri: $has_subdivision_uri,
                rdfs__label: 'has subdivision',
                materialized: true
            }]->(subdivision)
            """,
            parcel_instance_uri="urn:test:parcel:1",
            address_instance_uri="urn:test:address:1",
            geometry_instance_uri="urn:test:geometry:1",
            feature_instance_uri="urn:test:feature:1",
            collection_instance_uri="urn:test:collection:1",
            country_uri=USA_URI,
            subdivision_uri="https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NJ",
            parcel_props=parcel_props,
            address_props=address_props,
            geometry_props=geometry_props,
            feature_props=feature_props,
            collection_props=collection_props,
            has_parcel_address_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasParcelAddress",
            has_parcel_geometry_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasParcelGeometry",
            represents_parcel_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#representsParcel",
            has_feature_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasFeature",
            has_country_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasCountry",
            has_subdivision_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasSubdivision",
        ).consume()
        for idx, vertex in enumerate(vertices, start=1):
            vertex_props = neo4j_compatible(vertex.model_dump(by_alias=True))
            session.run(
                """
                MATCH (geometry {uri: $geometry_uri})
                MERGE (vertex:BoundaryVertex:GPSCoordinate:Resource {uri: $vertex_uri})
                SET vertex += $vertex_props,
                    vertex.rdfs__label = 'sample boundary vertex'
                MERGE (geometry)-[:hasBoundaryVertex {
                    uri: $has_boundary_vertex_uri,
                    rdfs__label: 'has boundary vertex',
                    materialized: true
                }]->(vertex)
                """,
                geometry_uri="urn:test:geometry:1",
                vertex_uri=f"urn:test:vertex:{idx}",
                vertex_props=vertex_props,
                has_boundary_vertex_uri="http://www.onto2ai-toolset.com/ontology/parcel/Parcel/#hasBoundaryVertex",
            ).consume()


def assert_constraints_enforced(driver, required_by_label: dict[str, set[str]]) -> None:
    valid_props = {
        "Address": neo4j_compatible(Address(addressId="addr-invalid-base").model_dump(by_alias=True)),
        "USPostalAddress": neo4j_compatible(build_sample_address().model_dump(by_alias=True)),
        "GPSCoordinate": neo4j_compatible(GPSCoordinate(
            gpsCoordinateId="gps-invalid-base",
            latitude=Decimal("40.7128"),
            longitude=Decimal("-74.0060"),
        ).model_dump(by_alias=True)),
        "Geometry": {"geometryId": "geom-invalid-base"},
        "Parcel": neo4j_compatible(build_sample_parcel(
            build_sample_address(),
            build_sample_polygon_geometry(build_sample_boundary_vertices()),
        ).model_dump(by_alias=True, exclude={"has_parcel_address", "has_parcel_geometry"})),
        "GeoJSONFeature": neo4j_compatible(build_sample_feature(
            build_sample_parcel(
                build_sample_address(),
                build_sample_polygon_geometry(build_sample_boundary_vertices()),
            )
        ).model_dump(by_alias=True, exclude={"represents_parcel"})),
        "GeoJSONFeatureCollection": neo4j_compatible(build_sample_feature_collection(
            build_sample_feature(
                build_sample_parcel(
                    build_sample_address(),
                    build_sample_polygon_geometry(build_sample_boundary_vertices()),
                )
            )
        ).model_dump(by_alias=True, exclude={"has_feature"})),
    }
    label_aliases = {
        "Address": "Address:Resource",
        "USPostalAddress": "USPostalAddress:Address:Resource",
        "GPSCoordinate": "GPSCoordinate:Resource",
        "Geometry": "Geometry:Resource",
        "Parcel": "Parcel:Resource",
        "GeoJSONFeature": "GeoJSONFeature:Resource",
        "GeoJSONFeatureCollection": "GeoJSONFeatureCollection:Resource",
    }
    for label, required_props in sorted(required_by_label.items()):
        require(required_props, f"Expected required constraints for {label}")
        for missing_prop in sorted(required_props):
            invalid_props = {k: v for k, v in valid_props[label].items() if k != missing_prop}
            try:
                with driver.session(database=TEST_DB_NAME) as session:
                    session.run(
                        f"CREATE (n:{label_aliases[label]} $props)",
                        props={"uri": f"urn:test:invalid:{label}:{missing_prop}", **invalid_props},
                    ).consume()
            except ConstraintError:
                continue
            raise AssertionError(
                f"Constraint for required property '{missing_prop}' on '{label}' was not enforced"
            )


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def single_value(driver, query: str, **params):
    with driver.session(database=TEST_DB_NAME) as session:
        row = session.run(query, params).single()
        return row.value() if row is not None else None


def validate_testdb(driver) -> dict[str, object]:
    query_context = parse_query_context(QUERY_CONTEXT_PATH)
    required_constraints = parse_required_constraints(CONSTRAINT_PATH)
    sample_model = build_sample_address()
    model_fields = set(sample_model.model_dump(by_alias=True).keys())
    expected_required = query_context["mandatory_properties"].get(
        "USPostalAddress:Address",
        set(),
    )
    require(
        expected_required.issubset(model_fields),
        "Pydantic USPostalAddress model must cover all mandatory query-context properties",
    )
    constraint_required = required_constraints.get("USPostalAddress", set())
    require(
        expected_required == constraint_required,
        "Constraint file must match mandatory US postal address properties in query context",
    )
    expected_constraint_map = {
        "Address": query_context["mandatory_properties"].get("Address", set()),
        "USPostalAddress": query_context["mandatory_properties"].get("USPostalAddress:Address", set()),
        "GPSCoordinate": query_context["mandatory_properties"].get("GPSCoordinate", set()),
        "Geometry": query_context["mandatory_properties"].get("Geometry", set()),
        "Parcel": query_context["mandatory_properties"].get("Parcel", set()),
        "GeoJSONFeature": query_context["mandatory_properties"].get("GeoJSONFeature", set()),
        "GeoJSONFeatureCollection": query_context["mandatory_properties"].get(
            "GeoJSONFeatureCollection",
            set(),
        ),
    }
    for label, expected_props in expected_constraint_map.items():
        require(
            required_constraints.get(label, set()) == expected_props,
            f"Constraint file must match query context for {label}",
        )

    try:
        USPostalAddress(
            streetAddressLine1="1 Main St",
            cityName="Jersey City",
            subdivision=USStateEnum.NJ,
            postalCode="invalid-zip",
        )
    except ValidationError:
        zip_validation_ok = True
    else:
        zip_validation_ok = False
    require(zip_validation_ok, "Pydantic USPostalAddress model must reject invalid ZIP codes")
    assert_constraints_enforced(driver, {k: v for k, v in required_constraints.items() if k in expected_constraint_map})

    forbidden_rels = {"municipalityAddressName", "postalAddressCode", "hasMunicipality"}
    class_outgoing = single_value(
        driver,
        """
        MATCH (a {uri: $uri})-[r]->()
        RETURN collect(DISTINCT type(r)) AS rel_types
        """,
        uri="urn:test:address:1",
    )
    outgoing_set = set(class_outgoing or [])
    require(
        outgoing_set.isdisjoint(forbidden_rels),
        "Legacy duplicate address relationships should not remain",
    )
    for source_label, rel_type, target_label in query_context["topology"]:
        source_pattern = ":".join(f"`{part}`" for part in source_label.split(":"))
        target_pattern = ":".join(f"`{part}`" for part in target_label.split(":"))
        exists = single_value(
            driver,
            f"""
            MATCH (s:{source_pattern})-[r]->(t:{target_pattern})
            WHERE type(r) = $rel_type
            RETURN count(r) > 0 AS ok
            """,
            rel_type=rel_type,
        )
        require(bool(exists), f"Query-context topology edge missing: {source_label} -[{rel_type}]-> {target_label}")

    country_members = single_value(
        driver,
        """
        MATCH (i:Country) RETURN collect(DISTINCT i.uri) AS uris
        """,
    )
    country_set = set(country_members or [])
    expected_country_members = {
        uri for _, uri in query_context["enum_members"].get("Country", [])
    }
    require(
        country_set == expected_country_members,
        "Country enum membership in testdb must match query context",
    )

    state_count = single_value(
        driver,
        """
        MATCH (i:CountrySubdivision)
        WHERE i.uri STARTS WITH 'https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-'
        RETURN count(DISTINCT i) AS cnt
        """,
    )
    expected_state_members = {
        uri for _, uri in query_context["enum_members"].get("CountrySubdivision", [])
    }
    require(
        state_count == len(expected_state_members),
        "Country subdivision enum count in testdb must match query context",
    )

    ny_present = single_value(
        driver,
        "MATCH (:CountrySubdivision {uri: $uri}) RETURN count(*) > 0 AS ok",
        uri="https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NY",
    )
    nj_present = single_value(
        driver,
        "MATCH (:CountrySubdivision {uri: $uri}) RETURN count(*) > 0 AS ok",
        uri="https://www.omg.org/spec/LCC/Countries/Regions/ISO3166-2-SubdivisionCodes-US/US-NJ",
    )
    require(bool(ny_present), "Country subdivision enum must include New York")
    require(bool(nj_present), "Country subdivision enum must include New Jersey")

    orphan_classes = single_value(
        driver,
        "MATCH (n) WHERE 'owl__Class' IN labels(n) RETURN count(n) AS cnt",
    )
    require(orphan_classes == 0, "Dataset testdb must not contain owl__Class nodes")
    ontology_rels = single_value(
        driver,
        "MATCH ()-[r]->() WHERE type(r) IN ['rdf__type', 'rdfs__subClassOf'] RETURN count(r) AS cnt",
    )
    require(ontology_rels == 0, "Dataset testdb must not contain ontology relationships")

    instance_count = single_value(
        driver,
        "MATCH (:USPostalAddress {uri: 'urn:test:address:1'}) RETURN count(*) AS cnt",
    )
    require(instance_count == 1, "Sample US postal address instance must exist in testdb")
    parcel_chain_ok = single_value(
        driver,
        """
        MATCH (:GeoJSONFeatureCollection {uri:'urn:test:collection:1'})-[:hasFeature]->
              (:GeoJSONFeature {uri:'urn:test:feature:1'})-[:representsParcel]->
              (:Parcel {uri:'urn:test:parcel:1'})-[:hasParcelGeometry]->
              (:PolygonGeometry {uri:'urn:test:geometry:1'})-[:hasBoundaryVertex]->
              (:BoundaryVertex)
        RETURN count(*) >= 2 AS ok
        """,
    )
    require(bool(parcel_chain_ok), "Sample parcel instance graph must cover collection, feature, parcel, geometry, and boundary vertices")

    return {
        "test_db": TEST_DB_NAME,
        "staging_db": STAGING_DB_NAME,
        "constraints_applied": len(parse_constraints_file(CONSTRAINT_PATH)),
        "country_enum_count": len(country_set),
        "us_state_count": state_count,
        "address_relationships": sorted(outgoing_set),
        "orphan_class_count": orphan_classes,
        "pydantic_fields": sorted(model_fields),
        "query_context_required_properties": sorted(expected_required),
        "constraint_required_properties": sorted(constraint_required),
        "major_constraint_labels": sorted(required_constraints.keys()),
    }


def main() -> int:
    config = get_neo4j_config()
    driver = GraphDatabase.driver(config.uri, auth=(config.username, config.password))
    try:
        recreate_test_database(driver, TEST_DB_NAME)
        query_context = parse_query_context(QUERY_CONTEXT_PATH)
        apply_constraints(driver, TEST_DB_NAME, CONSTRAINT_PATH)
        load_enum_reference_data(driver, query_context)
        load_sample_instance_data(driver)
        summary = validate_testdb(driver)
        print("Parcel schema dataset smoke test passed.")
        for key, value in summary.items():
            print(f"{key}: {value}")
        return 0
    finally:
        driver.close()


if __name__ == "__main__":
    raise SystemExit(main())
