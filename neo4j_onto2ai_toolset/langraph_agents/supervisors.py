from langgraph_supervisor import create_supervisor
from neo4j_onto2ai_toolset.langraph_agents.model_agents import llm
from neo4j_onto2ai_toolset.langraph_agents.model_agents import *

# manage_model_supervisor = create_supervisor(
#     model=llm,
#     agents=[create_model_agent],
#     prompt=(
#         "Context: you are an Neo4j expert."
#         "Objective: given user input, create a graph data model, generate to Cypher statements, one statement per line. No pre-amble."
#         "The node in the model is a owl__Class with rdfs_label, and the annotation properties are metadata for both node and relationship."
#         "For node, use Merge instead of Create to add node."
#         "For create relationship statement, MATCH the nodes with rdfs__label, if you sure about cardinality of the relationship is more than 1, add relationship property owl__minQualifiedCardinality."
#         "Style: Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
#         "Do not include any explanations or apologies in your responses"
#     )
# )

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
        )
    )