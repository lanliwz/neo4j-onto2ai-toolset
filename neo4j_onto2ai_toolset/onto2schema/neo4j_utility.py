from neo4j import GraphDatabase
import time
from neo4j_onto2ai_toolset.onto2schema.cypher_statement.cypher_for_modeling import *
from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import *
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger as ontoToollogger
import logging
ontoToollogger = logging.getLogger("onto2ai-toolset")
# The SematicGraphDB class is used to interact with a Neo4j database.
# It provides methods to create nodes, relationships, and execute arbitrary Cypher queries.
class Neo4jDatabase:
    # Initialize the FinGraphDB with the connection details to the Neo4j database.
    def __init__(self, uri, user, password, database_name):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), database=database_name)
        self._database_name = database_name

    # Close the connection to the Neo4j database.
    def close(self):
        self._driver.close()

    # Create a node with the given label and properties.
    def create_node(self, label, properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node, label, properties)

    # Execute an arbitrary Cypher query with structured logging.
    def execute_cypher(self, query, *, name: str | None = None):
        """Execute a Cypher statement with structured logging.

        Args:
            query: Cypher statement text
            name: Optional logical name for the statement (useful when calling many statements)
        """
        stmt_name = name or "cypher"
        q_preview = (query or "").replace("\n", " ").strip()
        if len(q_preview) > 200:
            q_preview = q_preview[:200] + "..."

        ontoToollogger.info(
            f"{stmt_name} execution started - {query}",
            extra={
                "op": stmt_name,
                "database": getattr(self, "_database_name", None),
                "query_preview": q_preview,
            },
        )

        start = time.time()
        try:
            with self._driver.session() as session:
                session.execute_write(self._execute_cypher, query)
        except Exception as e:
            elapsed_ms = int((time.time() - start) * 1000)
            ontoToollogger.exception(
                f"{stmt_name} execution failed",
                extra={
                    "op": stmt_name,
                    "database": getattr(self, "_database_name", None),
                    "elapsed_ms": elapsed_ms,
                    "query_preview": q_preview,
                },
            )
            raise
        else:
            elapsed_ms = int((time.time() - start) * 1000)
            ontoToollogger.info(
                f"{stmt_name} execution finished",
                extra={
                    "op": stmt_name,
                    "database": getattr(self, "_database_name", None),
                    "elapsed_ms": elapsed_ms,
                },
            )

    # read graph data
    #
    def get_node2node_relationship(self,label=None):
        with self._driver.session() as session:
            query = query_cls2cls_relationship(label)
            ontoToollogger.debug(query)
            result = session.execute_read(self._get_dataset,query)
            ontoToollogger.debug(result)
            return [f"(:{record['start_node']})-[:{record['relationship']}]->(:{record['end_node']})" for record in result]

    def get_node_dataproperty(self, label=None):
        with self._driver.session() as session:
            result = session.execute_read(self._get_dataset, query_dataproperty(label))
            return [f"(:{record['start_node']}) nodes have data property {record['relationship']}" for record in
                    result]

    def get_nodes(self, label=None):
        with self._driver.session() as session:
            ontoToollogger.debug(query_start_nodes(label))
            result = session.execute_read(self._get_dataset,query_start_nodes(label))
            ontoToollogger.debug(result)
            return [f"(:{record['start_node']}) nodes have annotation properties {record['annotation_properties']}"
                    for record in result
                    if record['start_node'] is not None]

    def get_end_nodes(self,label=None):
        with self._driver.session() as session:
            result = session.execute_read(self._get_dataset, query_end_nodes(label))
            return [f"(:{record['end_node']}) nodes have annotation properties {record['annotation_properties']}"
                    for record in result
                    if record['end_node'] is not None]

    def get_relationships(self,label=None):
        with (self._driver.session() as session):
            result = session.execute_read(self._get_dataset, query_relationships(label))
            return [f"[:{record['relationship']}] relationship has annotation properties  {record['annotation_properties']}" for record in result]

    @staticmethod
    def _get_dataset(tx,query):
        result = tx.run(query)
        return [record.data() for record in result]


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


def get_schema(start_node:str, db : Neo4jDatabase):
    schema = ("\n".join(db.get_node2node_relationship(start_node)) + '\n'
              + "\n".join(db.get_node_dataproperty(start_node)) + '\n'
              + "\n".join(db.get_end_nodes(start_node)) + '\n'
              + "\n".join(db.get_nodes(start_node)) + '\n'
              + "\n".join(db.get_relationships(start_node)) + '\n'
              )

    ontoToollogger.debug(schema)
    return schema

def get_full_schema(db : Neo4jDatabase):
    nodes = "\n".join(db.get_nodes())
    relationships = "\n".join(db.get_relationships())
    node2node_rels = "\n".join(db.get_node2node_relationship())
    node_dataprops = "\n".join(db.get_node_dataproperty())
    schema = (
        f"Node Labels: \n{nodes} \n"
        f"Relationships: \n{node2node_rels} \n"
        f"Relationship types: \n{relationships} \n"
        f"Node Properties: \n{node_dataprops} \n"

    )
    ontoToollogger.debug(schema)
    return schema

def get_node4schema(start_node:str, db : Neo4jDatabase):
    schema = (
              "\n".join(db.get_nodes(start_node)) + '\n'
              )

    return schema

