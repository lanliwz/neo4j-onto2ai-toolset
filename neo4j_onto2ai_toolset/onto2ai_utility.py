import json
import time
import logging
from operator import add
from typing import Annotated, List, Literal, Optional, Union, Dict, Any

from neo4j import GraphDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# Internal project imports
from neo4j_onto2ai_toolset.onto2schema.cypher_statement.cypher_for_modeling import *
from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import *
from neo4j_onto2ai_toolset.langgraph_prompts.onto2schema_prompt import gen_prompt4schema, gen_pydantic_class
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger as mylogger

ontoToollogger = logging.getLogger("onto2ai-toolset")

# --- Database Utilities (Merged from neo4j_utility.py) ---

class Neo4jDatabase:
    """Interacts with a Neo4j database for schema-related operations."""
    def __init__(self, uri, user, password, database_name):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._database_name = database_name

    def close(self):
        self._driver.close()

    def create_node(self, label, properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node, label, properties)

    def execute_cypher(self, query, params=None, *, name: str | None = None):
        """Execute a Cypher statement with structured logging."""
        stmt_name = name or "cypher"
        q_preview = (query or "").replace("\n", " ").strip()
        if len(q_preview) > 200:
            q_preview = q_preview[:200] + "..."

        ontoToollogger.info(
            f"{stmt_name} execution started - {query}",
            extra={
                "op": stmt_name,
                "database": getattr(self, "_database_name", None),
                "query_preview": q_preview,
            },
        )

        start = time.time()
        try:
            with self._driver.session(database=self._database_name) as session:
                return session.execute_write(self._get_dataset, query, params)
        except Exception as e:
            elapsed_ms = int((time.time() - start) * 1000)
            ontoToollogger.exception(
                f"{stmt_name} execution failed",
                extra={
                    "op": stmt_name,
                    "database": getattr(self, "_database_name", None),
                    "elapsed_ms": elapsed_ms,
                    "query_preview": q_preview,
                },
            )
            raise
        else:
            elapsed_ms = int((time.time() - start) * 1000)
            ontoToollogger.info(
                f"{stmt_name} execution finished",
                extra={
                    "op": stmt_name,
                    "database": getattr(self, "_database_name", None),
                    "elapsed_ms": elapsed_ms,
                },
            )

    def get_node2node_relationship(self, label=None):
        with self._driver.session(database=self._database_name) as session:
            query = query_cls2cls_relationship(label)
            ontoToollogger.debug(query)
            result = session.execute_read(self._get_dataset, query)
            ontoToollogger.debug(result)
            return [f"(:{record['start_node']})-[:{record['relationship']}]->(:{record['end_node']})" for record in result]

    def get_node_dataproperty(self, label=None):
        with self._driver.session(database=self._database_name) as session:
            result = session.execute_read(self._get_dataset, query_dataproperty(label))
            return [f"(:{record['start_node']}) node has property {record['relationship']} [type: {record['xsd_type'] or record['end_node']}, cardinality: {record['cardinality'] or '-'}]" for record in result]

    def get_nodes(self, label=None):
        with self._driver.session(database=self._database_name) as session:
            ontoToollogger.debug(query_start_nodes(label))
            result = session.execute_read(self._get_dataset, query_start_nodes(label))
            ontoToollogger.debug(result)
            return [f"(:{record['start_node']}) nodes have annotation properties {record['annotation_properties']}"
                    for record in result if record['start_node'] is not None]

    def get_end_nodes(self, label=None):
        with self._driver.session(database=self._database_name) as session:
            result = session.execute_read(self._get_dataset, query_end_nodes(label))
            return [f"(:{record['end_node']}) nodes have annotation properties {record['annotation_properties']}"
                    for record in result if record['end_node'] is not None]

    def get_relationships(self, label=None):
        with self._driver.session(database=self._database_name) as session:
            result = session.execute_read(self._get_dataset, query_relationships(label))
            return [f"[:{record['relationship']}] relationship has annotation properties  {record['annotation_properties']}" for record in result]

    @staticmethod
    def _get_dataset(tx, query, params=None):
        result = tx.run(query, parameters=params)
        return [record.data() for record in result]

    @staticmethod
    def _create_node(tx, label, properties):
        query = f"CREATE (a:{label} {{properties}})"
        tx.run(query, properties=properties)

    @staticmethod
    def _execute_cypher(tx, query):
        tx.run(query)

    def create_node_and_relationship(self, node1_label, node1_properties, relationship_type, node2_label, node2_properties):
        with self._driver.session(database=self._database_name) as session:
            session.execute_write(self._create_node_rel, node1_label, node1_properties, relationship_type, node2_label, node2_properties)

    @staticmethod
    def _create_node_rel(tx, node1_label, node1_properties, relationship_type, node2_label, node2_properties):
        query = (
            f"CREATE (a:{node1_label} {{properties1}}) "
            f"-[:{relationship_type}]-> "
            f"(b:{node2_label} {{properties2}})"
        )
        tx.run(query, properties1=node1_properties, properties2=node2_properties)

    def get_label_counts(self) -> Dict[str, int]:
        """Fetch instance counts for all labels and concepts in the database."""
        import re
        
        # Query 1: Regular Neo4j Labels
        q1 = "MATCH (n) UNWIND labels(n) AS label RETURN label, count(n) AS count"
        
        # Query 2: Ontological types (for non-materialized datasets)
        # We look for nodes connected to a class via rdf__type
        q2 = "MATCH (c:owl__Class)<-[:rdf__type]-(i) RETURN c.rdfs__label AS label, count(i) AS count"
        
        counts = {}
        
        def to_camel(s):
            if not s: return ""
            return "".join(word.capitalize() for word in re.split(r"[-\s]", str(s)))

        try:
            # Get regular label counts
            results1 = self.execute_cypher(q1, name="get_label_counts_core")
            for row in results1:
                lbl = row['label']
                counts[lbl] = row['count']
                
            # Get ontological type counts
            results2 = self.execute_cypher(q2, name="get_label_counts_onto")
            for row in results2:
                raw_lbl = row['label']
                camel_lbl = to_camel(raw_lbl)
                # Aggregate
                counts[camel_lbl] = counts.get(camel_lbl, 0) + row['count']
        except Exception as e:
            ontoToollogger.error(f"Error in get_label_counts: {e}")
            
        return counts

