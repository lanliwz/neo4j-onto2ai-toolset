from langchain_core.messages import AnyMessage
from neo4j_onto2ai_toolset.langgraph_nodes.model_nodes import AgentState
from neo4j_onto2ai_toolset.onto2ai_tool_config import ONTOLOGY_DOMAIN,logger

ONTO2AI_CONTEXT="Context: Ontology-driven Cypher query generation for Neo4j.\n"
uri_domain = "http://upupedu.com/ontology/entitlement/tabular_data"
def create_entitlement_model_prompt(
    state: AgentState
) -> list[AnyMessage]:
    prompt = (
        f"{ONTO2AI_CONTEXT}"
        "Goal: From the specification below, output a JSON array of Cypher statements that build the ontology model, "
        "remember, you are creating model, not instance of the model, so for any data property, create it as a "
        "relationship and a new :rdfs__Datatype with corresponding xml data type and format restriction."
        "Each array element is a single Cypher statement string.\n"
        "Core Concepts (all nodes are :owl__Class with lowercase, space-separated rdfs__label):\n"
        "- policy — Encapsulates access logic, combining row-level and column-level rules. Each policy must has a policy_id "
        "and a policy_name, optionally has a definition\n"
        "- policy group — A collection of policies aligned to a persona, function, or role set. Each policy must has a "
        "policy_group_id and a policy_group_name, optionally has a definition\n"
        "- column — Represents a physical database column; Each column must have a column_id and a column_name as data properties.\n"
        "- table — Database table contained in a schema and grouping columns; Each table must have a table_id, table_name as data properties.\n"
        "- schema — Database schema grouping tables within a database catalog; Each schema must have a schema_id and a schema_name as data properties.\n"
        "- user — Subject/principal entitled to policy groups. Each user must have a user_id as data properties\n"
        "Relationships (create as many valid instances as possible):\n"
        "- (policy)-[:hasRowRule]->(column) — Policy includes row-level access conditions; row rule applies to a specific "
        "column. Each policy can have multiple row rules.\n"
        "- (policy)-[:hasColumnRule]->(column) — Policy includes column-level masking logic; mask rule applies to a "
        "specific column. Each policy can have multiple column rules.\n"
        "- (user)-[:memberOf]->(policy group) — User inherits policies through group membership.\n"
        "- (policy group)-[:includesPolicy]->(policy) — Policy groups bundle policies.\n"
        "- (table)-[:hasColumn]->(column) — Table contains one or more columns.\n"
        "- (schema)-[:hasTable]->(table) — Schema contains zero, one or more tables.\n"
        "Hard Constraints:\n"
        "- Always MERGE nodes and relationships by uri; never CREATE.\n"
        "- Every node must be labeled :owl__Class and include rdfs__label (lowercase words, space-separated) and "
        "skos__definition (no single quotes).\n"
        "- When MERGE a relationship, always MATCH nodes first, use WITH to pass variables."
        "- Every relationship must include uri, rdfs__label (lowercase words, space-separated), and skos__definition "
        "(no single quotes). If owl__minQualifiedCardinality and owl__maxQualifiedCardinality can be defined, include them "
        "on the relationship.\n"
        "- Relationship types must be camelCase, starting lowercase (hasRowRule, hasColumnRule, memberOf, includesPolicy).\n"
        f"- All uri(s) must use the domain {uri_domain}.\n"
        "- Add all annotation properties as metadata to both nodes and relationships (e.g., rdfs__label, skos__definition, "
        "and any provided annotations).\n"
        "- Include data properties for each concept. Include reasonable annotations as long as available.\n"
        "Output Rules:\n"
        "- Each statement must be valid Cypher and stand alone (e.g., MERGE … ON CREATE SET …;).\n"
        "- Always ensure MERGE targets use uri as the unique identifier.\n"
        "- Output must be strictly the JSON array of Cypher statements, nothing else.\n"
        "Next Step: Pass the output directly to tool modify_model, then run it.\n"
    )

    logger.debug(f"create_model_prompt - {prompt}")
    return [{"role": "system", "content": prompt}] + state["messages"]



# quick test
# state_of_input = {"messages": [{
#             "role": "user",
#             "content": "{user_input}"
#             }]}
# print(create_entitlement_model_prompt(state_of_input))