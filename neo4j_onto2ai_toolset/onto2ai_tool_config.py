import os
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j_onto2ai_toolset.onto2ai_logger_config import *


GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME")
GPT_REASONING_EFFORT = os.getenv("GPT_REASONING_EFFORT")


neo4j_bolt_url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
neo4j_db_name = os.getenv('NEO4J_RDF_DB_NAME')

# Semantic Data Config
auth_data = {
    'uri': neo4j_bolt_url,
    'database': neo4j_db_name,
    'user': username,
    'pwd': password
    }

# LLM Model Config
llm = ChatOpenAI(model=GPT_MODEL_NAME,reasoning_effort=GPT_REASONING_EFFORT)

# Graph Database Config
graphdb = Neo4jGraph(
    url=neo4j_bolt_url,
    username=username,
    password=password,
    database=neo4j_db_name,
    enhanced_schema=True
)