def get_schema(start_node: str, db: Neo4jDatabase):
    schema = ("\n".join(db.get_node2node_relationship(start_node)) + '\n'
              + "\n".join(db.get_node_dataproperty(start_node)) + '\n'
              + "\n".join(db.get_end_nodes(start_node)) + '\n'
              + "\n".join(db.get_nodes(start_node)) + '\n'
              + "\n".join(db.get_relationships(start_node)) + '\n')
    ontoToollogger.debug(schema)
    return schema

def get_full_schema(db: Neo4jDatabase, use_heuristics: bool = True):
    import re
    import ast
    
    # 1. Fetch raw components
    nodes_raw = db.get_nodes()
    relationships_raw = db.get_relationships()
    node2node_rels_raw = db.get_node2node_relationship()
    node_dataprops_raw = db.get_node_dataproperty()
    
    if not use_heuristics:
        schema = (
            f"Node Labels: \n{chr(10).join(nodes_raw)} \n"
            f"Relationships: \n{chr(10).join(node2node_rels_raw)} \n"
            f"Relationship types: \n{chr(10).join(relationships_raw)} \n"
            f"Node Properties: \n{chr(10).join(node_dataprops_raw)} \n"
        )
        return schema

    # 2. Heuristic Filtering Logic
    instance_counts = db.get_label_counts()
    
    # Parse label metadata
    label_metadata = {}
    for line in nodes_raw:
        match = re.search(r"^\(:(.*?)\) nodes have annotation properties\s+(.*)", line)
        if match:
            label = match.group(1)
            try:
                props = ast.literal_eval(match.group(2))
                label_metadata[label] = props
            except:
                label_metadata[label] = {}

    # Determine outgoing relationships (topology)
    outgoing_rels = set()
    for rel_str in node2node_rels_raw:
        # Example: (:Person)-[:hasAddress]->(:PhysicalAddress)
        m = re.search(r"^\(:(.*?)\)-.*?->", rel_str)
        if m:
            outgoing_rels.add(m.group(1).strip())

    # Baseline core entities (Always preserve these)
    baseline_entities = {'Person', 'Employer', 'Organization', 'IndividualTaxReturn', 'Form1040_2025', 'MonetaryAmount', 'W2Form', 'CreditCardAccount', 'Cardholder', 'Merchant', 'Payment'}
    
    # Effective Label Calculation
    effective_labels = set()
    for label in label_metadata:
        count = instance_counts.get(label, 0)
        is_baseline = label in baseline_entities
        has_outgoing = label in outgoing_rels
        
        props = label_metadata.get(label, {})
        is_datatype = any(k in props for k in ['enumValues', 'xsd__type', 'xsd_type', 'xsd_datatype'])
        
        # Effective if: has instances, is baseline, OR has outgoing relationships (and not a datatype)
        if (count > 0 or is_baseline or has_outgoing) and not is_datatype:
            effective_labels.add(label)

    # 3. Filter and rebuild output
    filtered_nodes = [n for n in nodes_raw if re.search(r"^\(:(.*?)\)", n).group(1) in effective_labels]
    filtered_topo = [r for r in node2node_rels_raw if re.search(r"^\(:(.*?)\)", r).group(1) in effective_labels]
    filtered_props = [p for p in node_dataprops_raw if re.search(r"^\(:(.*?)\)", p).group(1) in effective_labels]
    
    schema = (
        f"Node Labels: \n{chr(10).join(filtered_nodes)} \n"
        f"Relationships: \n{chr(10).join(filtered_topo)} \n"
        f"Relationship types: \n{chr(10).join(relationships_raw)} \n"
        f"Node Properties: \n{chr(10).join(filtered_props)} \n"
    )
    return schema

