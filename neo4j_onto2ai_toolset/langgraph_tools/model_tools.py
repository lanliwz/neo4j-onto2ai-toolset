import json

from langgraph.runtime import get_runtime

from neo4j_onto2ai_toolset.onto2ai_tool_config import *
from langchain_core.tools import tool
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB, get_schema as get_model_from_db
from langchain_neo4j import Neo4jGraph
from dataclasses import dataclass

from neo4j_onto2ai_toolset.onto2ai_tool_config import (
    neo4j_bolt_url,
    username,
    password,
    neo4j_db_name,
    graphdb,
    semanticdb)


# Namespace: upe (short for UpUpEdu) → compact and unique to your org.
# Base: http://upupedu.com/ontology#
@dataclass
class ModelContextSchema():
    userid: str = ONTOLOGY_AUTHOR
    uri_domain: str = ONTOLOGY_DOMAIN
    namespace: str = ONTOLOGY_NAMESPACE




@tool
def retrieve_model(key_concept: str) -> str:
    """retrieve the stored model"""
    context = get_runtime(ModelContextSchema)
    logger.debug(f'retrieve_model tool is used. context - {context}')
    resp = get_model_from_db(key_concept, semanticdb)
    return resp

@tool
def display_model(content: str) -> str:
    """display model content"""
    context = get_runtime(ModelContextSchema)
    logger.debug(f'display_model tool is used. context - {context}')
    logger.info(content)
    return content

@tool
def modify_model(content: str) -> str:
    """
    Insert/update/delete model node and relationship in model store
    content should be in format of json array, wrap as a string
    """
    context = get_runtime(ModelContextSchema)
    logger.debug(f'modify_model tool is used. context - {context}')
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