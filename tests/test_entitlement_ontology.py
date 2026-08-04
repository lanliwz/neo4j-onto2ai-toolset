import json
import unittest
from pathlib import Path
from unittest.mock import patch

from rdflib import Graph, OWL, RDF, RDFS, URIRef

from neo4j_onto2ai_toolset.onto2ai_mcp import extract_data_model


ONTOLOGY_PATH = (
    Path(__file__).resolve().parents[1]
    / "resource"
    / "ontology"
    / "www_onto2ai-toolset_com"
    / "ontology"
    / "entitlement"
    / "Onto2AIEntitlement.rdf"
)
SCHEMA_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "onto2ai_entitlement"
    / "staging"
    / "full_schema_model.json"
)
CONSTRAINT_PATH = SCHEMA_MODEL_PATH.with_name("neo4j_constraint.cypher")
NS = "http://www.onto2ai-toolset.com/ontology/entitlement/Onto2AIEntitlement/"


class EntitlementOntologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph().parse(ONTOLOGY_PATH)

    def test_block_query_is_one_behavior_with_two_enum_types(self):
        block_query = URIRef(NS + "BlockQueryBehavior")

        self.assertIn((block_query, RDF.type, OWL.NamedIndividual), self.graph)
        self.assertIn((block_query, RDF.type, URIRef(NS + "DenyBehavior")), self.graph)
        self.assertIn((block_query, RDF.type, URIRef(NS + "FallbackBehavior")), self.graph)
        self.assertNotIn(
            (URIRef(NS + "BlockQueryDenyBehavior"), RDF.type, OWL.NamedIndividual),
            self.graph,
        )
        self.assertNotIn(
            (URIRef(NS + "BlockQueryFallbackBehavior"), RDF.type, OWL.NamedIndividual),
            self.graph,
        )

    def test_required_object_relationship_cardinalities_are_in_rdf(self):
        expected = {
            ("User", "hasUserType", OWL.qualifiedCardinality, 1),
            ("User", "isMemberOf", OWL.minQualifiedCardinality, 1),
            ("PolicyGroup", "includesPolicy", OWL.minQualifiedCardinality, 1),
            ("EntitlementRule", "hasPriority", OWL.qualifiedCardinality, 1),
            ("RowFilterRule", "targetsFilteredColumn", OWL.minQualifiedCardinality, 1),
            ("ColumnMaskRule", "targetsMaskedColumn", OWL.minQualifiedCardinality, 1),
            ("Column", "belongsToTable", OWL.qualifiedCardinality, 1),
            ("Table", "belongsToSchema", OWL.qualifiedCardinality, 1),
            ("Schema", "belongsToDatabase", OWL.qualifiedCardinality, 1),
            ("JdbcConnectionProfile", "connectsTo", OWL.qualifiedCardinality, 1),
        }

        actual = set()
        for class_uri, _, restriction in self.graph.triples((None, RDFS.subClassOf, None)):
            property_uri = self.graph.value(restriction, OWL.onProperty)
            if property_uri is None:
                continue
            for predicate in (OWL.qualifiedCardinality, OWL.minQualifiedCardinality):
                value = self.graph.value(restriction, predicate)
                if value is not None:
                    actual.add(
                        (
                            str(class_uri).removeprefix(NS),
                            str(property_uri).removeprefix(NS),
                            predicate,
                            int(value),
                        )
                    )

        self.assertTrue(expected.issubset(actual))

    def test_all_optional_single_relationships_have_max_one_restrictions(self):
        expected = {
            ("EntitlementRule", "hasValueSourceType"),
            ("RowFilterRule", "hasFilterAction"),
            ("RowFilterRule", "hasMatchMode"),
            ("RowFilterRule", "hasComparisonOperator"),
            ("RowFilterRule", "hasDenyBehavior"),
            ("ColumnMaskRule", "hasMaskAction"),
            ("ColumnMaskRule", "hasMaskingMethod"),
            ("ColumnMaskRule", "hasFallbackBehavior"),
            ("Column", "hasSensitivityClassification"),
        }

        actual = set()
        for class_uri, _, restriction in self.graph.triples((None, RDFS.subClassOf, None)):
            property_uri = self.graph.value(restriction, OWL.onProperty)
            max_value = self.graph.value(restriction, OWL.maxQualifiedCardinality)
            if property_uri is not None and max_value is not None and int(max_value) == 1:
                actual.add(
                    (
                        str(class_uri).removeprefix(NS),
                        str(property_uri).removeprefix(NS),
                    )
                )

        self.assertEqual(actual, expected)

    def test_only_intended_multivalue_datatype_properties_are_nonfunctional(self):
        datatype_properties = set(
            self.graph.subjects(RDF.type, OWL.DatatypeProperty)
        )
        functional_properties = set(
            self.graph.subjects(RDF.type, OWL.FunctionalProperty)
        )
        nonfunctional_names = {
            str(uri).removeprefix(NS)
            for uri in datatype_properties - functional_properties
        }

        self.assertEqual(
            nonfunctional_names,
            {"policyDescription", "policyGroupName", "policyName"},
        )

    def test_packaged_schema_model_preserves_ontology_contract(self):
        model = json.loads(SCHEMA_MODEL_PATH.read_text(encoding="utf-8"))
        nodes = model["nodes"]
        relationships = model["relationships"]
        node_labels = [node["label"] for node in nodes]

        self.assertEqual(model["metadata"]["named_individual_count"], 40)
        self.assertEqual(len(node_labels), len(set(node_labels)))
        self.assertEqual(
            {
                relationship["uri"]
                for relationship in relationships
                if relationship["type"] == "rdf__type"
            },
            {"http://www.w3.org/1999/02/22-rdf-syntax-ns#type"},
        )
        self.assertEqual(
            {
                prop["type"]
                for node in nodes
                for prop in node.get("properties", [])
            },
            {"boolean", "integer", "string"},
        )
        self.assertEqual(
            sum(
                prop.get("unique") is True
                for node in nodes
                for prop in node.get("properties", [])
            ),
            10,
        )

        constraints = CONSTRAINT_PATH.read_text(encoding="utf-8")
        self.assertEqual(constraints.count(" IS UNIQUE;"), 10)
        self.assertEqual(constraints.count(" IS NOT NULL;"), 10)

        relationship_cardinalities = {
            (
                relationship["start_node_label"],
                relationship["type"],
                relationship["end_node_label"],
            ): relationship["cardinality"]
            for relationship in relationships
        }
        self.assertEqual(
            relationship_cardinalities[
                ("policy group", "includesPolicy", "policy")
            ],
            "1..*",
        )
        self.assertEqual(
            relationship_cardinalities[
                ("jdbc connection profile", "connectsTo", "relational database")
            ],
            "1",
        )
        self.assertEqual(
            relationship_cardinalities[
                ("column mask rule", "hasFallbackBehavior", "fallback behavior")
            ],
            "0..1",
        )


