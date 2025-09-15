from langchain_core.messages import AnyMessage
from neo4j_onto2ai_toolset.langgraph_nodes.model_nodes import AgentState
from neo4j_onto2ai_toolset.onto2ai_tool_config import ONTOLOGY_DOMAIN,logger

ONTO2AI_CONTEXT="Context: Ontology-driven Cypher query generation for Neo4j.\n"
uri_domain = ONTOLOGY_DOMAIN
def create_model_prompt(
    state: AgentState
) -> list[AnyMessage]:
        prompt = (
        f"{ONTO2AI_CONTEXT}"
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
        "Next Step: Pass the output directly to tool modify_model, then run it.\n"
        )
        logger.debug(f"create_model_prompt - {prompt}")
        return [{"role": "system", "content": prompt}] + state["messages"]

def enhance_model_prompt(
    state: AgentState
) -> list[AnyMessage]:
        prompt=(
        f"{ONTO2AI_CONTEXT}"
        "Objective: From the input, extract the concept, then use tool retrieve_model to get stored model and enhance it by inferring  related concepts and relationships.\n"
        "Output Style: a JSON array of Cypher statements. No explanations, comments, wrappers, backticks, or preamble.\n"
        "Each statement must be a string element in the array.\n"
        "Audience: Technical users working with ontology-based Neo4j graphs.\n"
        "Constraints:\n"
        "- Each node must be an :owl__Class with rdfs__label in lowercase words (space-separated).\n"
        "- Add all annotation properties as metadata to nodes and relationships.\n"
        "- Always use MERGE on uri as the unique identifier (never CREATE).\n"
        "- Relationship types must be camelCase, starting lowercase; include owl__minQualifiedCardinality if available.\n"
        f"- All new nodes and relationships must have a uri with domain {uri_domain}.\n"
        "- Each node/relationship must include skos__definition (no single quotes allowed).\n"
        "- Always MATCH or MERGE nodes/relationships by uri.\n"
        "- Include as many valid relationships as possible.\n"
        "- Output must be strictly the JSON array of Cypher statements, nothing else.\n"
        "Next Step: Pass the output directly to tool modify_model, then run it.\n"
        )
        logger.debug(f"enhance_model_prompt - {prompt}")
        return [{"role": "system", "content": prompt}] + state["messages"]

def validate_and_clean_model_prompt(
    state: AgentState
) -> list[AnyMessage]:
        prompt=(
        f"{ONTO2AI_CONTEXT}"
        "Objective: From the input, extract the concept, then use tool retrieve_model to get stored model, \n"
        "then identify any duplicated node and relationship and generate cypher statements to delete the duplicated items\n"
        "Output Style: a JSON array of Cypher statements. No explanations, comments, wrappers, backticks, or preamble.\n"
        "Each statement must be a string element in the array.\n"
        "Audience: Technical users working with ontology-based Neo4j graphs.\n"
        "Constraints:\n"
        "- Each node must be an :owl__Class with rdfs__label in lowercase words (space-separated).\n"
        "- Relationship types must be camelCase, starting lowercase. \n"
        "- Always MATCH nodes/relationships by uri.\n"
        "- Output must be strictly the JSON array of Cypher statements, nothing else.\n"
        "Next Step: Pass the output directly to tool modify_model, then run it.\n"
        )
        logger.debug(f"validate_and_clean_model_prompt - {prompt}")
        return [{"role": "system", "content": prompt}] + state["messages"]


# quick test
# state_of_input = {"messages": [{
#             "role": "user",
#             "content": "{user_input}"
#             }]}
# print(enhance_model_prompt(state_of_input))