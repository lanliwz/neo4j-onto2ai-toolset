from agents.tax62n_db_connect import llm, graph
from chatbots.langgraph_state_model import *
from langgraph.graph import END, START, StateGraph
from agents.tax62n_query_examples import examples

from functools import partial

langgraph = StateGraph(OverallState, input=InputState, output=OutputState)

# def correct_cypher(state: OverallState):
#     return correct_cypher_syntax(state=state,graph=graph,llm=llm)
# langgraph.add_node(correct_cypher)

def guardrails(state: InputState):
    return guard_of_taxsystem(state=state,llm=llm)
langgraph.add_node(guardrails)

def gen_cypher(state: OverallState):
    return generate_cypher(state=state,graph=graph,llm=llm,examples=examples)


langgraph.add_node(gen_cypher)
# langgraph.add_node(validate_cypher)
# langgraph.add_node(correct_cypher)
# langgraph.add_node(execute_cypher)
# langgraph.add_node(generate_final_answer)
#
langgraph.add_edge(START, "guardrails")
langgraph.add_edge("guardrails", "gen_cypher")
langgraph.add_edge("gen_cypher", END)
# langgraph.add_edge("generate_cypher", "validate_cypher")
# langgraph.add_conditional_edges(
#     "validate_cypher",
#     validate_cypher_condition,
# )
# langgraph.add_edge("execute_cypher", "generate_final_answer")
# langgraph.add_edge("correct_cypher", "validate_cypher")
# langgraph.add_edge("generate_final_answer", END)
#
langgraph = langgraph.compile()
#
print(langgraph.invoke({"question": "what are the account payments in the year 2024, by account"}))