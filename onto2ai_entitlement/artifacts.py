from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent

ONTOLOGY_PATH = PACKAGE_ROOT / "ontology" / "Onto2AIEntitlement.rdf"
STAGING_MODEL_PATH = PACKAGE_ROOT / "staging" / "full_schema_model.json"
STAGING_PYDANTIC_PATH = PACKAGE_ROOT / "staging" / "pydantic_schema_model.py"
STAGING_QUERY_CONTEXT_PATH = PACKAGE_ROOT / "staging" / "neo4j_query_context.md"
STAGING_CONSTRAINT_PATH = PACKAGE_ROOT / "staging" / "neo4j_constraint.cypher"
SMOKE_TEST_PATH = PACKAGE_ROOT / "staging" / "schema_to_data_flow_smoke_test.py"
