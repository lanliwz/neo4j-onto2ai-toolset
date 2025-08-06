import json

from langgraph.prebuilt import create_react_agent
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import (
    neo4j_bolt_url,
    username,
    password,
    neo4j_db_name)

from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB, get_schema as get_model_from_db
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import llm, graphdb

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)

# Tools
def retrieve_stored_model(key_concept: str) -> str:
    """Display the stored model related to the key concept"""
    resp = get_model_from_db(key_concept, db)
    return resp

def execute_cypher_statement(cypher_statement: str) -> str:
    """
    Executes the given Cypher statement.
    """
    result = graphdb.query(cypher_statement)
    return result

# Agents
model_qa_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="model_qa_agent",
    prompt= (
        "You are a model expert."
        "1. Find any duplicated concept and relationship for given model."
        "2. Generate cypher to delete duplicated items. one statement per line."
    )
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
    )
)

pydantic_class_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="pydantic_class_agent",
    prompt= (
        "You are a model expert."
        "Based on input model, generate Pydantic classes. No pre-amble."
        "Do not wrap the response in any backticks or anything else. Respond with code only!"
    )
)



