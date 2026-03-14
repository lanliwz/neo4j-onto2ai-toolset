from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent

ONTOLOGY_PATH = PACKAGE_ROOT / "ontology" / "HousePlan.rdf"
STAGING_CONSTRAINT_PATH = PACKAGE_ROOT / "staging" / "neo4j_constraint.cypher"
GEOJSON_IMPORTER_PATH = PACKAGE_ROOT / "importers" / "geojson_import.py"
