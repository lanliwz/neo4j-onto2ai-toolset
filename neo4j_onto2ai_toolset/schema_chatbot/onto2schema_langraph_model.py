import json
from operator import add
from typing import Annotated, List, Literal, Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import SemanticGraphDB, get_schema
from neo4j_onto2ai_toolset.prompts.onto2schema_prompt import gen_prompt4schema, gen_pydantic_class
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import *
from neo4j_onto2ai_toolset.logger_config import logger as mylogger




class InputState(TypedDict):
    question: str
    start_node: str
    init: str = "init"

class OverallState(TypedDict):
    to_do_action: str
    start_node: str
    question: str
    domain: str
    based_on: str
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
    class Decision(BaseModel):
        decision: Literal["schema","pydantic-model","relation-model", "based_on","domain","end"] = Field(
            description="Decision on whether the question is related to ontology or schema etc"
        )
        start_node: str = Field(
            description="class label or node label"
        )
        action: Literal["review", "enhance","create"] = Field(
            description="whether the question is related to review, enhance or create schema etc"
        )
        based_on: str = Field(
            description="The link in the question or the description after 'base on'?"
        )
        domain: str = Field(
            description="extract domain from the link or the url provided in the question"
        )

    guard_of_entrance = """
    As an intelligent assistant, your primary objective is to decide whether a given question is related to schema, model, ontology, then provide structured response.
    If the question is related, and at least one class name or node label provided in the question as schema, output the class label or node label in lower case as start_node.
    To make this decision, assess the content of the question.
    If it refers to get ontology/schema, output decision=schema.
    If it refers to generate pydantic model, output decision=pydantic-model.  
    If it refers to generate relation model, output decision=relation-model.  
    Otherwise, output decision=end
    """
    guard_of_entrance_prompt = ChatPromptTemplate.from_messages(    [
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
    db_records = ""
    guard_of_entrance_chain = guard_of_entrance_prompt | llm.with_structured_output(Decision)
    question=input("what is your question?")
    output = guard_of_entrance_chain.invoke({"question": question})
    if output.decision=='end':
        db_records = "unrelated question, end the conversation!"

    mylogger.info(output)

    return {
        "next_action": output.decision,
        "start_node": output.start_node,
        "to_do_action": output.action,
        "based_on": output.based_on,
        "domain": output.domain or "http://mydomain/ontology",
        "database_records": db_records,
        "steps": ["more_question"],
    }

def review_schema(state: OverallState, db: SemanticGraphDB) -> OverallState:
    mylogger.debug("review schema - " + state.get("start_node"))
    original_schema_prompt = get_schema(start_node=state.get("start_node"), db=db)
    mylogger.info(original_schema_prompt)
    return {
        "database_records": original_schema_prompt,
        "steps": ["get_schema"]
    }

def generate_relational_db_ddl(state: OverallState, db: SemanticGraphDB, llm: ChatOpenAI) -> OverallState:
    original_schema = get_schema(start_node=state.get("start_node"), db=db)
    text2prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Given an input, generate oracle database DDL, ignore annotation properties. No pre-amble."
                    "For simple node and one to one relationship, add column to the table instead of creating another table"
                    "Do not wrap the response in any backticks or anything else. Respond with code only!"
                ),
            ),
            (
                "human",
                (
                    """{schema}"""
                ),
            ),
        ]
    )
    text_chain = text2prompt | llm | StrOutputParser()
    generated_ddl = text_chain.invoke(
        {
            "schema": original_schema
        }
    )
    mylogger.info(generated_ddl)
    return {"cypher_statement": generated_ddl, "steps": ["generate_relational_db_ddl"]}

def generate_pydantic_class(state: OverallState, db: SemanticGraphDB, llm: ChatOpenAI) -> OverallState:
    original_schema_prompt = gen_pydantic_class(start_node=state.get("start_node"), db=db)
    text2prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Given an input, generate Pydantic classes. No pre-amble."
                    "Do not wrap the response in any backticks or anything else. Respond with code only!"
                ),
            ),
            (
                "human",
                (
                    """{schema}"""
                ),
            ),
        ]
    )
    text2cypher_chain = text2prompt | llm | StrOutputParser()
    generated_clz = text2cypher_chain.invoke(
        {
            "schema": original_schema_prompt.to_string()
        }
    )
    mylogger.info(generated_clz)
    return {"cypher_statement": generated_clz, "steps": ["generate_pydantic_class"]}

