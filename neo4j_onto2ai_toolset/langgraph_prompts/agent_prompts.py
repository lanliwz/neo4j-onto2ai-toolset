from langchain_core.messages import AnyMessage
from langgraph.runtime import get_runtime
from neo4j_onto2ai_toolset.langgraph_nodes.model_nodes import AgentState
from neo4j_onto2ai_toolset.onto2ai_tool_config import ONTOLOGY_DOMAIN

def create_model_prompt(
    state: AgentState
) -> list[AnyMessage]:
        uri_domain = ONTOLOGY_DOMAIN
        prompt = (
        "Context: Ontology-driven Cypher query generation for Neo4j.\n"
        "Objective: From the input, extract the concept, infer related concepts and relationships, "
        "and return a JSON array of Cypher statements.\n"
        "Output Style: Cypher statements only. No explanations, comments, wrappers, backticks, or preamble. "
        "Each statement must be a string element in the array.\n"
        "Audience: Technical users working with ontology-based Neo4j graphs.\n"
        "Constraints:\n"
        "- Each node must be an :owl__Class with rdfs__label in lowercase words (space-separated).\n"
        "- Add all annotation properties as metadata to nodes and relationships.\n"
        "- Always use MERGE on uri as the unique identifier (never CREATE).\n"
        "- Relationship types must be camelCase, starting lowercase; include owl__minQualifiedCardinality if available.\n"
        f"- All nodes and relationships must have a uri with domain {uri_domain}.\n"
        "- Each node/relationship must include skos__definition (no single quotes allowed).\n"
        "- Always MATCH or MERGE nodes/relationships by uri.\n"
        "- Include as many valid relationships as possible.\n"
        "- Output must be strictly the JSON array of Cypher statements, nothing else.\n"
        "Execution: Pass the output directly to create_model_agent.\n"
        )
        return [{"role": "system", "content": prompt}] + state["messages"]
