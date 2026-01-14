import os
from dataclasses import dataclass
from typing import Optional
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j_onto2ai_toolset.onto2ai_logger_config import *
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import Neo4jDatabase

GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME")
GPT_REASONING_EFFORT = os.getenv("GPT_REASONING_EFFORT")


ONTOLOGY_DOMAIN = os.getenv("ONTOLOGY_DOMAIN")
ONTOLOGY_NAMESPACE = os.getenv("ONTOLOGY_NAMESPACE")
ONTOLOGY_AUTHOR = os.getenv("ONTOLOGY_AUTHOR")

@dataclass(frozen=True)
class Neo4jModelConfig:
    url: str
    username: str
    password: str
    database: str

def get_neo4j_model_config() -> Neo4jModelConfig:
    """
    Resolve Neo4j MODEL configuration from environment variables.
    Fail fast if required values are missing.
    """
    url = os.getenv("NEO4J_MODEL_DB_URL")
    username = os.getenv("NEO4J_MODEL_DB_USERNAME")
    password = os.getenv("NEO4J_MODEL_DB_PASSWORD")
    database = os.getenv("NEO4J_MODEL_DB_NAME")

    if not url:
        raise ValueError("NEO4J_MODEL_DB_URL is not set")
    if not username:
        raise ValueError("NEO4J_MODEL_DB_USERNAME is not set")
    if not password:
        raise ValueError("NEO4J_MODEL_DB_PASSWORD is not set")
    if not database:
        raise ValueError("NEO4J_MODEL_DB_NAME is not set")

    logger.info(f"NEO4J_MODEL_URL: {url}")
    logger.info(f"NEO4J_MODEL_USERNAME: {username}")
    logger.info(f"NEO4J_MODEL_DB_NAME: {database}")

    return Neo4jModelConfig(url=url, username=username, password=password, database=database)

neo4j_model = get_neo4j_model_config()

# Semantic Data Config
auth_data = {
    "uri": neo4j_model.url,
    "database": neo4j_model.database,
    "user": neo4j_model.username,
    "pwd": neo4j_model.password,
    }

semanticdb = Neo4jDatabase(neo4j_model.url, neo4j_model.username, neo4j_model.password, neo4j_model.database)

# LLM Model Config
llm = ChatOpenAI(model=GPT_MODEL_NAME)

# Graph Database Config
graphdb = Neo4jGraph(
    url=neo4j_model.url,
    username=neo4j_model.username,
    password=neo4j_model.password,
    database=neo4j_model.database,
    enhanced_schema=True
)



