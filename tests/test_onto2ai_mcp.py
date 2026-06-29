import unittest

from neo4j_onto2ai_toolset.onto2ai_mcp import (
    extract_domain_subset,
    MATERIALIZED_SCHEMA_OUTGOING_QUERY,
    MATERIALIZED_SCHEMA_QUERY,
    _neo4j_label_key_for_uri,
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

    def test_named_individual_label_key_uses_canonical_prefixes(self):
        self.assertEqual(
            _neo4j_label_key_for_uri(
                "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/Country"
            ),
            "l_cr__Country",
        )
        self.assertEqual(
            _neo4j_label_key_for_uri(
                "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/SecondaryUnitDesignator"
            ),
            "fnd_plc_adr__SecondaryUnitDesignator",
        )

    def test_enum_extraction_supports_rdflib_neo4j_label_typed_individuals(self):
        import inspect
        import neo4j_onto2ai_toolset.onto2ai_mcp as onto2ai_mcp

        extract_source = inspect.getsource(onto2ai_mcp.extract_data_model)
        constraint_source = inspect.getsource(onto2ai_mcp.generate_neo4j_schema_constraint)

        self.assertIn("enumLabel IN labels(i)", extract_source)
        self.assertIn("class_keys", extract_source)
        self.assertIn("enumLabel IN labels(i)", constraint_source)
        self.assertIn("class_keys", constraint_source)


if __name__ == "__main__":
    unittest.main()
