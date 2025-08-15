from langgraph_supervisor import create_supervisor
from neo4j_onto2ai_toolset.langraph_agents.model_agents import llm
from neo4j_onto2ai_toolset.langraph_agents.model_agents import *

manage_model_supervisor = create_supervisor(
    # Each message in messages should follow the Chat Message format:
    # {
    # "role": "user" | "assistant" | "system" | "tool",
    # "content": str
    # }
    #
    agents=[],
    model=llm,
    prompt=(
        "Context: Ontology-driven Cypher query generation for Neo4j graph database.\n"
        "Objective: Given a request to create a new model, extract the concept and namespace from the request first, may be a URL or text, generate an array of Cypher statements to add or merge nodes (owl:Class) and relationships with properties, using the ontology conventions below.\n"
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
        "- Absolutely do not include any explanations, apologies, preamble, or backticks in your responses."
    )
)

model2schema_supervisor = create_supervisor(
    # Each message in messages should follow the Chat Message format:
    # {
    # "role": "user" | "assistant" | "system" | "tool",
    # "content": str
    # }
    #
    agents=[model_qa_agent, rdb_ddl_agent, pydantic_class_agent, model_review_agent],
    model=llm,
    prompt=(
        "You are a supervisor managing all tasks related to review, validate model and generate all type of schema."
        "For question about model, extract key concept from the question first"
        "If the question is about review or show the model, then use model_review_agent"
        "If the question is about validation of the model, then use model_qa_agent"
        "If the question is about generate relational database schema of the model, then use rdb_ddl_agent"
        "If the question is about generate python or pydantic class or schema of the model, then use pydantic_class_agent"
        "If the question is about creating a new model, then use manage_model_supervisor"
    )
    )