from langgraph_supervisor import create_supervisor
from neo4j_onto2ai_toolset.langraph_agents.model_agents import *


model_manager = create_supervisor(
    # Each message in messages should follow the Chat Message format:
    # {
    # "role": "user" | "assistant" | "system" | "tool",
    # "content": str
    # }
    #
    agents=[validate_model_agent, rdb_ddl_agent, pydantic_class_agent, model_review_agent, create_model_agent, modify_model_agent, create_entitlement_model_agent],
    model=llm,
    prompt=(
        "You are a supervisor responsible for routing the user's inquiry to the correct agent.\n"
        "Task:\n"
        f"- If the question is about 'create entitlement model' → use {create_entitlement_model_agent.name}.\n"
        f"- If the question is about reviewing or showing a model → use {model_review_agent.name}.\n"
        f"- If the question is about validating a model → use {validate_model_agent.name}.\n"
        f"- If the question is about generating a relational database schema → use {rdb_ddl_agent.name}.\n"
        f"- If the question is about generating Python or Pydantic classes/schemas → use {pydantic_class_agent.name}.\n"
        f"- If the question is about enhancing a model → use {modify_model_agent.name}.\n"
        f"- If the question is about creating a new model → use {create_model_agent.name}.\n\n"
        "Constraints:\n"
        "- Always pick the most specific matching agent.\n"
        "- Return the selected agent's tool output exactly as it is.\n"
        "- Do not add explanations, summaries, or reformatting.\n"
    )
    )