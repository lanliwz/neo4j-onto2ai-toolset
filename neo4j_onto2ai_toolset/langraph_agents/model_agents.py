from langgraph.prebuilt import create_react_agent
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import llm, graphdb
from neo4j_onto2ai_toolset.langgraph_tools.model_tools import *

# Agents
modeler_agent = create_react_agent(
    model=llm,
    tools=[display_model],
    name="model_maintenance_agent",
    prompt=(
        "Context: Ontology-driven Cypher query generation for Neo4j graph database."
        "Objective: From the input, extract the concept and the namespace, generate an array of Cypher statements to add or merge nodes (owl:Class) and relationships with properties, using the ontology conventions below.\n"
        "Style: The Output of the LLM must be Cypher statements only, no explanations or wrappers, with each statement as an array element."
        "Audience: Technical users working with ontology-based Neo4j graphs."
        "Requirements:"
        "- Each node is an owl:Class with rdfs__label (lowercase, space-separated)."
        "- Add all annotation properties as metadata to both nodes and relationships."
        "- Merge nodes if already exist."
        "- Relationship type is camelCase, first letter lowercase; add owl__minQualifiedCardinality if possible."
        "- All nodes/relationships have uri with HTTP and the provided domain."
        "- Each node/relationship includes skos__definition (no single quotes)."
        "- Match nodes only with rdfs__label."
        "- If schema is a URL, add gojs_documentLink to node."
        "- Find and add as many relationships as possible."
        "- Absolutely do not include any explanations, apologies, preamble, or backticks in your responses."
        "Tools: pass the output to display_model"
    ),
    context_schema=ModelContextSchema
)

realworld_model_agent = create_react_agent(
    model=llm,
    tools=[create_model],
    name="realworld_model_agent",
    prompt=(
        "Context: You are an ontology-to-Cypher generation agent. You transform model definitions into Cypher MERGE statements for owl__Class nodes and relationships, enriched with semantic metadata. "
        "Objective: Generate Cypher statements to add nodes (owl__Class) and relationships. Output each Cypher statement as a single element in an array. The goal is to build a semantically rich graph model aligned with the given model. "
        "Style: Use real-world knowledge to infer possible relationships. Always produce Cypher MERGE statements (no explanations, no apologies). Be consistent and precise in formatting. "
        "Tone: Direct, declarative, and machine-readable. No extra narrative text, only Cypher statements in array form. "
        "Audience: This output is consumed by a graph database pipeline (Neo4j) and automated systems — not a human reader. Precision and correctness are critical. "
        "Response: For each node: Create as owl__Class with rdfs__label (lower case, words separated by spaces). Add annotation properties as metadata (skos__definition must not contain single quotes). Assign a uri with domain in format of http://mymodel.com/ontology. "
        "For each relationship: Match nodes by rdfs__label. Generate Cypher to create relationship using camelCase (first character lowercase). Include annotation properties and, if possible, owl__minQualifiedCardinality. Add skos__definition for each relationship (no single quotes). "
        "Note: Add as many relationships as can be reasonably inferred. Return only Cypher statement arrays — no explanations or apologies."
        "Tools: pass the output to create_model"
    ),
    context_schema=ModelContextSchema
)
model_review_agent = create_react_agent(
    model=llm,
    tools=[retrieve_stored_model],
    name="model_review_agent",
    prompt= (
        "You are a model expert."
        "re-format the model in plain english."
    ),
    context_schema=ModelContextSchema
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
    context_schema=ModelContextSchema
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
    context_schema=ModelContextSchema
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
    context_schema=ModelContextSchema
)


# response = realworld_model_agent.invoke(
#     {
#         "messages":"create human model, with namespace myfin.com"
#     }
# )
# print (response)
