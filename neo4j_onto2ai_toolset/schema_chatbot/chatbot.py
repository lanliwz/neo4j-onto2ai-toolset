from typing import Literal, Annotated
from langgraph.graph import END, START, StateGraph
import operator

# Internal project imports
from neo4j_onto2ai_toolset.onto2ai_tool_config import neo4j_model, graphdb
from neo4j_onto2ai_toolset.onto2ai_utility import (
    Neo4jDatabase, get_schema,
    OverallState, InputState, OutputState,
    classify_intent, generate_cypher_node, generate_pydantic_class_node,
    generate_relational_db_ddl, execute_query_node,
    del_dup_node, review_schema, create_schema_node
)

# 1. Initialize DB Connection
db = Neo4jDatabase(neo4j_model.url, neo4j_model.username, neo4j_model.password, neo4j_model.database)

# 2. Modern Graph Definition
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 3. Node Definitions (Async wrappers for dependency injection)
async def review_node(state: OverallState):
    return await review_schema(state, db)

async def enhance_node(state: OverallState):
    return await generate_cypher_node(state, db)

async def pydantic_node(state: OverallState):
    return await generate_pydantic_class_node(state, db)

async def relational_node(state: OverallState):
    return await generate_relational_db_ddl(state, db)

builder.add_node("classify", classify_intent)
builder.add_node("review", review_node)
builder.add_node("enhance", enhance_node)
builder.add_node("create", create_schema_node)
builder.add_node("gen_pydantic", pydantic_node)
builder.add_node("gen_relational", relational_node)
builder.add_node("execute_query", execute_query_node)
builder.add_node("cleanup", del_dup_node)

# 4. Routing Logic
def router(state: OverallState) -> str:
    action = state.get("next_action")
    todo = state.get("to_do_action")
    
    if action == "end": return END
    if action == "pydantic-model": return "gen_pydantic"
    if action == "relation-model": return "gen_relational"
    if action == "schema":
        if todo == "review": return "review"
        if todo == "enhance": return "enhance"
        if todo == "create": return "create"
        
    return END

# 5. Edges and Compilation
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", router)

# Paths that update the DB
builder.add_edge("create", "execute_query")
builder.add_edge("enhance", "execute_query")
builder.add_edge("execute_query", "cleanup")
builder.add_edge("cleanup", END)

# Paths that just generate code or review
builder.add_edge("review", END)
builder.add_edge("gen_pydantic", END)
builder.add_edge("gen_relational", END)

# Compile into a Runnable
graph_app = builder.compile()