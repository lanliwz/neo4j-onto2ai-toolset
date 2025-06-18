import os
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j_onto2ai_toolset.logger_config import *

# llm = ChatOpenAI(model="gpt-o3-mini", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

neo4j_bolt_url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
neo4j_db_name = 'rdf'

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

