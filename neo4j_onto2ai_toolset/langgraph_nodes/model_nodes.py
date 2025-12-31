from typing import TypedDict, Any, List, Dict, Union
import asyncio

# Corrected Imports for modern LangChain
from langchain_classic.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, START, END
from langchain_core.agents import AgentFinish
from neo4j_onto2ai_toolset.onto2ai_tool_config import llm, graphdb

# from neo4j_onto2ai_toolset.onto2ai_tool_config import llm, graphdb

# 1. Define State
class AgentState(TypedDict, total=False):
    input: str
    concept: str
    namespace: str
    cypher_statements: List[str]
    intermediate_steps: List[Any]
    output: Any


# 2. Fix the Prompt and Agent Creation
# Added 'agent_scratchpad' and fixed the tool requirement
prompt = ChatPromptTemplate.from_messages([
    ("system", "You convert ontology schema into Cypher queries for Neo4j. Output ONLY Cypher statements as an array."),
    ("human", (
        "Context: {input}\n"
        "Namespace: {namespace}\n"
        "Concept: {concept}\n"
        "Requirements: Use rdfs__label, camelCase relationships, and provide statements in a clear list format."
    )),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# create_tool_calling_agent requires a tools list, even if empty.
# Note: Ensure 'llm' has .bind_tools() capability (e.g., ChatOpenAI or ChatVertexAI)
create_model_agent: Runnable = create_tool_calling_agent(
    llm=llm,
    tools=[],
    prompt=prompt
)


# 3. Improved Extraction Logic
def _extract_statements(raw_result: Any) -> List[str]:
    # Handling AgentFinish (The final output of the agent)
    if isinstance(raw_result, AgentFinish):
        out = raw_result.return_values.get("output", "")
    else:
        # Fallback for dict results or direct LLM calls
        out = raw_result.get("output", "") if isinstance(raw_result, dict) else str(raw_result)

    if not out:
        return []

    # Handle the specific bracketed format [ 'STMT1', 'STMT2' ]
    if isinstance(out, str):
        s = out.strip()
        if s.startswith("[") and s.endswith("]"):
            # A simple way to clean up the LLM's string representation of a list
            content = s[1:-1].strip()
            # Split by common delimiters while avoiding issues with internal commas
            return [stmt.strip().strip("'\"") for stmt in content.split(";") if stmt.strip()]
        return [s]
    return [str(out)]


# 4. Graph Node Function
def create_model_node(state: AgentState) -> AgentState:
    # Ensure scratchpad exists for the agent
    inputs = {
        "input": state.get("input", ""),
        "concept": state.get("concept", ""),
        "namespace": state.get("namespace", ""),
        "agent_scratchpad": state.get("intermediate_steps", [])
    }

    # Invoke the agent
    raw_result = create_model_agent.invoke(inputs)

    # Extract and Execute
    statements = _extract_statements(raw_result)
    exec_results = []

    for stmt in statements:
        try:
            # res = graphdb.query(stmt)
            # exec_results.append(str(res))
            exec_results.append(f"Successfully simulated: {stmt[:30]}...")
        except Exception as e:
            exec_results.append(f"Error: {str(e)}")

    # Return the updated state keys
    return {
        "cypher_statements": statements,
        "output": exec_results,
        "intermediate_steps": state.get("intermediate_steps", []) + [raw_result]
    }


# 5. Build and Compile
workflow = StateGraph(AgentState)
workflow.add_node("create_model_node", create_model_node)
workflow.add_edge(START, "create_model_node")
workflow.add_edge("create_model_node", END)

app = workflow.compile()