from neo4j import GraphDatabase
import cypher_statement.onto2schema_util


# The SematicGraphDB class is used to interact with a Neo4j database.
# It provides methods to create nodes, relationships, and execute arbitrary Cypher queries.
class SemanticGraphDB:
    # Initialize the FinGraphDB with the connection details to the Neo4j database.
    def __init__(self, uri, user, password, database_name):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), database=database_name)

    # Close the connection to the Neo4j database.
    def close(self):
        self._driver.close()

    # Create a node with the given label and properties.
    def create_node(self, label, properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node, label, properties)

    # Execute an arbitrary Cypher query.
    def execute_cypher(self, query):
        with self._driver.session() as session:
            session.execute_write(self._execute_cypher, query)

    # Helper method to create a node.
    @staticmethod
    def _create_node(tx, label, properties):
        query = f"CREATE (a:{label} {{properties}})"
        tx.run(query, properties=properties)

    # Helper method to execute a Cypher query.
    @staticmethod
    def _execute_cypher(tx, query):
        tx.run(query)

    # Create a node and a relationship between it and another node.
    def create_node_and_relationship(self, node1_label, node1_properties, relationship_type, node2_label,
                                     node2_properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node_rel, node1_label, node1_properties, relationship_type, node2_label,
                                  node2_properties)

    # Helper method to create a node and a relationship.
    @staticmethod
    def _create_node_rel(tx, node1_label, node1_properties, relationship_type, node2_label, node2_properties):
        query = (
            f"CREATE (a:{node1_label} {{properties1}}) "
            f"-[:{relationship_type}]-> "
            f"(b:{node2_label} {{properties2}})"
        )
        tx.run(query, properties1=node1_properties, properties2=node2_properties)

def clean_up_neo4j_graph(db:SemanticGraphDB):
    db.execute_cypher(cypher_statement.onto2schema_util.del_all_relationship)
    db.execute_cypher(cypher_statement.onto2schema_util.del_all_node)


def rdf_to_neo4j_graph(db : SemanticGraphDB):

    db.execute_cypher(cypher_statement.onto2schema_util.crt_rel__restrict_cardinality_1)
    db.execute_cypher(cypher_statement.onto2schema_util.crt_rel__restrict_cardinality_2)

    db.execute_cypher(cypher_statement.onto2schema_util.domain_range_1)
    db.execute_cypher(cypher_statement.onto2schema_util.domain_range_2)

    db.execute_cypher(cypher_statement.onto2schema_util.data_property_without_range)
    db.execute_cypher(cypher_statement.onto2schema_util.object_property_without_range)

    db.execute_cypher(cypher_statement.onto2schema_util.allValueFrom)
    db.execute_cypher(cypher_statement.onto2schema_util.allValueFrom_01)
    db.execute_cypher(cypher_statement.onto2schema_util.someValueFrom)
    db.execute_cypher(cypher_statement.onto2schema_util.someValueFrom_01)


    db.execute_cypher(cypher_statement.onto2schema_util.domain_onProperty)
    db.execute_cypher(cypher_statement.onto2schema_util.range_onProperty_object)
    db.execute_cypher(cypher_statement.onto2schema_util.range_onProperty_datatype)
    db.execute_cypher(cypher_statement.onto2schema_util.range_onProperty_datarange)
    db.execute_cypher(cypher_statement.onto2schema_util.xsd_datatypes)
    db.execute_cypher(cypher_statement.onto2schema_util.union_of_datatype)
    db.execute_cypher(cypher_statement.onto2schema_util.oneOf)

    # clean up duplicated edge
    db.execute_cypher(cypher_statement.onto2schema_util.del_dup_rels)
    db.execute_cypher(cypher_statement.onto2schema_util.rm_redounded_label)


