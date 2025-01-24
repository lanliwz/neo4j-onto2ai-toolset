from chatbots.cypher_syntax_corrector import correct_cypher
from chatbots.cypher_runner import execute_cypher
from chatbots.cypher_exception_handler import validate_cypher
from chatbots.cypher_krag_utl import *
from langgraph.graph import END, START, StateGraph


langgraph = StateGraph(OverallState, input=InputState, output=OutputState)
langgraph.add_node(guardrails)
langgraph.add_node(generate_cypher)
langgraph.add_node(validate_cypher)
langgraph.add_node(correct_cypher)
langgraph.add_node(execute_cypher)
langgraph.add_node(generate_final_answer)

langgraph.add_edge(START, "guardrails")
langgraph.add_conditional_edges(
    "guardrails",
    guardrails_condition,
)
langgraph.add_edge("generate_cypher", "validate_cypher")
langgraph.add_conditional_edges(
    "validate_cypher",
    validate_cypher_condition,
)
langgraph.add_edge("execute_cypher", "generate_final_answer")
langgraph.add_edge("correct_cypher", "validate_cypher")
langgraph.add_edge("generate_final_answer", END)

langgraph = langgraph.compile()

# print(langgraph.invoke({"question": "what are the account payments in the year 2024, group by account"}))
print(langgraph.invoke({"question": "what are the total account payments in the year 2024, by account?"}))
