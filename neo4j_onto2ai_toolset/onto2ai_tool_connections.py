import os
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j_onto2ai_toolset.onto2ai_logger_config import *


# llm = ChatOpenAI(model="gpt-o3-mini", temperature=0)
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME")
llm = ChatOpenAI(model=GPT_MODEL_NAME,reasoning_effort="medium")

neo4j_bolt_url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
neo4j_db_name = os.getenv('NEO4J_RDF_DB_NAME')


graphdb = Neo4jGraph(
    url=neo4j_bolt_url,
    username=username,
    password=password,
    database=neo4j_db_name,
    enhanced_schema=True
)

auth_data = {
    'uri': neo4j_bolt_url,
    'database': neo4j_db_name,
    'user': username,
    'pwd': password
    }

