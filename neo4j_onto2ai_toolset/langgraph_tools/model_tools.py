import json
from neo4j_onto2ai_toolset.logger_config import logger
from langchain_core.tools import tool
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB, get_schema as get_model_from_db
from langchain_neo4j import Neo4jGraph
from dataclasses import dataclass

from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import (
    neo4j_bolt_url,
    username,
    password,
    neo4j_db_name)

semanticdb = SemanticGraphDB(neo4j_bolt_url, username, password, neo4j_db_name)

graphdb = Neo4jGraph(
    url=neo4j_bolt_url,
    username=username,
    password=password,
    database=neo4j_db_name,
    enhanced_schema=True
)

@dataclass
class ModelContextSchema:
    key_concept: str
    uri_domain: str
    runtime_username: str

@tool
def retrieve_stored_model(key_concept: str) -> str:
    """Display the stored model related to the key concept"""
    resp = get_model_from_db(key_concept, semanticdb)
    return resp

@tool
def display_model(content: str) -> str:
    """Display the stored model related to the key concept"""
    print(content)
    return content

@tool
def create_model(content: str) -> str:
    """Insert model node and relationship into model store"""
    statements = json.loads(content)
    records = []
    for stmt in statements:
        try:
            records.append(graphdb.query(stmt))
            logger.info(f'executed - {stmt}')
        except Exception as e:
            records.append(e)
            logger.error(f'error - {stmt}')
    return str(records)