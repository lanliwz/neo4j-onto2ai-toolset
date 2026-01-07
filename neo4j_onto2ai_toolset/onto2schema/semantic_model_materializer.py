from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import *
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB


def materialize_property_graph_model(db: SemanticGraphDB):
    """
    Materialize an operational Neo4j property-graph model from OWL/RDF structures
    loaded into Neo4j (restrictions, domain/range, dataranges, unionOf/oneOf, XSD datatypes, etc.).
    """
    # restrictions + cardinality
    db.execute_cypher(crt_rel__restrict_cardinality, name="crt_rel__restrict_cardinality")

    db.execute_cypher(domain_range_1, name="domain_range_1")
    db.execute_cypher(domain_range_2, name="domain_range_2")

    db.execute_cypher(data_property_without_range, name="data_property_without_range")
    db.execute_cypher(object_property_without_range, name="object_property_without_range")


    db.execute_cypher(domain_onProperty, name="domain_onProperty")
    db.execute_cypher(range_onProperty_object, name="range_onProperty_object")
    db.execute_cypher(range_onProperty_datatype, name="range_onProperty_datatype")
    db.execute_cypher(range_onProperty_datarange, name="range_onProperty_datarange")
    db.execute_cypher(xsd_datatypes, name="xsd_datatypes")
    db.execute_cypher(union_of_datatype, name="union_of_datatype")
    db.execute_cypher(union_of_class, name="union_of_class")

    db.execute_cypher(oneOf, name="oneOf")

    # clean up duplicated edge
    db.execute_cypher(del_dup_rels, name="del_dup_rels")
    db.execute_cypher(rm_redounded_label, name="rm_redounded_label")