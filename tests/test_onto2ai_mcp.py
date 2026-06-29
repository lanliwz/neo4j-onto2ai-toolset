import unittest

from neo4j_onto2ai_toolset.onto2ai_mcp import (
    extract_domain_subset,
    MATERIALIZED_SCHEMA_OUTGOING_QUERY,
    MATERIALIZED_SCHEMA_QUERY,
    preview_concept_neighborhood,
    search_ontology_concepts,
)


class MaterializedSchemaQueryTests(unittest.TestCase):
    def test_materialized_schema_query_includes_modeller_incoming_branch(self):
        self.assertIn(
            "Incoming relationships from other classes to the requested class",
            MATERIALIZED_SCHEMA_QUERY,
        )
        self.assertIn("MATCH (source:owl__Class)-[r]->(c)", MATERIALIZED_SCHEMA_QUERY)
        self.assertIn('type(r) <> "rdfs__subClassOf"', MATERIALIZED_SCHEMA_QUERY)

    def test_outgoing_query_remains_generation_safe(self):
        self.assertNotIn(
            "Incoming relationships from other classes to the requested class",
            MATERIALIZED_SCHEMA_OUTGOING_QUERY,
        )
        self.assertNotIn(
            "MATCH (source:owl__Class)-[r]->(c)",
            MATERIALIZED_SCHEMA_OUTGOING_QUERY,
        )

    def test_source_ontology_mcp_tools_are_registered_callables(self):
        self.assertTrue(callable(search_ontology_concepts))
        self.assertTrue(callable(preview_concept_neighborhood))
        self.assertTrue(callable(extract_domain_subset))


if __name__ == "__main__":
    unittest.main()
