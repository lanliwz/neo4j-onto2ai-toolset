import json
from typing import Annotated, List, Union, Dict, Any, Literal, Optional
from typing_extensions import TypedDict
from operator import add

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field

from tax62_chatbot.tax62n_connect import llm, graph
from tax62_chatbot.tax62n_query_examples import examples

# --- State Definition ---

class TaxChatState(TypedDict):
    """Modern LangGraph state for the Tax Chatbot."""
    messages: Annotated[List[BaseMessage], add_messages]
    cypher_statement: Optional[str]
    cypher_errors: Annotated[List[str], add]
    database_records: Optional[Union[str, List[Dict[str, Any]]]]
    next_action: Optional[str]

# --- Structured Output Models ---

class GuardDecision(BaseModel):
    decision: Literal["continue", "end"] = Field(
        description="Whether to continue the conversation or end it because the topic is unrelated to taxes/payments."
    )

# --- Node Functions ---

async def guard_node(state: TaxChatState):
    """Checks if the user's latest message is related to the domain."""
    system_msg = """
    As an intelligent assistant, your primary objective is to decide whether the user's inquiry is related to tax, account, balance, billing, or payment. 
    If it is, output "continue". Otherwise, output "end".
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm.with_structured_output(GuardDecision)
    last_message = state["messages"][-1]
    
    # We pass all messages to give context (e.g. if the user says "tell me more")
    result = await chain.ainvoke({"messages": state["messages"]})
    
    if result.decision == "end":
        return {
            "messages": [AIMessage(content="I'm sorry, I can only assist with tax, account, and payment related questions.")],
            "next_action": "end"
        }
    
    return {"next_action": "continue"}
async def generate_cypher_node(state: TaxChatState):
    """Generates a Cypher query based on the conversation history and schema."""
    
    # Simple few-shot formatting
    fewshot_text = "\n\n".join([f"Question: {ex['question']}\nCypher: {ex['query']}" for ex in examples[:5]])
    
    # Escape curly braces for ChatPromptTemplate
    schema_escaped = graph.schema.replace("{", "{{").replace("}", "}}")
    fewshot_escaped = fewshot_text.replace("{", "{{").replace("}", "}}")
    
    system_msg = f"""
    You are a Neo4j expert. Convert the user's request into a valid Cypher query based on the following schema:
    {schema_escaped}
    
    Use the following examples for guidance:
    {fewshot_escaped}
    
    Respond ONLY with the Cypher query. No markdown, no backticks.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    # Clean up any potential markdown fences in output
    raw_cypher = await chain.ainvoke({"messages": state["messages"]})
    cypher = raw_cypher.replace("```cypher", "").replace("```", "").strip()
    
    return {"cypher_statement": cypher}

async def execute_query_node(state: TaxChatState):
    """Executes the generated Cypher query."""
    cypher = state.get("cypher_statement")
    if not cypher:
        return {"database_records": "No query generated."}
    
    try:
        records = graph.query(cypher)
        return {"database_records": records if records else "No records found."}
    except Exception as e:
        return {"cypher_errors": [str(e)], "database_records": f"Error executing query: {e}"}

async def final_answer_node(state: TaxChatState):
    """Generates the final natural language answer."""
    results = state.get("database_records")
    
    system_msg = """
    You are a helpful tax and payment assistant. 
    Use the database results provided to answer the user's question accurately.
    If no results were found, inform the user politely.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "Database results: {results}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    answer = await chain.ainvoke({"messages": state["messages"], "results": str(results)})
    
    return {"messages": [AIMessage(content=answer)]}

# --- Router Logic ---

def should_continue(state: TaxChatState):
    if state.get("next_action") == "end":
        return END
    return "generate_cypher"

# --- Graph Construction ---

builder = StateGraph(TaxChatState)

builder.add_node("guard", guard_node)
builder.add_node("generate_cypher", generate_cypher_node)
builder.add_node("execute_query", execute_query_node)
builder.add_node("final_answer", final_answer_node)

builder.add_edge(START, "guard")
builder.add_conditional_edges("guard", should_continue)
builder.add_edge("generate_cypher", "execute_query")
builder.add_edge("execute_query", "final_answer")
builder.add_edge("final_answer", END)

# In-memory persistence for multi-turn chat
memory = InMemorySaver()
tax_chatbot_graph = builder.compile(checkpointer=memory)
