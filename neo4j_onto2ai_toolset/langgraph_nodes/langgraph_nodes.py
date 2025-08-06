import logging
from typing import Literal

from langgraph.graph import END, START, StateGraph

from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import (
    neo4j_bolt_url,
    username,
    password,
    neo4j_db_name)

from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import llm, graphdb
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_langraph_model import (
    OverallState,
    generate_cypher,
    execute_graph_query,
    del_dup_cls_rels,
    create_schema)

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)

# node
def cypher_to_create_schema(state: OverallState):
    return create_schema(state=state,llm=llm)

# node
def query_to_enhance_schema(state: OverallState):
    return generate_cypher(state=state,db=db,llm=llm)


# node
def run_query(state: OverallState):
    execute_graph_query(state=state,db=graphdb)

# node
def del_dups(state: OverallState):
    del_dup_cls_rels(state=state,db=graphdb)



