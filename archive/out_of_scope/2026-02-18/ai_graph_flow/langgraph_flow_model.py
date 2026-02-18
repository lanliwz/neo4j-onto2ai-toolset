from langchain_chroma import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from neo4j.exceptions import CypherSyntaxError
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from typing import Annotated, List, Literal, Optional
from operator import add
from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector, Schema


class InputState(TypedDict):
    question: str


class OverallState(TypedDict):
    question: str
    next_action: str
    cypher_statement: str
    cypher_errors: List[str]
    database_records: List[dict]
    steps: Annotated[List[str], add]


class OutputState(TypedDict):
    answer: str
    steps: List[str]
    cypher_statement: str


class Property(BaseModel):
    """
    Represents a filter condition based on a specific node property in a graph in a Cypher statement.
    """

    node_label: str = Field(
        description="The label of the node to which this property belongs."
    )
    property_key: str = Field(description="The key of the property being filtered.")
    property_value: str = Field(
        description="The value that the property is being matched against."
    )


class ValidateCypherOutput(BaseModel):
    """
    Represents the validation result of a Cypher query's output,
    including any errors and applied filters.
    """

    errors: Optional[List[str]] = Field(
        description="A list of syntax or semantical errors in the Cypher statement. Always explain the discrepancy between schema and Cypher statement"
    )
    filters: Optional[List[Property]] = Field(
        description="A list of property-based filters applied in the Cypher statement."
    )


def more_question(state: OverallState) -> OutputState:
    """
    Decides if more question need to ask
    """
    next_question = "get next question from keyboard input"
    return {"question": next_question, "steps": ["more_question"]}


def generate_cypher(state: OverallState, graph: Neo4jGraph, llm: ChatOpenAI, examples: []) -> OverallState:
    """
    Generates a cypher statement based on the provided schema and user input
    """
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples, OpenAIEmbeddings(), Chroma, k=4, input_keys=["question"]
    )
    text2cypher_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Given an input question, convert it to a Cypher query. No pre-amble."
                    "Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
                ),
            ),
            (
                "human",
                (
                    """You are a Neo4j expert. Given an input question, create a syntactically correct Cypher query to run.
                    Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!
                    Here is the schema information
                    {schema}

                    Below are a number of examples of questions and their corresponding Cypher queries.

                    {fewshot_examples}

                    User input: {question}
                    Cypher query:"""
                ),
            ),
        ]
    )

    text2cypher_chain = text2cypher_prompt | llm | StrOutputParser()

    NL = "\n"
    fewshot_examples = (NL * 2).join(
        [
            f"Question: {el['question']}{NL}Cypher:{el['query']}"
            for el in example_selector.select_examples(
            {"question": state.get("question")}
        )
        ]
    )
    generated_cypher = text2cypher_chain.invoke(
        {
            "question": state.get("question"),
            "fewshot_examples": fewshot_examples,
            "schema": graph.schema,
        }
    )
    return {"cypher_statement": generated_cypher, "steps": ["generate_cypher"]}


def correct_cypher_syntax(state: OverallState, graph: Neo4jGraph, llm: ChatOpenAI) -> OverallState:
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


def guard_of_taxsystem(state: InputState, llm: ChatOpenAI) -> OverallState:
    class GuardOfTaxSystemOutput(BaseModel):
        decision: Literal["continue", "end"] = Field(
            description="Decision on whether the question is related to tax, payment, billing etc"
        )

    guard_of_entrance = """
    As an intelligent assistant, your primary objective is to decide whether a given question is related to tax/account/balance/billing/payment or not. 
    If the question is related, output "continue". Otherwise, output "end".
    To make this decision, assess the content of the question and determine if it refers to any account balance, transaction, billing, payment, 
    or related topics. Provide only the specified output: "continue" or "end".
    """

    guard_of_entrance_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                guard_of_entrance,
            ),
            (
                "human",
                ("{question}"),
            ),
        ]
    )
    guard_of_entrance_chain = guard_of_entrance_prompt | llm.with_structured_output(GuardOfTaxSystemOutput)
    output = guard_of_entrance_chain.invoke({"question": state.get("question")})
    database_records = None
    if output.decision == "end":
        database_records = "This questions is not about tax/account/balance/billing/payment. Therefore I cannot answer this question."
    return {
        "next_action": output.decision,
        "database_records": database_records,
        "steps": ["guardrail"],
    }


