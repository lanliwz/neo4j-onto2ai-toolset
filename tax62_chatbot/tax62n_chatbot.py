from tax62_chatbot.tax62n_connect import llm, graph
from ai_graph_flow.langgraph_flow_model import *
from langgraph.graph import END, START, StateGraph
from tax62_chatbot.tax62n_query_examples import examples

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

def run_query(state: OverallState):
    return execute_graph_query(state, graph)
langgraph.add_node(run_query)
# langgraph.add_node(validate_cypher)
# langgraph.add_node(correct_cypher)

def final_result(state: OverallState):
    return generate_final_answer_g(state,llm)

langgraph.add_node(final_result)


# langgraph.add_node(execute_cypher)
# langgraph.add_node(generate_final_answer)
#
langgraph.add_edge(START, "guardrails")
langgraph.add_edge("guardrails", "gen_cypher")
langgraph.add_edge("gen_cypher", "run_query")
langgraph.add_edge("run_query", "final_result")
langgraph.add_edge("final_result", END)
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
# print(langgraph.invoke({"question": "what are the account payments in the year 2024, by account"}))
# print(langgraph.invoke({"question": "what is total tax of year 2022-2023?"}))
# print(langgraph.invoke({"question": "what is tax increase year over year?"}))
print(langgraph.invoke({"question": "what is tax increase year over year from 2023 to 2024?"}))