from langchain_core.messages import AnyMessage
from neo4j_onto2ai_toolset.langgraph_nodes.model_nodes import AgentState
from neo4j_onto2ai_toolset.onto2ai_tool_config import ONTOLOGY_DOMAIN,logger

ONTO2AI_CONTEXT="Context: Ontology-driven Cypher query generation for Neo4j.\n"
uri_domain = "http://upupedu.com/ontology/entitlement/tabular_data"
def create_model_prompt(
    state: AgentState
) -> list[AnyMessage]:
        prompt = """
You are an ontology-aware Cypher generator.
Goal: From the specification below, output a JSON array of Cypher statements that build the ontology model, remember, you are creating a model, note instance of the model, so for any data property, create it as a relationship and a new :owl__Datatype with corresponding xml data type and format restriction. Each array element is a single Cypher statement string.
Core Concepts (all nodes are :owl__Class with lowercase, space-separated rdfs__label):
- policy — Encapsulates access logic, combining row-level and column-level rules. Each policy must has a policy_id and a policy_name, optionally has a definition
- policy group — A collection of policies aligned to a persona, function, or role set. Each policy must has a policy_group_id and a policy_group_name, optionally has a definition
- column — Represents a physical database column; capture schema_name, table_name, column_name as data properties on the node.
- user — Subject/principal entitled to policy groups.
Relationships (create as many valid instances as possible):
- (policy)-[:hasRowRule]->(column) — Policy includes row-level access conditions; row rule applies to a specific column. Each policy can have multiple row rules.
- (policy)-[:hasColumnRule]->(column) — Policy includes column-level masking logic; mask rule applies to a specific column. Each policy can have multiple column rules.
- (user)-[:memberOf]->(policy group) — User inherits policies through group membership. 
- (policy group)-[:includesPolicy]->(policy) — Policy groups bundle policies.
Hard Constraints:
- Always MERGE nodes and relationships by uri; never CREATE.
- Every node must be labeled :owl__Class and include rdfs__label (lowercase words, space-separated) and skos__definition (no single quotes).
- Every relationship must include uri, rdfs__label (lowercase words, space-separated), and skos__definition (no single quotes). If owl__minQualifiedCardinality and owl__maxQualifiedCardinality can be defined, include them on the relationship.
- Relationship types must be camelCase, starting lowercase (hasRowRule, hasColumnRule, memberOf, includesPolicy).
- All uris must use the domain http://upupedu.com/ontology (e.g., http://upupedu.com/ontology/policy, http://upupedu.com/ontology/relationship/hasRowRule).
- Add all annotation properties as metadata to both nodes and relationships (e.g., rdfs__label, skos__definition, and any provided annotations).
- Include node data properties for column: schema_name, table_name, column_name. Include reasonable annotations for other nodes as available.
Output Rules:
- Output must be ONLY a JSON array of Cypher statement strings; no explanations, comments, wrappers, or preamble.
- Each statement must be valid Cypher and stand alone (e.g., MERGE … ON CREATE SET …;).
- Always ensure MERGE targets use uri as the unique identifier.
Audience: Technical users working with ontology-based Neo4j graphs.
        """

        logger.debug(f"create_model_prompt - {prompt}")
        return [{"role": "system", "content": prompt}] + state["messages"]



# quick test
state_of_input = {"messages": [{
            "role": "user",
            "content": "{user_input}"
            }]}
print(create_model_prompt(state_of_input))