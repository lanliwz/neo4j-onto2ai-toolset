import atexit
import os
from dataclasses import dataclass
from typing import Any

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


_neo4j_model_config: Neo4jModelConfig | None = None
_semanticdb: Neo4jDatabase | None = None
_llm = None
_graphdb = None


def get_neo4j_model_config() -> Neo4jModelConfig:
    """
    Resolve Neo4j MODEL configuration from environment variables.
    Fail fast only when a caller actually needs the configuration.
    """
    global _neo4j_model_config
    if _neo4j_model_config is not None:
        return _neo4j_model_config

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

    logger.info("NEO4J_MODEL_URL: %s", url)
    logger.info("NEO4J_MODEL_USERNAME: %s", username)
    logger.info("NEO4J_MODEL_DB_NAME: %s", database)

    _neo4j_model_config = Neo4jModelConfig(
        url=url,
        username=username,
        password=password,
        database=database,
    )
    return _neo4j_model_config


def get_auth_data() -> dict[str, str]:
    neo4j_model = get_neo4j_model_config()
    return {
        "uri": neo4j_model.url,
        "database": neo4j_model.database,
        "user": neo4j_model.username,
        "pwd": neo4j_model.password,
    }


def get_semanticdb() -> Neo4jDatabase:
    global _semanticdb
    if _semanticdb is None:
        neo4j_model = get_neo4j_model_config()
        _semanticdb = Neo4jDatabase(
            neo4j_model.url,
            neo4j_model.username,
            neo4j_model.password,
            neo4j_model.database,
        )
    return _semanticdb


class LazyNeo4jModelConfig:
    """Compatibility proxy so older imports do not resolve env at import time."""

    def __getattr__(self, item: str) -> Any:
        return getattr(get_neo4j_model_config(), item)


class LazyNeo4jDatabase:
    """Compatibility proxy that opens the Neo4j driver only on first use."""

    def __getattr__(self, item: str) -> Any:
        return getattr(get_semanticdb(), item)

    @property
    def _database_name(self) -> str:
        return get_semanticdb()._database_name

    def close(self) -> None:
        global _semanticdb
        if _semanticdb is not None:
            _semanticdb.close()
            _semanticdb = None


class LazyAuthData:
    """Compatibility proxy that materializes auth data only when accessed."""

    def __call__(self) -> dict[str, str]:
        return get_auth_data()

    def __getitem__(self, key: str) -> str:
        return get_auth_data()[key]

    def get(self, key: str, default: Any = None) -> Any:
        return get_auth_data().get(key, default)

    def items(self):
        return get_auth_data().items()

    def keys(self):
        return get_auth_data().keys()

    def values(self):
        return get_auth_data().values()

    def __iter__(self):
        return iter(get_auth_data())

    def __len__(self) -> int:
        return len(get_auth_data())


neo4j_model = LazyNeo4jModelConfig()
semanticdb = LazyNeo4jDatabase()

# Backward compatibility for callers that imported auth_data directly.
auth_data = LazyAuthData()

# Default staging database name from environment
NEO4J_STAGING_DB_NAME = os.getenv("NEO4J_STAGING_DB_NAME", "stagingdb")


def get_staging_db(staging_db_name: str | None = None) -> Neo4jDatabase:
    """Create a Neo4jDatabase connection to the staging database."""
    neo4j_model = get_neo4j_model_config()
    db_name = staging_db_name or NEO4J_STAGING_DB_NAME
    logger.info("Creating staging database connection to: %s", db_name)
    return Neo4jDatabase(
        neo4j_model.url,
        neo4j_model.username,
        neo4j_model.password,
        db_name,
    )


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
        from langchain_openai import ChatOpenAI

        model_name = _resolve_openai_model_name()
        logger.info("Initializing OpenAI LLM for internal flows: %s", model_name)
        _llm = ChatOpenAI(model=model_name)
    return _llm


def get_graphdb():
    """Lazy initialization of the Neo4jGraph."""
    global _graphdb
    if _graphdb is None:
        from langchain_neo4j import Neo4jGraph

        neo4j_model = get_neo4j_model_config()
        logger.info("Initializing Neo4jGraph for database: %s", neo4j_model.database)
        _graphdb = Neo4jGraph(
            url=neo4j_model.url,
            username=neo4j_model.username,
            password=neo4j_model.password,
            database=neo4j_model.database,
            enhanced_schema=True,
        )
    return _graphdb


def cleanup():
    """Close global Neo4j connections during shutdown."""
    global _semanticdb
    if _semanticdb is not None:
        try:
            logger.info("Closing semanticdb connection...")
            _semanticdb.close()
        except Exception:
            pass
        finally:
            _semanticdb = None
    if _graphdb is not None:
        try:
            logger.info("Closing graphdb connection...")
            if hasattr(_graphdb, "_driver"):
                _graphdb._driver.close()
        except Exception:
            pass


atexit.register(cleanup)
