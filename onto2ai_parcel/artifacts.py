from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent

ONTOLOGY_PATH = PACKAGE_ROOT / "ontology" / "Parcel.rdf"
STAGING_PYDANTIC_PATH = PACKAGE_ROOT / "staging" / "pydantic_parcel_model.py"
STAGING_QUERY_CONTEXT_PATH = PACKAGE_ROOT / "staging" / "neo4j_query_context.md"
STAGING_CONSTRAINT_PATH = PACKAGE_ROOT / "staging" / "neo4j_constraint.cypher"
SMOKE_TEST_PATH = PACKAGE_ROOT / "staging" / "parcel_schema_smoke_test.py"
