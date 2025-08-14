from dataclasses import dataclass

from langchain.agents import create_tool_calling_agent
from langchain_core.runnables import Runnable
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import json

from langchain_neo4j import Neo4jGraph
from langgraph.prebuilt import create_react_agent
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import (
    neo4j_bolt_url,
    username,
    password,
    neo4j_db_name)

from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB, get_schema as get_model_from_db
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import llm, graphdb

semanticdb = SemanticGraphDB(neo4j_bolt_url, username, password, neo4j_db_name)

@dataclass
class ContextSchema:
    semantic_db: SemanticGraphDB
    graph_db: Neo4jGraph
    runtime_username: str

@tool
def retrieve_stored_model(key_concept: str) -> str:
    """Display the stored model related to the key concept"""
    resp = get_model_from_db(key_concept, semanticdb)
    return resp


create_model_agent: Runnable = create_tool_calling_agent(
    llm=llm,
    tools=[],
    prompt=ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are to convert ontology schema information into Cypher queries for Neo4j, following specific formatting and metadata rules. "
                "Your responses must strictly follow the requirements below."
            ),
        ),
        (
            "human",
            (
                "Context: Ontology-driven Cypher query generation for Neo4j graph database.\n"
                "Objective: Given a concept (may be a URL or text) and a namespace, generate an array of Cypher statements to add or merge nodes (owl:Class) and relationships with properties, using the ontology conventions below.\n"
                "Style: Output must be Cypher statements only, no explanations or wrappers, with each statement as an array element.\n"
                "Audience: Technical users working with ontology-based Neo4j graphs.\n"
                "Requirements:\n"
                "- Each node is an owl:Class with rdfs__label (lowercase, space-separated).\n"
                "- Add all annotation properties as metadata to both nodes and relationships.\n"
                "- Merge nodes if already exist.\n"
                "- Relationship type is camelCase, first letter lowercase; add owl__minQualifiedCardinality if possible.\n"
                "- All nodes/relationships have uri with HTTP and the provided domain.\n"
                "- Each node/relationship includes skos__definition (no single quotes).\n"
                "- Match nodes only with rdfs__label.\n"
                "- If schema is a URL, add gojs_documentLink to node.\n"
                "- Find and add as many relationships as possible.\n"
                "- Absolutely do not include any explanations, apologies, preamble, or backticks in your responses.\n"
                "\n"
                "Inputs:\n"
                "namespace: {namespace}\n"
                "concept: {concept}"
            ),
        ),
    MessagesPlaceholder("agent_scratchpad"),
])
)
# Agents
model_review_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="model_review_agent",
    prompt= (
        "You are a model expert."
        "re-format the model in plain english."
    ),
    context_schema=ContextSchema
)

# Agents
model_qa_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="model_qa_agent",
    prompt= (
        "You are a model expert."
        "1. Find any duplicated concept and relationship for given model."
        "2. Generate cypher to delete duplicated items. one statement per line."
    ),
    context_schema=ContextSchema
)

rdb_ddl_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="rdb_ddl_agent",
    prompt= (
        "You are a model expert."
        "Based on input model, generate oracle database DDL, ignore annotation properties. No pre-amble."
        "For simple node and one to one relationship, add column to the table instead of creating another table"
        "Do not wrap the response in any backticks or anything else. Respond with code only!"
    ),
    context_schema=ContextSchema
)

pydantic_class_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="pydantic_class_agent",
    prompt= (
        "You are a model expert."
        "Based on input model, generate Pydantic classes. No pre-amble."
        "Do not wrap the response in any backticks or anything else. Respond with code only!"
    ),
    context_schema=ContextSchema
)



