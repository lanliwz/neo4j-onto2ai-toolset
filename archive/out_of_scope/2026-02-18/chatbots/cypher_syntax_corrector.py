from ai_graph_flow.langgraph_flow_model import *
from chatbots.llm_neo4j_connect import *


# Cypher query corrector is experimental
corrector_schema = [
    Schema(el["start"], el["type"], el["end"])
    for el in graph.structured_schema.get("relationships")
]
cypher_query_corrector = CypherQueryCorrector(corrector_schema)

correct_cypher_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a Cypher expert reviewing a statement written by a junior developer. "
                "You need to correct the Cypher statement based on the provided errors. No pre-amble."
                "Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
            ),
        ),
        (
            "human",
            (
                """Check for invalid syntax or semantics and return a corrected Cypher statement.

Schema:
{schema}

Note: Do not include any explanations or apologies in your responses.
Do not wrap the response in any backticks or anything else.
Respond with a Cypher statement only!

Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.

The question is:
{question}

The Cypher statement is:
{cypher}

The errors are:
{errors}

Corrected Cypher statement: """
            ),
        ),
    ]
)

correct_cypher_chain = correct_cypher_prompt | llm | StrOutputParser()


def correct_cypher(state: OverallState) -> OverallState:
    """
    Correct the Cypher statement based on the provided errors.
    """
    corrected_cypher = correct_cypher_chain.invoke(
        {
            "question": state.get("question"),
            "errors": state.get("cypher_errors"),
            "cypher": state.get("cypher_statement"),
            "schema": graph.schema,
        }
    )

    return {
        "next_action": "validate_cypher",
        "cypher_statement": corrected_cypher,
        "steps": ["correct_cypher"],
    }

def correct_cypher_syntax(state: OverallState, graph:Neo4jGraph, llm: ChatOpenAI) -> OverallState:
    corrector_schema = [
        Schema(el["start"], el["type"], el["end"])
        for el in graph.structured_schema.get("relationships")
    ]
    cypher_query_corrector = CypherQueryCorrector(corrector_schema)
    correct_cypher_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are a Cypher expert reviewing a statement written by a junior developer. "
                    "You need to correct the Cypher statement based on the provided errors. No pre-amble."
                    "Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
                ),
            ),
            (
                "human",
                (
                    """Check for invalid syntax or semantics and return a corrected Cypher statement.
                        Schema: {schema}                   
                        Note: Do not include any explanations or apologies in your responses.
                        Do not wrap the response in any backticks or anything else.
                        Respond with a Cypher statement only!                   
                        Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.                    
                        The question is: {question}                   
                        The Cypher statement is: {cypher}                   
                        The errors are: {errors}                    
                        Corrected Cypher statement: 
                        """
                ),
            ),
        ]
    )
    correct_cypher_chain = correct_cypher_prompt | llm | StrOutputParser()
    corrected_cypher = correct_cypher_chain.invoke(
        {
            "question": state.get("question"),
            "errors": state.get("cypher_errors"),
            "cypher": state.get("cypher_statement"),
            "schema": graph.schema,
        }
    )

    return {
        "next_action": "validate_cypher",
        "cypher_statement": corrected_cypher,
        "steps": ["correct_cypher"],
    }