from llm_neo4j_connect import *
from langgraph_state_model import *

def execute_cypher(state: OverallState) -> OverallState:
    """
    Executes the given Cypher statement.
    """
    no_results = "I couldn't find any relevant information in the database"
    records = graph.query(state.get("cypher_statement"))
    # logging.info(state.get("cypher_statement"))
    return {
        "database_records": records if records else no_results,
        "next_action": "end",
        "steps": ["execute_cypher"],
    }

def execute_cypher_g(state: OverallState, graph: Neo4jGraph) -> OverallState:
    """
    Executes the given Cypher statement.
    """
    no_results = "I couldn't find any relevant information in the database"
    records = graph.query(state.get("cypher_statement"))
    # logging.info(state.get("cypher_statement"))
    return {
        "database_records": records if records else no_results,
        "next_action": "end",
        "steps": ["execute_cypher"],
    }