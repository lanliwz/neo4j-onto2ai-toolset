import os
from dataclasses import dataclass
from typing import Optional
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j_onto2ai_toolset.onto2ai_logger_config import *
from neo4j_onto2ai_toolset.onto2ai_utility import Neo4jDatabase

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

# Default staging database name from environment
NEO4J_STAGING_DB_NAME = os.getenv("NEO4J_STAGING_DB_NAME", "stagingdb")

def get_staging_db(staging_db_name: str = None) -> Neo4jDatabase:
    """Create a Neo4jDatabase connection to the staging database.
    
    Args:
        staging_db_name: Target database name. Defaults to NEO4J_STAGING_DB_NAME env var.
    
    Returns:
        Neo4jDatabase instance connected to the staging database.
    """
    db_name = staging_db_name or NEO4J_STAGING_DB_NAME
    logger.info(f"Creating staging database connection to: {db_name}")
    return Neo4jDatabase(
        neo4j_model.url,
        neo4j_model.username,
        neo4j_model.password,
        db_name
    )

# LLM Model Config
_llm = None

def get_llm():
    """Lazy initialization of the LLM."""
    global _llm
    if _llm is None:
        logger.info(f"Initializing LLM: {GPT_MODEL_NAME}")
        _llm = ChatOpenAI(model=GPT_MODEL_NAME)
    return _llm

# Graph Database Config
graphdb = Neo4jGraph(
    url=neo4j_model.url,
    username=neo4j_model.username,
    password=neo4j_model.password,
    database=neo4j_model.database,
    enhanced_schema=True
)



