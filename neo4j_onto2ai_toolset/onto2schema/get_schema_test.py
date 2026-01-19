from neo4j_onto2ai_toolset.schema_chatbot.onto2ai_utility import get_schema, Neo4jDatabase, get_full_schema
from neo4j_onto2ai_toolset.onto2ai_tool_config import *
neo4j_model = get_neo4j_model_config()
db = Neo4jDatabase(neo4j_model.url,
                   neo4j_model.username,
                   neo4j_model.password,
                   neo4j_model.database)


start_node ='graph object'
get_full_schema(db)