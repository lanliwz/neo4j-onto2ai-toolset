from neo4j_onto2ai_toolset.onto2ai_tool_config import get_neo4j_model_config
from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import *
from neo4j_onto2ai_toolset.onto2ai_utility import Neo4jDatabase

def reset_neo4j_db():
    neo4j_model_db_config = get_neo4j_model_config()

    # Operational Neo4j property graph
    # Operational Neo4j property graph before loading new ontology
    db = Neo4jDatabase(
        neo4j_model_db_config.url,
        neo4j_model_db_config.username,
        neo4j_model_db_config.password,
        neo4j_model_db_config.database,
    )
    db.execute_cypher(del_all_relationship, name="del_all_relationship")
    db.execute_cypher(del_all_node, name="del_all_node")
    db.close()