def get_node4schema(start_node: str, db: Neo4jDatabase):
    return "\n".join(db.get_nodes(start_node)) + '\n'

# --- Chatbot State Definitions ---

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

# --- Chatbot Node Functions (Local imports to break circles) ---

async def classify_intent(state: OverallState) -> Dict[str, Any]:
    """Classifies user question into a specific schema/model action."""
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm
    
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
    
    chain = prompt | get_llm().with_structured_output(IntentDecision)
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
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm
    
    schema_text = get_schema(start_node=state.get("start_node"), db=db)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate Oracle DDL for the given schema. No pre-amble. One-to-one as columns. Code only."),
        ("human", "{schema}")
    ])
    chain = prompt | get_llm() | StrOutputParser()
    ddl = await chain.ainvoke({"schema": schema_text})
    return {"cypher_statement": ddl, "steps": ["generate_relational_db_ddl"]}

async def generate_pydantic_class_node(state: OverallState, db: Neo4jDatabase) -> Dict[str, Any]:
    """Generates Pydantic v2 classes from the schema."""
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm
    
    prompt_value = gen_pydantic_class(start_node=state.get("start_node"), db=db)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate Pydantic v2 classes. No pre-amble. Code only."),
        ("human", "{prompt}")
    ])
    chain = prompt | get_llm() | StrOutputParser()
    code = await chain.ainvoke({"prompt": str(prompt_value)})
    return {"cypher_statement": code, "steps": ["generate_pydantic_class"]}

async def create_schema_node(state: OverallState) -> Dict[str, Any]:
    """Generates a Cypher statement to create a new schema from external text/URL."""
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm
    
    if not state.get('based_on'):
        return {"cypher_statement": "[]", "steps": ["create_schema_aborted"]}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Convert input text/URL into a list of Cypher MERGE statements to create classes and relationships."),
        ("human", "Domain: {domain}\nInput: {based_on}")
    ])
    chain = prompt | get_llm() | StrOutputParser()
    cypher = await chain.ainvoke({"domain": state["domain"], "based_on": state["based_on"]})
    return {"cypher_statement": cypher, "steps": ["create_schema"]}

async def generate_cypher_node(state: OverallState, db: Neo4jDatabase) -> Dict[str, Any]:
    """Generates a Cypher statement to enhance an existing schema."""
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_llm
    
    concept = state.get("start_node")
    prompt_value = gen_prompt4schema(start_node=concept, db=db)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate a Cypher statement to enhance the following schema. MATCH with rdfs__label."),
        ("human", "{schema}")
    ])
    chain = prompt | get_llm() | StrOutputParser()
    cypher = await chain.ainvoke({"schema": str(prompt_value)})
    return {"cypher_statement": cypher, "steps": ["generate_cypher"]}

async def execute_query_node(state: OverallState) -> Dict[str, Any]:
    """Executes generated Cypher (if it is a list of statements)."""
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_graphdb
    
    stmt_str = state.get("cypher_statement", "[]")
    
    try:
        statements = json.loads(stmt_str) if stmt_str.startswith("[") else [stmt_str]
    except:
        statements = [stmt_str]

    records = []
    for stmt in statements:
        if not stmt or len(stmt.strip()) < 5: continue
        try:
            res = get_graphdb().query(stmt)
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
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_graphdb
    from neo4j_onto2ai_toolset.onto2schema.cypher_statement.gen_schema import del_dup_rels, del_dup_class
    
    for stmt in [del_dup_rels, del_dup_class]:
        try:
            get_graphdb().query(stmt)
        except Exception as e:
            mylogger.error(f"Deduplication Error: {e}")
    return {"steps": ["delete_duplicates"]}