class EntitlementExtractionTests(unittest.IsolatedAsyncioTestCase):
    async def test_explicit_enum_membership_uses_canonical_rdf_type_uri(self):
        canonical_type_uri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

        class FakeDatabase:
            def execute_cypher(self, query, params=None, name=None):
                if name == "internal_extract_data_model_seed_classes":
                    return [
                        {
                            "SourceClassLabel": "behavior",
                            "SourceClassURI": NS + "Behavior",
                            "SourceClassDef": "An enum behavior.",
                        }
                    ]
                if name == "internal_extract_data_model":
                    return []
                if name == "internal_extract_data_model_enum_scope_classes":
                    return [{"ClassURI": NS + "Behavior"}]
                if name == "internal_extract_data_model_named_individuals":
                    if canonical_type_uri not in query:
                        raise AssertionError("rdf:type URI is not canonical")
                    return [
                        {
                            "IndividualLabel": "block query",
                            "IndividualURI": NS + "BlockQueryBehavior",
                            "IndividualDef": "Blocks the query.",
                            "ClassLabel": "behavior",
                            "ClassURI": NS + "Behavior",
                            "TypeRelURI": canonical_type_uri,
                        }
                    ]
                if name == "internal_extract_data_model_subclass_rels":
                    return []
                raise AssertionError(f"Unexpected query: {name}")

            def close(self):
                return None

        fake_database = FakeDatabase()
        with patch(
            "neo4j_onto2ai_toolset.onto2ai_tool_config.get_staging_db",
            return_value=fake_database,
        ):
            model = await extract_data_model(
                class_names=["behavior"],
                database="stagingdb",
            )

        rdf_type_relationships = [
            relationship
            for relationship in model.relationships
            if relationship.type == "rdf__type"
        ]
        self.assertEqual(len(rdf_type_relationships), 1)
        self.assertEqual(rdf_type_relationships[0].uri, canonical_type_uri)


if __name__ == "__main__":
    unittest.main()
