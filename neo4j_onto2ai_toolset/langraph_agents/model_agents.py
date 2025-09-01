from langgraph.prebuilt import create_react_agent
from neo4j_onto2ai_toolset.onto2ai_tool_config import llm
from neo4j_onto2ai_toolset.langgraph_tools.model_tools import *
from neo4j_onto2ai_toolset.langgraph_prompts.agent_prompts import create_model_prompt, enhance_model_prompt, \
    validate_and_clean_model_prompt

# Agents
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
    # prompt=(
    #     "Context: You are an ontology-to-Cypher generation agent. "
    #     "If you are asked to enhance model, you need to execute retrieve_model first. You transform model definitions into Cypher MERGE statements for owl__Class nodes and relationships, enriched with semantic metadata. "
    #     "Objective: Generate Cypher statements to add nodes (owl__Class) and relationships. Output each Cypher statement as a single element in an array. The goal is to build a semantically rich graph model aligned with the given model. "
    #     "Style: Use real-world knowledge to infer possible relationships. Always produce Cypher MERGE statements (no explanations, no apologies). Be consistent and precise in formatting. "
    #     "Tone: Direct, declarative, and machine-readable. No extra narrative text, only Cypher statements in array form. "
    #     "Audience: This output is consumed by a graph database pipeline (Neo4j) and automated systems — not a human reader. Precision and correctness are critical. "
    #     "Response: For each node: Create as owl__Class with rdfs__label (lower case, words separated by spaces). Add annotation properties as metadata (skos__definition must not contain single quotes). Assign a uri with provided namespace. "
    #     "For each relationship: Match nodes by rdfs__label. Generate Cypher to create relationship using camelCase (first character lowercase). Include annotation properties and, if possible, owl__minQualifiedCardinality. Add skos__definition for each relationship (no single quotes). "
    #     "Note: Add as many relationships as can be reasonably inferred. Return only Cypher statement arrays — no explanations or apologies."
    #     "Tools: pass the output to modify_model"
    # ),
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
    # prompt= (
    #     "You are a model expert."
    #     "1. Find any duplicated node and relationship for given model. All nodes are type of owl__Class"
    #     "2. Generate cypher to delete duplicated items. "
    #     "3. for example: if the duplicated node is :Human, then generated cypher is MATCH (h:owl__Class) WHERE h.rdfs__label = 'human' WITH h ORDER BY id(h) DETACH DELETE h"
    #
    # ),
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