def validate_cypher(state: OverallState, graph: Neo4jGraph, llm: ChatOpenAI) -> OverallState:
    """
    Validates the Cypher statements and maps any property values to the database.
    """
    validate_cypher_system = """
    You are a Cypher expert reviewing a statement written by a junior developer.
    """

    validate_cypher_user = """You must check the following:
    * Are there any syntax errors in the Cypher statement?
    * Are there any missing or undefined variables in the Cypher statement?
    * Are any node labels missing from the schema?
    * Are any relationship types missing from the schema?
    * Are any of the properties not included in the schema?
    * Does the Cypher statement include enough information to answer the question?

    Examples of good errors:
    * Label (:Foo) does not exist, did you mean (:Bar)?
    * Property bar does not exist for label Foo, did you mean baz?
    * Relationship FOO does not exist, did you mean FOO_BAR?

    Schema:
    {schema}

    The question is:
    {question}

    The Cypher statement is:
    {cypher}

    Make sure you don't make any mistakes!"""

    validate_cypher_prompt = ChatPromptTemplate.from_messages(
        [

            (
                "system",
                validate_cypher_system,
            ),
            (
                "human",
                (validate_cypher_user),
            ),
        ]
    )
    chain = validate_cypher_prompt | llm.with_structured_output(ValidateCypherOutput)

    errors = []
    mapping_errors = []
    # Check for syntax errors
    try:
        graph.query(f"EXPLAIN {state.get('cypher_statement')}")
    except CypherSyntaxError as e:
        errors.append(e.message)
    # Experimental feature for correcting relationship directions
    corrected_cypher = correct_cypher_syntax(state.get("cypher_statement"), graph, llm)
    if not corrected_cypher:
        errors.append("The generated Cypher statement doesn't fit the graph schema")
    if not corrected_cypher == state.get("cypher_statement"):
        print("Relationship direction was corrected")
    # Use LLM to find additional potential errors and get the mapping for values
    llm_output = chain.invoke(
        {
            "question": state.get("question"),
            "schema": graph.schema,
            "cypher": state.get("cypher_statement"),
        }
    )
    if llm_output.errors:
        errors.extend(llm_output.errors)

    if mapping_errors:
        next_action = "end"
    elif errors:
        next_action = "correct_cypher"
    else:
        next_action = "execute_cypher"

    return {
        "next_action": next_action,
        "cypher_statement": corrected_cypher,
        "cypher_errors": errors,
        "steps": ["validate_cypher"],
    }


def execute_graph_query(state: OverallState, graph: Neo4jGraph) -> OverallState:
    """
    Executes the given Cypher statement.
    """
    no_results = "I couldn't find any relevant information in the database"
    records = graph.query(state.get("cypher_statement"))
    # logging.info(state.get("cypher_statement"))
    return {
        "database_records": records if records else no_results,
        "next_action": "end",
        "steps": ["execute_cypher"],
    }


def generate_final_answer_g(state: OverallState, llm: ChatOpenAI) -> OutputState:
    """
    Decides if the question is related to movies.
    """
    generate_final_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a helpful assistant",
        ),
        (
            "human",
            (
                """Use the following results retrieved from a database to provide
                    a succinct, definitive answer to the user's question.

                    Respond as if you are answering the question directly.

                    Results: {results}
                    Question: {question}"""
            ),
        ),
    ])

    generate_final_chain = generate_final_prompt | llm | StrOutputParser()

    final_answer = generate_final_chain.invoke(
        {"question": state.get("question"), "results": state.get("database_records")}
    )
    return {"answer": final_answer, "steps": ["generate_final_answer"]}
