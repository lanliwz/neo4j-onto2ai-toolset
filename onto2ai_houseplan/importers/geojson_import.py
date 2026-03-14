#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from hashlib import sha1
from pathlib import Path
from typing import Any

from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db


HOUSEPLAN_NS = "http://www.onto2ai-toolset.com/ontology/houseplan/HousePlan/#"


CLASS_URIS = {
    "GeoJSONFeatureCollection": f"{HOUSEPLAN_NS}GeoJSONFeatureCollection",
    "GeoJSONFeature": f"{HOUSEPLAN_NS}GeoJSONFeature",
    "Parcel": f"{HOUSEPLAN_NS}Parcel",
    "USPostalAddress": f"{HOUSEPLAN_NS}USPostalAddress",
    "PolygonGeometry": f"{HOUSEPLAN_NS}PolygonGeometry",
    "BoundaryVertex": f"{HOUSEPLAN_NS}BoundaryVertex",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import houseplan parcel GeoJSON into stagingdb.")
    parser.add_argument("geojson_path", help="Path to GeoJSON file")
    parser.add_argument("--database", default="stagingdb", help="Target Neo4j database")
    return parser.parse_args()


def load_geojson(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def stable_id(*parts: str) -> str:
    return sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]


def scalar(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, separators=(",", ":"))


def upsert_feature_collection(db, file_path: Path, feature_count: int) -> str:
    collection_id = stable_id(str(file_path.resolve()))
    query = """
    MERGE (fc:GeoJSONFeatureCollection:owl__NamedIndividual {featureCollectionId: $feature_collection_id})
    SET fc.uri = $uri,
        fc.rdfs__label = $label,
        fc.filePath = $file_path,
        fc.featureCount = $feature_count,
        fc.sourceFormat = 'GeoJSON',
        fc.sourceFileName = $file_name
    WITH fc
    MATCH (cls:owl__Class {uri: $class_uri})
    MERGE (fc)-[:rdf__type {materialized: true}]->(cls)
    """
    db.execute_cypher(
        query,
        params={
            "feature_collection_id": collection_id,
            "uri": f"{HOUSEPLAN_NS}collection/{collection_id}",
            "label": file_path.stem,
            "file_path": str(file_path),
            "file_name": file_path.name,
            "feature_count": feature_count,
            "class_uri": CLASS_URIS["GeoJSONFeatureCollection"],
        },
        name="upsert_feature_collection",
    )
    return collection_id


def upsert_feature_graph(db, feature_collection_id: str, feature: dict[str, Any], index: int) -> None:
    properties = feature.get("properties") or {}
    geometry = feature.get("geometry") or {}
    coordinates = geometry.get("coordinates") or []
    if geometry.get("type") != "Polygon":
        raise ValueError(f"Only Polygon geometries are currently supported, got {geometry.get('type')!r}")

    object_id = str(properties.get("OBJECTID") or index)
    parcel_id = str(properties.get("PARCELID") or stable_id("parcel", object_id))
    feature_id = f"feature-{object_id}"
    geometry_id = f"geometry-{parcel_id}"
    address_id = f"address-{parcel_id}"

    parcel_area_acres = _to_float(properties.get("ACREAGE"))
    deeded_area_acres = _to_float(properties.get("ACREDEED"))
    parcel_area_sqft = round(parcel_area_acres * 43560, 3) if parcel_area_acres is not None else None

    query = """
    MATCH (fc:GeoJSONFeatureCollection {featureCollectionId: $feature_collection_id})
    MATCH (feature_cls:owl__Class {uri: $feature_class_uri})
    MATCH (parcel_cls:owl__Class {uri: $parcel_class_uri})
    MATCH (address_cls:owl__Class {uri: $address_class_uri})
    MATCH (geometry_cls:owl__Class {uri: $geometry_class_uri})

    MERGE (f:GeoJSONFeature:owl__NamedIndividual {featureId: $feature_id})
    SET f.uri = $feature_uri,
        f.rdfs__label = $feature_label,
        f.sourceObjectId = $source_object_id,
        f.sourceCreatedAtText = $source_created_at_text,
        f.sourceLastUpdatedAtText = $source_last_updated_at_text,
        f.sourceFeatureType = 'Feature'
    MERGE (fc)-[:hasFeature {materialized: true, uri: $has_feature_uri}]->(f)
    MERGE (f)-[:rdf__type {materialized: true}]->(feature_cls)

    MERGE (p:Parcel:owl__NamedIndividual {parcelId: $parcel_id})
    SET p.uri = $parcel_uri,
        p.rdfs__label = $parcel_label,
        p.parcelNumber = $parcel_number,
        p.taxMapNumber = $tax_map_number,
        p.taxDistrictCode = $tax_district_code,
        p.taxSectionCode = $tax_section_code,
        p.blockNumber = $block_number,
        p.lotNumber = $lot_number,
        p.municipalityName = $municipality_name,
        p.landUseText = $land_use_text,
        p.parcelStatusText = $parcel_status_text,
        p.titleFlagText = $title_flag_text,
        p.overlapFlagText = $overlap_flag_text,
        p.parcelAreaAcres = $parcel_area_acres,
        p.deededAreaAcres = $deeded_area_acres,
        p.parcelAreaSquareFeet = $parcel_area_square_feet,
        p.sourceParcelId = $source_parcel_id
    MERGE (f)-[:representsParcel {materialized: true, uri: $represents_parcel_uri}]->(p)
    MERGE (p)-[:rdf__type {materialized: true}]->(parcel_cls)

    MERGE (a:USPostalAddress:owl__NamedIndividual {addressId: $address_id})
    SET a.uri = $address_uri,
        a.rdfs__label = $address_label,
        a.streetAddressLine1 = $street_address_line1,
        a.cityName = $city_name,
        a.postalCode = $postal_code,
        a.fullAddressText = $full_address_text
    MERGE (p)-[:hasParcelAddress {materialized: true, uri: $has_parcel_address_uri}]->(a)
    MERGE (a)-[:rdf__type {materialized: true}]->(address_cls)

    MERGE (g:PolygonGeometry:owl__NamedIndividual {geometryId: $geometry_id})
    SET g.uri = $geometry_uri,
        g.rdfs__label = $geometry_label,
        g.geometryTypeName = $geometry_type_name,
        g.ringCount = $ring_count,
        g.coordinatesJson = $coordinates_json
    MERGE (f)-[:hasGeometry {materialized: true, uri: $has_geometry_uri}]->(g)
    MERGE (p)-[:hasParcelGeometry {materialized: true, uri: $has_parcel_geometry_uri}]->(g)
    MERGE (g)-[:rdf__type {materialized: true}]->(geometry_cls)
    """
    db.execute_cypher(
        query,
        params={
            "feature_collection_id": feature_collection_id,
            "feature_class_uri": CLASS_URIS["GeoJSONFeature"],
            "parcel_class_uri": CLASS_URIS["Parcel"],
            "address_class_uri": CLASS_URIS["USPostalAddress"],
            "geometry_class_uri": CLASS_URIS["PolygonGeometry"],
            "feature_id": feature_id,
            "feature_uri": f"{HOUSEPLAN_NS}feature/{feature_id}",
            "feature_label": f"parcel feature {object_id}",
            "source_object_id": object_id,
            "source_created_at_text": scalar(properties.get("CREATEDATE")),
            "source_last_updated_at_text": scalar(properties.get("LASTUPDATE")),
            "has_feature_uri": f"{HOUSEPLAN_NS}hasFeature",
            "parcel_id": parcel_id,
            "parcel_uri": f"{HOUSEPLAN_NS}parcel/{parcel_id}",
            "parcel_label": properties.get("FULLADDRESS") or f"parcel {parcel_id}",
            "parcel_number": scalar(properties.get("PARCELID")),
            "tax_map_number": "/".join(
                part for part in [
                    scalar(properties.get("DISTRICT")),
                    scalar(properties.get("SECTION")),
                    scalar(properties.get("BLOCK")),
                    scalar(properties.get("LOT")),
                ] if part
            ) or None,
            "tax_district_code": scalar(properties.get("DISTRICT")),
            "tax_section_code": scalar(properties.get("SECTION")),
            "block_number": scalar(properties.get("BLOCK")),
            "lot_number": scalar(properties.get("LOT")),
            "municipality_name": scalar(properties.get("MUNICIPALITY")),
            "land_use_text": scalar(properties.get("LANDUSE")),
            "parcel_status_text": scalar(properties.get("STATUS")),
            "title_flag_text": scalar(properties.get("TITLEFLAG")),
            "overlap_flag_text": scalar(properties.get("OVERLAP")),
            "parcel_area_acres": parcel_area_acres,
            "deeded_area_acres": deeded_area_acres,
            "parcel_area_square_feet": parcel_area_sqft,
            "source_parcel_id": scalar(properties.get("PARCELID")),
            "represents_parcel_uri": f"{HOUSEPLAN_NS}representsParcel",
            "address_id": address_id,
            "address_uri": f"{HOUSEPLAN_NS}address/{address_id}",
            "address_label": properties.get("FULLADDRESS") or f"address {address_id}",
            "street_address_line1": scalar(properties.get("FULLADDRESS")),
            "city_name": scalar(properties.get("MUNICIPALITY")),
            "postal_code": scalar(properties.get("ZIPCODE")),
            "full_address_text": scalar(properties.get("FULLADDRESS")),
            "has_parcel_address_uri": f"{HOUSEPLAN_NS}hasParcelAddress",
            "geometry_id": geometry_id,
            "geometry_uri": f"{HOUSEPLAN_NS}geometry/{geometry_id}",
            "geometry_label": f"parcel geometry {parcel_id}",
            "geometry_type_name": scalar(geometry.get("type")),
            "ring_count": len(coordinates),
            "coordinates_json": json.dumps(coordinates, separators=(",", ":")),
            "has_geometry_uri": f"{HOUSEPLAN_NS}hasGeometry",
            "has_parcel_geometry_uri": f"{HOUSEPLAN_NS}hasParcelGeometry",
        },
        name="upsert_feature_graph",
    )

    upsert_boundary_vertices(db, geometry_id=geometry_id, parcel_id=parcel_id, coordinates=coordinates)


def upsert_boundary_vertices(db, *, geometry_id: str, parcel_id: str, coordinates: list[Any]) -> None:
    vertex_class_uri = CLASS_URIS["BoundaryVertex"]
    query = """
    MATCH (g:PolygonGeometry {geometryId: $geometry_id})
    MATCH (vertex_cls:owl__Class {uri: $vertex_class_uri})
    MERGE (v:BoundaryVertex:owl__NamedIndividual {gpsCoordinateId: $gps_coordinate_id})
    SET v.uri = $vertex_uri,
        v.rdfs__label = $vertex_label,
        v.latitudeDecimalDegrees = $latitude,
        v.longitudeDecimalDegrees = $longitude,
        v.vertexOrder = $vertex_order
    MERGE (g)-[:hasBoundaryVertex {materialized: true, uri: $has_boundary_vertex_uri, vertexOrder: $vertex_order}]->(v)
    MERGE (v)-[:rdf__type {materialized: true}]->(vertex_cls)
    """
    vertex_order = 0
    for ring_index, ring in enumerate(coordinates):
        for point_index, point in enumerate(ring):
            if len(point) < 2:
                continue
            lon, lat = point[0], point[1]
            gps_coordinate_id = f"vertex-{parcel_id}-{ring_index}-{point_index}"
            db.execute_cypher(
                query,
                params={
                    "geometry_id": geometry_id,
                    "vertex_class_uri": vertex_class_uri,
                    "gps_coordinate_id": gps_coordinate_id,
                    "vertex_uri": f"{HOUSEPLAN_NS}vertex/{gps_coordinate_id}",
                    "vertex_label": f"boundary vertex {vertex_order}",
                    "latitude": _to_float(lat),
                    "longitude": _to_float(lon),
                    "vertex_order": vertex_order,
                    "has_boundary_vertex_uri": f"{HOUSEPLAN_NS}hasBoundaryVertex",
                },
                name="upsert_boundary_vertex",
            )
            vertex_order += 1


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def run_import(geojson_path: str | Path, database: str = "stagingdb") -> int:
    path = Path(geojson_path).expanduser()
    data = load_geojson(path)
    features = data.get("features") or []

    db = get_staging_db(database)
    try:
        feature_collection_id = upsert_feature_collection(db, path, len(features))
        for index, feature in enumerate(features, start=1):
            upsert_feature_graph(db, feature_collection_id, feature, index)
    finally:
        db.close()

    print(f"Imported {len(features)} feature(s) from {path} into {database}.")
    return 0


def main() -> int:
    args = parse_args()
    return run_import(args.geojson_path, database=args.database)


if __name__ == "__main__":
    raise SystemExit(main())
