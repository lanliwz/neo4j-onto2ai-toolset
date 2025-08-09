# LangGraph: build a minimal StateGraph and invoke it
from typing import TypedDict, Any, List
from langgraph.graph import StateGraph, END
from neo4j_onto2ai_toolset.logger_config import logger as mylogger


from neo4j_onto2ai_toolset.langraph_agents.model_agents import create_model_agent, graphdb

# ---- Define state ----
class AgentState(TypedDict, total=False):
    input: str
    concept: str
    namespace: str
    intermediate_steps: List[Any]
    output: Any

def execute_cypher_statement(statements: List[str]) -> List[str]:
    """
    Executes the given Cypher statements.

    Parameters:
        statements (List[str]): List of Cypher statement strings.

    Returns:
        List[str]: The stringified query results or error messages for each statement.
    """
    results: List[str] = []
    for stmt in statements:
        print(stmt)
        try:
            res = graphdb.query(stmt)  # assumes graphdb.query returns something serializable
            results.append(str(res))
        except Exception as e:
            print(e)
            results.append(f"Error: {str(e)}")
    return results

def execute_cypher_node(state: AgentState) -> AgentState:
    raw_result   = execute_cypher_statement(state["output"])
    output_value = raw_result.get("output") if isinstance(raw_result, dict) else raw_result
    return {
        "input": state.get("input", ""),
        "output": output_value,
        "intermediate_steps": state.get("intermediate_steps", []),
    }

from typing import Any, List, Dict, Union
from langchain_core.agents import AgentFinish
import json

def unwrap_agent_result(res: Any) -> Any:
    """Return the 'output' (or raw return_values) if res is AgentFinish; else return res."""
    if isinstance(res, AgentFinish):
        # Most ReAct agents put the final text under return_values["output"]
        print(res.return_values.get("output", res.return_values))
        return res.return_values.get("output", res.return_values)
    return res

def normalize_statements(payload: Union[str, List[str], Dict[str, Any]]) -> List[str]:
    """
    Convert various payload shapes to List[str] statements.
    Accepts:
      - JSON array string
      - newline-separated string
      - dict with 'statements' or 'output'
      - already a list of strings
    """
    if isinstance(payload, list):
        return [str(s).strip() for s in payload if str(s).strip()]

    if isinstance(payload, dict):
        if "statements" in payload and isinstance(payload["statements"], list):
            return [str(s).strip() for s in payload["statements"] if str(s).strip()]
        if "output" in payload:
            return normalize_statements(payload["output"])

    if isinstance(payload, str):
        s = payload.strip()
        # Try JSON first
        try:
            maybe = json.loads(s)
            return normalize_statements(maybe)
        except Exception:
            # Fallback: split by lines or commas
            if "\n" in s:
                return [line.strip() for line in s.splitlines() if line.strip()]
            if s.startswith("[") and s.endswith("]"):
                # Not valid JSON? do a naive split
                inner = s[1:-1]
                return [part.strip().strip('"').strip("'") for part in inner.split(",") if part.strip()]
            return [s] if s else []

    # Last resort
    return [str(payload)]

# ---- Your node/tool call flow ----

def create_model_node(state: dict) -> dict:
    raw_result = create_model_agent.invoke({
        "concept": state["concept"],
        "namespace": state["namespace"],
        "intermediate_steps": state.get("intermediate_steps", [])
    })

    # 1) Unwrap AgentFinish -> dict/str
    payload = unwrap_agent_result(raw_result)

    # 2) Normalize to the tool’s expected argument shape
    statements: List[str] = normalize_statements(payload)

    # If your tool schema is: ExecuteCypherStatement(statements: List[str])
    tool_input: Dict[str, Any] = {"statements": statements}

    # EITHER: directly call the tool
    # execute_cypher_statement.invoke(tool_input)

    # OR: return state for a ToolNode to consume
    return {
        "input": state.get("input", ""),
        "output": statements,                 # keep the plain statements if you also want them in state
        "tool_name": "execute_cypher_statement",
        "tool_input": tool_input,             # <-- dict, not AgentFinish
        "intermediate_steps": state.get("intermediate_steps", []),
        "concept": state["concept"],
        "namespace": state["namespace"],
    }

# ---- Build the graph ----
graph = StateGraph(AgentState)
graph.add_node("create_model_node", create_model_node)
graph.add_node("execute_cypher_node",execute_cypher_node)
graph.add_edge("__start__", "create_model_node")
graph.add_edge("create_model_node","execute_cypher_node")
graph.add_edge("execute_cypher_node", END)

app = graph.compile()

# ---- Invoke it ----
initial_state: AgentState = {
    "input": "Create/merge ontology-backed model node",
    "concept": "Cash Account",
    "namespace": "http://example.com/ontology/",
    "intermediate_steps": [],  # ensure key exists to avoid KeyError in agents expecting it
}

result_state = app.invoke(initial_state)

# ---- Use the result ----
print("Final output:", result_state["output"])