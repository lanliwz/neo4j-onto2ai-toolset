from typing import Literal, Annotated
from langgraph.graph import END, START, StateGraph
import operator

# Internal project imports
from neo4j_onto2ai_toolset.onto2ai_tool_config import (
    neo4j_bolt_url, username, password, neo4j_db_name, llm, graphdb
)
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_langraph_model import (
    OverallState, InputState, OutputState,
    more_question, generate_cypher, generate_pydantic_class,
    generate_relational_db_ddl, execute_graph_query,
    del_dup_cls_rels, review_schema, create_schema
)

# 1. Initialize DB Connection
db = SemanticGraphDB(neo4j_bolt_url, username, password, neo4j_db_name)

# 2. Modern Graph Definition
# We pass Input and Output schemas to ensure clear contract validation
builder = StateGraph(OverallState, input=InputState, output=OutputState)

# 3. Node Definitions
# In the modern way, we keep the nodes as simple functions that return state updates
builder.add_node("more_question", more_question)

builder.add_node("cypher_to_create_schema",
                 lambda state: create_schema(state=state, llm=llm))

builder.add_node("query_to_enhance_schema",
                 lambda state: generate_cypher(state=state, db=db, llm=llm))

builder.add_node("gen_pydantic_model",
                 lambda state: generate_pydantic_class(state=state, db=db, llm=llm))

builder.add_node("gen_relation_model",
                 lambda state: generate_relational_db_ddl(state=state, db=db, llm=llm))

builder.add_node("run_query",
                 lambda state: execute_graph_query(state, graphdb))

builder.add_node("del_dups",
                 lambda state: del_dup_cls_rels(state, graphdb))

builder.add_node("review_current_schema",
                 lambda state: review_schema(state=state, db=db))


# 4. Routing Logic
def router_logic(state: OverallState) -> Literal[
    "query_to_enhance_schema",
    "review_current_schema",
    "gen_pydantic_model",
    "gen_relation_model",
    "cypher_to_create_schema",
    "__end__"  # Use __end__ or END constant
]:
    next_act = state.get("next_action")
    todo = state.get("to_do_action")

    if next_act == "end":
        return END

    # Map actions to specific nodes
    routing_map = {
        ("schema", "enhance"): "query_to_enhance_schema",
        ("schema", "review"): "review_current_schema",
        ("schema", "create"): "cypher_to_create_schema",
        ("pydantic-model", None): "gen_pydantic_model",
        ("relation-model", None): "gen_relation_model",
    }

    # Return matched node or default to END
    return routing_map.get((next_act, todo if next_act == "schema" else None), END)


# 5. Edges and Compilation
builder.add_edge(START, "more_question")

# Conditional routing from the question node
builder.add_conditional_edges("more_question", router_logic)

# Execution paths
builder.add_edge("cypher_to_create_schema", "run_query")
builder.add_edge("query_to_enhance_schema", "run_query")
builder.add_edge("run_query", "del_dups")
builder.add_edge("del_dups", "more_question")

# Loops back to question for refinement
builder.add_edge("review_current_schema", "more_question")
builder.add_edge("gen_pydantic_model", "more_question")
builder.add_edge("gen_relation_model", "more_question")

# Compile into a Runnable
graph_app = builder.compile()