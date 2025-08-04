from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from typing import TypedDict, List, Optional
import os
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import (
    neo4j_bolt_url,
    username,
    password,
    neo4j_db_name)

from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB, get_schema as get_model_from_db
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import llm, graphdb

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)
checkpointer = InMemorySaver()


# Tools
def get_stored_model(key_concept: str) -> str:
    """Display the stored model related to the key concept"""
    resp = get_model_from_db(key_concept, db)
    return resp

model_qa_agent = create_react_agent(
    model=llm,
    tools=[get_stored_model],
    name="model_qa_agent",
    prompt= (
        "You are a model expert."
        "1. Find any duplicated concept and relationship for given model."
        "2. Generate cypher to delete duplicated items. one statement per line."
    )
)

rdb_ddl_agent = create_react_agent(
    model=llm,
    tools=[get_stored_model],
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
    tools=[get_stored_model],
    name="pydantic_class_agent",
    prompt= (
        "You are a model expert."
        "Based on input model, generate Pydantic classes. No pre-amble."
        "Do not wrap the response in any backticks or anything else. Respond with code only!"
    )
)

supervisor = create_supervisor(
    # Each message in messages should follow the Chat Message format:
    # {
    # "role": "user" | "assistant" | "system" | "tool",
    # "content": str
    # }
    #
    agents=[model_qa_agent,rdb_ddl_agent,pydantic_class_agent],
    model=llm,
    prompt=(
    "You are a team supervisor managing all models."
    "For question about model, extract key concept from the question first"
    "If the quest is about validation of the model, then use model_qa_agent"
    "If the quest is about generate relational database schema of the model, then use rdb_ddl_agent"
    "If the quest is about generate python or pydantic class or schema of the model, then use pydantic_class_agent"
    )
)

from langchain.schema import AIMessage
from typing import List, Optional

def get_last_ai_content(messages: List) -> Optional[str]:
    """
    Returns the content of the last non-empty AIMessage from a LangChain messages list.
    Tries index -1 first, then scans backward as fallback.
    """
    # Try index -1 first
    last = messages[-1]
    if isinstance(last, AIMessage) and last.content.strip():
        return last.content.strip()

    # Fallback: scan in reverse
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content.strip():
            return msg.content.strip()

    return None  # No AIMessage found

def start_cli_chat():
    app = supervisor.compile()
    print("🤖 Chat started. Type `exit` to stop.")
    while True:
        user_input = input("🗨️  You: ")
        if "exit" in user_input:
            print("👋 Exiting chat.")
            break
        state_of_input = {"messages": [{"role": "user",
                    # "content": "find person model and check any duplication?"
                    "content": f"{user_input}"
                }]}
        response = app.invoke(state_of_input)
        print(get_last_ai_content(response["messages"]))



start_cli_chat()
