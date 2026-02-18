import os
from dataclasses import dataclass
from typing import Optional
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI
from neo4j_onto2ai_toolset.onto2ai_logger_config import *
from neo4j_onto2ai_toolset.onto2ai_utility import Neo4jDatabase

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
GPT_MODEL_NAME = os.getenv("GPT_MODEL_NAME")  # Backward-compatible alias
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


def _resolve_openai_model_name() -> str:
    """
    Resolve the OpenAI model used by internal LangChain flows.

    Priority:
    1. GPT_MODEL_NAME (legacy, OpenAI-specific)
    2. LLM_MODEL_NAME (canonical cross-component variable)
    3. gpt-5.2 (safe default)
    """
    candidate = GPT_MODEL_NAME or LLM_MODEL_NAME
    if not candidate:
        return "gpt-5.2"

    # ChatOpenAI cannot load Gemini IDs; keep OpenAI model resolution explicit.
    if candidate.lower().startswith("gemini"):
        logger.warning(
            "LLM_MODEL_NAME points to a Gemini model, but internal LangChain "
            "flows require an OpenAI ChatOpenAI model. Falling back to gpt-5.2."
        )
        return "gpt-5.2"
    return candidate

def get_llm():
    """Lazy initialization of the LLM."""
    global _llm
    if _llm is None:
        model_name = _resolve_openai_model_name()
        logger.info(f"Initializing OpenAI LLM for internal flows: {model_name}")
        _llm = ChatOpenAI(model=model_name)
    return _llm

# Graph Database Config
_graphdb = None

def get_graphdb():
    """Lazy initialization of the Neo4jGraph."""
    global _graphdb
    if _graphdb is None:
        logger.info(f"Initializing Neo4jGraph for database: {neo4j_model.database}")
        from langchain_neo4j import Neo4jGraph
        _graphdb = Neo4jGraph(
            url=neo4j_model.url,
            username=neo4j_model.username,
            password=neo4j_model.password,
            database=neo4j_model.database,
            enhanced_schema=True
        )
    return _graphdb

# Cleanup logic for clean shutdown
import atexit

def cleanup():
    """Close global Neo4j connections during shutdown."""
    if semanticdb:
        try:
            logger.info("Closing semanticdb connection...")
            semanticdb.close()
        except:
            pass
    if _graphdb:
        try:
            logger.info("Closing graphdb connection...")
            # Neo4jGraph doesn't have a direct close, but it has a driver
            if hasattr(_graphdb, "_driver"):
                _graphdb._driver.close()
        except:
            pass

atexit.register(cleanup)


