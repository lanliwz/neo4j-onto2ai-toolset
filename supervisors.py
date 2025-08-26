from langgraph_supervisor import create_supervisor
from neo4j_onto2ai_toolset.langraph_agents.model_agents import llm
from neo4j_onto2ai_toolset.langraph_agents.model_agents import *


model_manager = create_supervisor(
    # Each message in messages should follow the Chat Message format:
    # {
    # "role": "user" | "assistant" | "system" | "tool",
    # "content": str
    # }
    #
    agents=[validate_model_agent, rdb_ddl_agent, pydantic_class_agent, model_review_agent, modeler_agent, modify_model_agent],
    model=llm,
    prompt=(
        "You are a user working with stored models to produce schemas for applications. "
        "Your first step is always to extract the key concept from the question. "
        "Then, route the request to the correct agent: "
        "- If the question is about reviewing or showing a model → use model_review_agent. "
        "- If the question is about validating a model → use validate_model_agent. "
        "- If the question is about generating a relational database schema → use rdb_ddl_agent. "
        "- If the question is about generating Python or Pydantic classes/schemas → use pydantic_class_agent. "
        "- If the question is about enhance a model → use modify_model_agent, along with additional instruct to use retrieve_model tool first."
        "- If the question is about creating a new model → use modify_model_agent."
    )
    )