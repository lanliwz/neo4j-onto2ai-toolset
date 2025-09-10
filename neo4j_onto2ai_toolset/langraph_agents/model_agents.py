from langgraph.prebuilt import create_react_agent
from neo4j_onto2ai_toolset.onto2ai_tool_config import llm
from neo4j_onto2ai_toolset.langgraph_tools.model_tools import *
from neo4j_onto2ai_toolset.langgraph_prompts.agent_prompts import create_model_prompt, enhance_model_prompt, \
    validate_and_clean_model_prompt
from neo4j_onto2ai_toolset.langgraph_prompts.crt_entitlement_schema_prompts import create_entitlement_model_prompt

# Agents
create_entitlement_model_agent = create_react_agent(
    model=llm,
    tools=[modify_model],
    name="create_entitlement_model_agent",
    prompt=create_entitlement_model_prompt,
    context_schema=ModelContextSchema
)

create_model_agent = create_react_agent(
    model=llm,
    tools=[modify_model],
    name="create_model_agent",
    prompt=create_model_prompt,
    context_schema=ModelContextSchema
)

modify_model_agent = create_react_agent(
    model=llm,
    tools=[retrieve_model,modify_model],
    name="modify_model_agent",
    prompt=enhance_model_prompt,
    context_schema=ModelContextSchema
)
model_review_agent = create_react_agent(
    model=llm,
    tools=[retrieve_model],
    name="model_review_agent",
    prompt= (
        "You are a model expert."
        "re-format the model in plain english."
    ),
    context_schema=ModelContextSchema
)

# Agents
validate_model_agent = create_react_agent(
    model=llm,
    tools=[retrieve_model,modify_model],
    name="validate_model_agent",
    prompt=validate_and_clean_model_prompt,
    context_schema=ModelContextSchema
)

rdb_ddl_agent = create_react_agent(
    model=llm,
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
    model=llm,
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
