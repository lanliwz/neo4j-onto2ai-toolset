from neo4j import GraphDatabase

# The FinGraphDB class is used to interact with a Neo4j database.
# It provides methods to create nodes, relationships, and execute arbitrary Cypher queries.
class FinGraphDB:
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
    def create_object(self, query):
        with self._driver.session() as session:
            session.execute_write(self._create_object, query)

    # Helper method to create a node.
    @staticmethod
    def _create_node(tx, label, properties):
        query = f"CREATE (a:{label} {{properties}})"
        tx.run(query, properties=properties)

    # Helper method to execute a Cypher query.
    @staticmethod
    def _create_object(tx, query):
        tx.run(query)

    # Create a node and a relationship between it and another node.
    def create_node_and_relationship(self, node1_label, node1_properties, relationship_type, node2_label,
                                     node2_properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node_rel, node1_label, node1_properties, relationship_type, node2_label,
                                  node2_properties)

    # Create a BILL_FOR relationship.
    def create_BILL_FOR_rel(self):
        with self._driver.session() as session:
            session.execute_write(_create_BILL_FOR_rel)

    # Helper method to create a node and a relationship.
    @staticmethod
    def _create_node_rel(tx, node1_label, node1_properties, relationship_type, node2_label, node2_properties):
        query = (
            f"CREATE (a:{node1_label} {{properties}}) "
            f"-[:{relationship_type}]-> "
            f"(b:{node2_label} {{properties}})"
        )
        tx.run(query, properties=node1_properties)
        tx.run(query, properties=node2_properties)

# Helper function to create a BILL_FOR relationship.
def _create_BILL_FOR_rel(tx):
    query = (
        "MATCH (n:JerseyCityTaxBilling),(a:Account)"
        "WHERE a.Account=n.Account and not exists((n)-[:BILL_FOR]->(a))"
        "CREATE (n)-[r:BILL_FOR]->(a)"
    )