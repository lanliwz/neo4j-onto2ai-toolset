from typing import TypedDict, Any, List, Dict, Union

from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, START, END
from langchain_core.agents import AgentFinish
from neo4j_onto2ai_toolset.schema_chatbot.onto2ai_tool_connections import llm, graphdb

class AgentState(TypedDict, total=False):
    input: str
    concept: str
    namespace: str
    cypher_statements: List[str]
    intermediate_steps: List[Any]
    output: Any

create_model_agent: Runnable = create_tool_calling_agent(
    llm=llm,
    tools=[],
    prompt=ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are to convert ontology schema information into Cypher queries for Neo4j, following specific formatting and metadata rules."
                "Your responses must strictly follow the requirements below."
            ),
        ),
        (
            "human",
            (
                "Context: Ontology-driven Cypher query generation for Neo4j graph database.\n"
                "Objective: Given a concept (may be a URL or text) and a namespace, generate an array of Cypher statements to add or merge nodes (owl:Class) and relationships with properties, using the ontology conventions below.\n"
                "Style: Output must be Cypher statements only, no explanations or wrappers, with each statement as an array element.\n"
                "Audience: Technical users working with ontology-based Neo4j graphs.\n"
                "Requirements:\n"
                "- Each node is an owl:Class with rdfs__label (lowercase, space-separated).\n"
                "- Add all annotation properties as metadata to both nodes and relationships.\n"
                "- Merge nodes if already exist.\n"
                "- Relationship type is camelCase, first letter lowercase; add owl__minQualifiedCardinality if possible.\n"
                "- All nodes/relationships have uri with HTTP and the provided domain.\n"
                "- Each node/relationship includes skos__definition (no single quotes).\n"
                "- Match nodes only with rdfs__label.\n"
                "- Find and add as many relationships as possible.\n"
                "- Absolutely do not include any explanations, apologies, preamble, or backticks in your responses.\n"
                "\n"
                "Inputs:\n"
                "namespace: {namespace}\n"
                "concept: {concept}"
            ),
        ),
    MessagesPlaceholder("agent_scratchpad"),
])
)
def _extract_statements(raw_result: Union[Dict[str, Any], AgentFinish]) -> List[str]:
    # 1) pull "output" or "cypher_statements" from dict/AgentFinish
    if isinstance(raw_result, AgentFinish):
        rv = raw_result.return_values or {}
        stmts = rv.get("cypher_statements")
        out = rv.get("output")
    else:
        stmts = raw_result.get("cypher_statements")
        out = raw_result.get("output")

    # Prefer explicit list
    if isinstance(stmts, list):
        return [str(s).strip() for s in stmts if str(s).strip()]

    if out is None:
        return []

    # If it's already a list, coerce to strings
    if isinstance(out, list):
        return [str(s).strip() for s in out if str(s).strip()]

    # If it's a string, attempt to normalize special "[ ... , ... , ... ]" block
    if isinstance(out, str):
        s = out.strip()
        # Case 1: proper semicolon-separated
        if ";" in s and not s.startswith("["):
            return [st.strip() for st in s.split(";") if st.strip()]
        # Case 2: bracketed comma-separated block produced by the LLM
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            # split only on commas that start a new Cypher clause (MERGE/MATCH/CREATE/etc.)
            # here we handle your exact pattern with MERGE boundaries
            parts: List[str] = []
            buf = []
            for line in inner.splitlines():
                if line.strip().startswith("MERGE ") and buf:
                    parts.append("\n".join(buf).strip().rstrip(","))
                    buf = [line]
                else:
                    buf.append(line)
            if buf:
                parts.append("\n".join(buf).strip().rstrip(","))

            # If we got the classic 3-part MERGE n / MERGE m / MERGE (n)-[...] pattern,
            # fold them into ONE statement with WITH to carry variables.
            if len(parts) >= 3 and parts[0].startswith("MERGE (n") and parts[1].startswith("MERGE (m") and parts[2].startswith("MERGE (n)-"):
                combined = f"""{parts[0]}
WITH n
{parts[1]}
WITH n, m
{parts[2]}"""
                return [combined.strip()]
            # Otherwise return each as its own statement (they must be independently valid)
            return [p for p in parts if p]

        # Fallback: single raw statement
        return [s]

    # Last resort
    return [str(out)]


def create_model_node(state: AgentState) -> AgentState:
    steps: List[Any] = list(state.get("intermediate_steps", []))
    raw_result = create_model_agent.invoke({
        "concept": state["concept"],
        "namespace": state["namespace"],
        "intermediate_steps": steps
    })
    steps.append({"create_model_agent_result": str(raw_result)})

    statements = _extract_statements(raw_result)

    exec_results: List[str] = []
    for stmt in statements:
        try:
            res = graphdb.query(stmt)
            exec_results.append(str(res))
        except Exception as e:
            exec_results.append(f"Error executing:\n{stmt}\n{e}")

    return {
        "cypher_statements": statements,
        "output": exec_results,
        "intermediate_steps": steps,
    }

# ---- Build the graph ----
graph = StateGraph(AgentState)
graph.add_node("create_model_node", create_model_node)
graph.add_edge(START, "create_model_node")
graph.add_edge("create_model_node", END)
app = graph.compile()

# ---- Invoke it ----
initial_state: AgentState = {
    "input": "Create/merge ontology-backed model node",
    "concept": "Check Account",
    "namespace": "http://example.com/ontology/",
    "intermediate_steps": [],
}

result_state = app.invoke(initial_state)
print("Executed statements:", result_state.get("cypher_statements"))
print("Final output:", result_state.get("output"))