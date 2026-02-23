from typing import Any, List

from langchain_classic.agents import create_tool_calling_agent
from langchain_core.agents import AgentFinish
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph

from neo4j_onto2ai_toolset.langgraph_nodes.types import AgentState
from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm

# No LLM/tool initialization at import time.
_CREATE_MODEL_AGENT: Runnable | None = None
_APP = None

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You convert ontology schema into Cypher queries for Neo4j. Output ONLY Cypher statements as an array."),
        (
            "human",
            (
                "Context: {input}\n"
                "Namespace: {namespace}\n"
                "Concept: {concept}\n"
                "Requirements: Use rdfs__label, camelCase relationships, and provide statements in a clear list format."
            ),
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


def _get_create_model_agent() -> Runnable:
    global _CREATE_MODEL_AGENT
    if _CREATE_MODEL_AGENT is None:
        _CREATE_MODEL_AGENT = create_tool_calling_agent(
            llm=get_llm(),
            tools=[],
            prompt=_prompt,
        )
    return _CREATE_MODEL_AGENT


def _extract_statements(raw_result: Any) -> List[str]:
    if isinstance(raw_result, AgentFinish):
        out = raw_result.return_values.get("output", "")
    else:
        out = raw_result.get("output", "") if isinstance(raw_result, dict) else str(raw_result)

    if not out:
        return []

    if isinstance(out, str):
        s = out.strip()
        if s.startswith("[") and s.endswith("]"):
            content = s[1:-1].strip()
            return [stmt.strip().strip("'\"") for stmt in content.split(";") if stmt.strip()]
        return [s]
    return [str(out)]


def create_model_node(state: AgentState) -> AgentState:
    inputs = {
        "input": state.get("input", ""),
        "concept": state.get("concept", ""),
        "namespace": state.get("namespace", ""),
        "agent_scratchpad": state.get("intermediate_steps", []),
    }

    raw_result = _get_create_model_agent().invoke(inputs)

    statements = _extract_statements(raw_result)
    exec_results: List[str] = [f"Successfully simulated: {stmt[:30]}..." for stmt in statements]

    return {
        "cypher_statements": statements,
        "output": exec_results,
        "intermediate_steps": state.get("intermediate_steps", []) + [raw_result],
    }


def get_app():
    global _APP
    if _APP is None:
        workflow = StateGraph(AgentState)
        workflow.add_node("create_model_node", create_model_node)
        workflow.add_edge(START, "create_model_node")
        workflow.add_edge("create_model_node", END)
        _APP = workflow.compile()
    return _APP