def create_schema(state: OverallState, llm: ChatOpenAI) -> OverallState:
    """
    Generates a cypher statement based on the provided schema and user input
    """
    # Check if 'based_on' exists, if not, do nothing

    text2cypher_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    """
                    Given an input, convert it to a Cypher query. No pre-amble.
                    Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!
                    """
                ),
            ),
            (
                "human",
                (
                    """
                    Task: generate Cypher statements to add relationship, owl__Class, class hierarchy as owl__subClassOf, output each statement as one element of an array.
                    Instruction: The node in the schema is a owl__Class with rdfs_label, 
                    and the annotation properties are metadata for both node and relationship. Use real world knowledge to infer 
                    generate Cypher statement to merge the node.
                    match the nodes and generate Cypher statement to create relationship, if possible, add relationship property owl__minQualifiedCardinality.
                    The new node or relationship should have uri with domain {domain}. 
                    rdfs__label always be lower case, with space between words.
                    relationship type is camel case with first character lower case.
                    For each node and relationship, generate a skos__definition, which should not contain single quote character.
                    match only with rdfs__label.
                    Get schema info from {schema}
                    Note: Add many relationships you can find, do not include any explanations or apologies in your responses.
                    """
                ),
            ),
        ]
    )
    mylogger.info(text2cypher_prompt)
    text2cypher_chain = text2cypher_prompt | llm | StrOutputParser()

    if not state.get('based_on'):
        return {"cypher_statement": '[]', "steps": ["create_schema"]}

    generated_cypher = text2cypher_chain.invoke(
        {
            "schema": state.get('based_on'),
            "domain": state.get('domain')
        }
    )

    return {"cypher_statement": generated_cypher, "steps": ["create_schema"]}

def generate_cypher(state: OverallState, db: SemanticGraphDB, llm: ChatOpenAI) -> OverallState:
    """
    Generates a cypher statement based on the provided schema and user input
    """
    original_schema_prompt = gen_prompt4schema(start_node=state.get("start_node"), db=db)

    logger.info(original_schema_prompt.to_string())

    text2cypher_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Given an input, convert it to a Cypher query. No pre-amble."
                    "Do not wrap the response in any backticks or anything else. Respond with a Cypher statement only!"
                    "When merge a node, using rdfs__label as merge property"
                    "ON CREATE SET a.uri='some uri'"
                    "ON MATCH SET a.uri=COALESCE(a.uri,'some uri')"
                ),
            ),
            (
                "human",
                (
                    """{schema}"""
                ),
            ),
        ]
    )
    text2cypher_chain = text2cypher_prompt | llm | StrOutputParser()
    generated_cypher = text2cypher_chain.invoke(
        {
            "schema": original_schema_prompt.to_string()
        }
    )

    return {"cypher_statement": generated_cypher, "steps": ["generate_cypher"]}




def execute_graph_query(state: OverallState, graph: Neo4jGraph) -> OverallState:
    # import ast
    """
    Executes the given Cypher statement.
    """
    no_results = "I couldn't find any relevant information in the database"
    stmt_str = state.get("cypher_statement")
    mylogger.debug(stmt_str)
    statements = json.loads(stmt_str)
    records = []
    for stmt in statements:

        try:
            records.append(graph.query(stmt))
            mylogger.info(f'executed - {stmt}')
        except Exception as e:
            mylogger.error(e)
            records.append(e)
    return {
        "database_records": records if records else no_results,
        "next_action": "end",
        "steps": ["execute_cypher"],
    }

def del_dup_cls_rels(state: OverallState, graph: Neo4jGraph) -> OverallState:
    from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import del_dup_rels,del_dup_class
    """
    Executes the given Cypher statements.
    """
    no_results = "I couldn't find any relevant information in the database"
    statements = [del_dup_rels,del_dup_class]
    records = []
    for stmt in statements:

        try:
            records.append(graph.query(stmt))
            mylogger.info(f'executed - {stmt}')
        except Exception as e:
            mylogger.error(e)
            records.append(e)
    return {
        "database_records": records if records else no_results,
        "next_action": "end",
        "steps": ["execute_cypher"],
    }

def generate_final_answer_g(state: OverallState,llm: ChatOpenAI) -> OutputState:
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