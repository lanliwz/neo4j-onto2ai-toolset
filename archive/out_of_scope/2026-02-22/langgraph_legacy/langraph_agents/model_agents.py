from langgraph.prebuilt import create_react_agent
from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm
from neo4j_onto2ai_toolset.langgraph_tools.model_tools import *
from neo4j_onto2ai_toolset.langgraph_prompts.agent_prompts import create_model_prompt, enhance_model_prompt, \
    validate_and_clean_model_prompt
from neo4j_onto2ai_toolset.langgraph_prompts.crt_entitlement_schema_prompts import create_entitlement_model_prompt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

checkpointer = InMemorySaver()
# Agents
create_entitlement_model_agent = create_react_agent(
    model=get_llm(),
    tools=[modify_model],
    name="create_entitlement_model_agent",
    prompt=create_entitlement_model_prompt,
    context_schema=ModelContextSchema,
    checkpointer = checkpointer
)

create_model_agent = create_react_agent(
    model=get_llm(),
    tools=[modify_model],
    name="create_model_agent",
    prompt=create_model_prompt,
    context_schema=ModelContextSchema,
    checkpointer = checkpointer
)

modify_model_agent = create_react_agent(
    model=get_llm(),
    tools=[retrieve_model,modify_model],
    name="modify_model_agent",
    prompt=enhance_model_prompt,
    context_schema=ModelContextSchema,
    checkpointer = checkpointer
)
model_review_agent = create_react_agent(
    model=get_llm(),
    tools=[retrieve_model],
    name="model_review_agent",
    prompt=(
        "You are a Cypher expert and an ontologist.\n"
        "Task:\n"
        "1. From the user’s question, extract the key concept.\n"
        f"2. Use this concept to call the tool {retrieve_model.name}.\n"
        "3. Return the tool output exactly as it is, without adding, re-formatting, or explaining.\n\n"
        "Constraints:\n"
        "- Only extract the main concept from the user's question, ignore the word like show, display, review, me or model.\n"
        "- Do not summarize or rephrase the tool output.\n"
        "- If no model is found, explain what concept you extracted and why retrieval failed.\n"
    ),
    context_schema=ModelContextSchema
)

model_view_all_agent = create_react_agent(
    model=get_llm(),
    tools=[retrieve_all_model],
    name="model_view_all_agent",
    prompt=(
        "You are a Cypher expert and an ontologist.\n"
        "Task:\n"
        "1. From the user’s question, extract the key concept.\n"
        f"2. Use this concept to call the tool {retrieve_all_model.name}.\n"
        "3. Return the tool output exactly as it is, without adding, re-formatting, or explaining.\n\n"
        "Constraints:\n"
        "- Only extract the main concept from the user's question, ignore the word like show, display, review, me or model.\n"
        "- Do not summarize or rephrase the tool output.\n"
        "- If no model is found, explain what concept you extracted and why retrieval failed.\n"
    ),
    context_schema=ModelContextSchema
)

# Agents
validate_model_agent = create_react_agent(
    model=get_llm(),
    tools=[retrieve_model,modify_model],
    name="validate_model_agent",
    prompt=validate_and_clean_model_prompt,
    context_schema=ModelContextSchema
)

rdb_ddl_agent = create_react_agent(
    model=get_llm(),
    tools=[retrieve_model],
    name="rdb_ddl_agent",
    prompt= (
        "You are a model expert."
        "Based on input model, generate oracle database DDL, ignore annotation properties. No pre-amble."
        "For simple node and one to one relationship, add column to the table instead of creating another table"
        "Do not wrap the response in any backticks or anything else. Respond with code only!"
    ),
    context_schema=ModelContextSchema
)

pydantic_class_agent = create_react_agent(
    model=get_llm(),
    tools=[retrieve_model],
    name="pydantic_class_agent",
    prompt= (
        "You are a model expert."
        "Based on input model, generate Pydantic classes. No pre-amble."
        "Do not wrap the response in any backticks or anything else. Respond with code only!"
    ),
    context_schema=ModelContextSchema
)


# response = realworld_model_agent.invoke(
#     {
#         "messages":"create human model, with namespace myfin.com"
#     }
# )
# print (response)
