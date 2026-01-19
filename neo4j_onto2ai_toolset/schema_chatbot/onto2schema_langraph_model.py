import json
from operator import add
from typing import Annotated, List, Literal, Optional, Union, Dict, Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import Neo4jDatabase, get_schema
from neo4j_onto2ai_toolset.langgraph_prompts.onto2schema_prompt import gen_prompt4schema, gen_pydantic_class
from neo4j_onto2ai_toolset.onto2ai_tool_config import llm, graphdb
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger as mylogger

# --- State Definitions ---

class OverallState(TypedDict):
    question: str
    next_action: Annotated[str, "The high-level action category"]
    to_do_action: Annotated[str, "The specific operation within the category"]
    start_node: str
    domain: str
    based_on: str
    cypher_statement: str
    cypher_errors: Annotated[List[str], add]
    database_records: Union[str, List[Dict[str, Any]]]
    steps: Annotated[List[str], add]

class InputState(TypedDict):
    question: str

class OutputState(TypedDict):
    answer: str
    steps: List[str]
    database_records: Union[str, List[Dict[str, Any]]]
    cypher_statement: str
    next_action: str

# --- Structured Output Models ---

class IntentDecision(BaseModel):
    """Decision on how to handle the user's schema/ontology related question."""
    decision: Literal["schema", "pydantic-model", "relation-model", "end"] = Field(
        description="The target output format or investigation area."
    )
    start_node: str = Field(
        description="Main entity or concept name (in lower case)."
    )
    action: Literal["review", "enhance", "create"] = Field(
        default="review",
        description="Specific intent: reviewing existing, enhancing, or creating new from scratch."
    )
    based_on: Optional[str] = Field(
        default=None,
        description="Optional source material or URL mentioned as documentation."
    )
    domain: Optional[str] = Field(
        default="http://mydomain/ontology",
        description="The target ontology domain if relevant."
    )

# --- Node Functions ---

async def classify_intent(state: OverallState) -> Dict[str, Any]:
    """Classifies user question into a specific schema/model action."""
    system_msg = """
    You are an ontology architect. Analyze the user question and determine the next action.
    - 'schema' if they want to see, update, or create an ontology model/schema.
    - 'pydantic-model' if they want Python Pydantic classes.
    - 'relation-model' if they want SQL/Relational DDL.
    - 'end' for unrelated topics.
    
    If it's about a specific concept (e.g., 'Person', 'Order'), put it in 'start_node'.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        ("human", "{question}")
    ])
    
    chain = prompt | llm.with_structured_output(IntentDecision)
    output = await chain.ainvoke({"question": state["question"]})
    
    mylogger.info(f"Intent Classification: {output}")
    
    return {
        "next_action": output.decision,
        "start_node": output.start_node,
        "to_do_action": output.action,
        "based_on": output.based_on,
        "domain": output.domain,
        "steps": ["classify_intent"]
    }

async def review_schema(state: OverallState, db: Neo4jDatabase) -> Dict[str, Any]:
    """Retrieves the current schema for a concept."""
    concept = state.get("start_node", "person")
    mylogger.debug(f"Reviewing schema for: {concept}")
    schema_text = get_schema(start_node=concept, db=db)
    return {
        "database_records": schema_text,
        "steps": ["review_schema"]
    }

async def generate_relational_db_ddl(state: OverallState, db: Neo4jDatabase) -> Dict[str, Any]:
    """Generates Oracle DDL from the schema."""
    schema_text = get_schema(start_node=state.get("start_node"), db=db)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate Oracle DDL for the given schema. No pre-amble. One-to-one as columns. Code only."),
        ("human", "{schema}")
    ])
    chain = prompt | llm | StrOutputParser()
    ddl = await chain.ainvoke({"schema": schema_text})
    return {"cypher_statement": ddl, "steps": ["generate_relational_db_ddl"]}

async def generate_pydantic_class_node(state: OverallState, db: Neo4jDatabase) -> Dict[str, Any]:
    """Generates Pydantic v2 classes from the schema."""
    # Using existing prompt utility
    prompt_value = gen_pydantic_class(start_node=state.get("start_node"), db=db)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate Pydantic v2 classes. No pre-amble. Code only."),
        ("human", "{prompt}")
    ])
    chain = prompt | llm | StrOutputParser()
    code = await chain.ainvoke({"prompt": str(prompt_value)})
    return {"cypher_statement": code, "steps": ["generate_pydantic_class"]}

async def create_schema_node(state: OverallState) -> Dict[str, Any]:
    """Generates a Cypher statement to create a new schema from external text/URL."""
    if not state.get('based_on'):
        return {"cypher_statement": "[]", "steps": ["create_schema_aborted"]}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Convert input text/URL into a list of Cypher MERGE statements to create classes and relationships."),
        ("human", "Domain: {domain}\nInput: {based_on}")
    ])
    chain = prompt | llm | StrOutputParser()
    cypher = await chain.ainvoke({"domain": state["domain"], "based_on": state["based_on"]})
    return {"cypher_statement": cypher, "steps": ["create_schema"]}

async def generate_cypher_node(state: OverallState, db: Neo4jDatabase) -> Dict[str, Any]:
    """Generates a Cypher statement to enhance an existing schema."""
    concept = state.get("start_node")
    prompt_value = gen_prompt4schema(start_node=concept, db=db)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate a Cypher statement to enhance the following schema. MATCH with rdfs__label."),
        ("human", "{schema}")
    ])
    chain = prompt | llm | StrOutputParser()
    cypher = await chain.ainvoke({"schema": str(prompt_value)})
    return {"cypher_statement": cypher, "steps": ["generate_cypher"]}

async def execute_query_node(state: OverallState) -> Dict[str, Any]:
    """Executes generated Cypher (if it is a list of statements)."""
    stmt_str = state.get("cypher_statement", "[]")
    
    try:
        # Expected to be a JSON list of strings
        statements = json.loads(stmt_str) if stmt_str.startswith("[") else [stmt_str]
    except:
        statements = [stmt_str]

    records = []
    for stmt in statements:
        if not stmt or len(stmt.strip()) < 5: continue
        try:
            res = graphdb.query(stmt)
            records.append(res)
        except Exception as e:
            mylogger.error(f"Cypher Error: {e}")
            return {"cypher_errors": [str(e)], "steps": ["execute_query_failed"]}

    return {
        "database_records": records,
        "next_action": "end",
        "steps": ["execute_query"]
    }

async def del_dup_node(state: OverallState) -> Dict[str, Any]:
    """Cleans up duplicate classes and relationships."""
    from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import del_dup_rels, del_dup_class
    for stmt in [del_dup_rels, del_dup_class]:
        try:
            graphdb.query(stmt)
        except Exception as e:
            mylogger.error(f"Deduplication Error: {e}")
    return {"steps": ["delete_duplicates"]}