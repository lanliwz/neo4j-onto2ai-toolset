from langgraph_supervisor import create_supervisor
from neo4j_onto2ai_toolset.langraph_agents.model_agents import llm

manage_model_supervisor = create_supervisor(
    model=llm,
    prompt=(
        "Context: you are an Neo4j expert."
        "Objective: given user input, create a graph data model, generate to Cypher statements, one statement per line. No pre-amble."
        "The node in the model is a owl__Class with rdfs_label, and the annotation properties are metadata for both node and relationship."
        "For node, use Merge instead of Create to add node."
        "For create relationship statement, MATCH the nodes with rdfs__label, if you sure about cardinality of the relationship is more than 1, add relationship property owl__minQualifiedCardinality."
        "Style: Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
        "Do not include any explanations or apologies in your responses"
    )
)

