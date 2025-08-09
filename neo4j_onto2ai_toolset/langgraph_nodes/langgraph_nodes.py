# LangGraph: build a minimal StateGraph and invoke it
from typing import TypedDict, Any, List
from langgraph.graph import StateGraph, END

from neo4j_onto2ai_toolset.langraph_agents.model_agents import create_model_agent


# ---- Define state ----
class AgentState(TypedDict, total=False):
    input: str
    concept: str
    namespace: str
    intermediate_steps: List[Any]
    output: Any

# ---- Assume you already have a runnable/agent ----
# e.g., create_model_agent: RunnableLike that accepts a dict and returns a result
# from langchain_core.runnables import Runnable
# create_model_agent: Runnable = ...

def create_model_node(state: AgentState) -> AgentState:
    result = create_model_agent.invoke({
        "concept": state["concept"],
        "namespace": state["namespace"],
        "intermediate_steps": state.get("intermediate_steps", [])
    })
    return {
        "input": state.get("input", ""),
        "output": result,
        "intermediate_steps": state.get("intermediate_steps", []),
        "concept": state["concept"],
        "namespace": state["namespace"],
    }

# ---- Build the graph ----
graph = StateGraph(AgentState)
graph.add_node("create_model_node", create_model_node)
graph.add_edge("__start__", "create_model_node")
graph.add_edge("create_model_node", END)

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