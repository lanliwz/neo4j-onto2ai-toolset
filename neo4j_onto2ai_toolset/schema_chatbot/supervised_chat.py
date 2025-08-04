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
# checkpointer = InMemorySaver()


# # --- Define State Type ---
# class ChatState(TypedDict):
#     user_input: Optional[str]
#     history: List[str]
#     steps: List[str]
#
# # --- Define chat handler ---
# def handle_user_input(state: ChatState) -> ChatState:
#     state["history"].append(f"User: {state['user_input']}")
#     state["steps"].append("input_handled")
#     return state
#
# def end_chat(state: ChatState) -> ChatState:
#     state["steps"].append("exit")
#     return state
#
# # --- Define routing logic ---
# def router(state: ChatState) -> str:
#     if state["user_input"].strip().lower() == "exit":
#         return "end"
#     return "input_handler"

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

# supervisor_wf = supervisor.compile()




#### test block
# app = supervisor.compile()
# result = app.invoke({"messages": [{"role": "user",
#             # "content": "find person model and check any duplication?"
#             "content": "find person model and then gnerate python schema"
#         }]})
# print(result)

# def supervisor_node(state: ChatState) -> ChatState:
#     print(state)
#     user_input = state["user_input"]
#     # result = supervisor_wf.invoke(f"""{{"messages": [{{"role": "user","content": "{user_input}"}}]}}""")
#     result = supervisor_wf.invoke(state)
#     state["history"].append(f"supervisor: {result}")
#     state["steps"].append("chat")
#     return state

# --- Build LangGraph ---
# graph = StateGraph(ChatState)
#
# graph.add_node("chat", supervisor_node)
# graph.add_node("end", end_chat)
# graph.add_node("input_handler", handle_user_input)
#
# graph.set_entry_point("input_handler")
# graph.add_edge("input_handler", "chat")
# graph.add_conditional_edges("chat", router)
#
# workflow = graph.compile()

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
        result = app.invoke(state_of_input)
        print(result["messages"])


start_cli_chat()
