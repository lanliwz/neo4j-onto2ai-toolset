import unittest

from neo4j_onto2ai_toolset.onto2ai_mcp import (
    MATERIALIZED_SCHEMA_OUTGOING_QUERY,
    MATERIALIZED_SCHEMA_QUERY,
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


if __name__ == "__main__":
    unittest.main()
