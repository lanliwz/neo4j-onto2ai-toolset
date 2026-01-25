"""
Schema API endpoints for the Onto2AI Model Manager.
"""
import os
import logging
from typing import List, Optional
from functools import lru_cache
from fastapi import APIRouter, HTTPException
from neo4j import GraphDatabase

from .models import (
    ClassInfo, ClassSchema, RelationshipInfo,
    ChatRequest, ChatResponse,
    CypherRequest, CypherResponse,
    ClassUpdateRequest
)

router = APIRouter(tags=["schemas"])
logger = logging.getLogger("onto2ai-toolset")

# Lazy database connection
_db_connection = None

def get_db():
    """Get or create the staging database connection."""
    global _db_connection
    if _db_connection is None:
        uri = os.getenv("NEO4J_MODEL_DB_URL", "bolt://localhost:7687")
        user = os.getenv("NEO4J_MODEL_DB_USERNAME", "neo4j")
        password = os.getenv("NEO4J_MODEL_DB_PASSWORD", "")
        database = os.getenv("NEO4J_STAGING_DB_NAME", "stagingdb")
        
        _db_connection = Neo4jDatabaseSimple(uri, user, password, database)
        logger.info(f"Connected to staging database: {database}")
    return _db_connection


class Neo4jDatabaseSimple:
    """Simple Neo4j database wrapper for the API."""
    
    def __init__(self, uri, user, password, database):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
        self._database = database
    
    def execute_cypher(self, query, params=None, name=None):
        with self._driver.session(database=self._database) as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]


@router.get("/classes", response_model=List[ClassInfo])
async def list_classes():
    """
    List all owl:Class nodes in the stagingdb.
    Returns basic info: label, URI, definition.
    """
    db = get_db()
    try:
        query = """
        MATCH (c:owl__Class)
        WHERE c.rdfs__label IS NOT NULL
        RETURN DISTINCT 
            c.rdfs__label AS label,
            c.uri AS uri,
            c.skos__definition AS definition
        ORDER BY c.rdfs__label
        """
        results = db.execute_cypher(query, name="list_classes")
        return [
            ClassInfo(
                label=row["label"],
                uri=row["uri"] or "",
                definition=row.get("definition")
            )
            for row in results
        ]
    except Exception as e:
        logger.error(f"Error listing classes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/class/{class_name}", response_model=ClassSchema)
async def get_class_schema(class_name: str):
    """
    Get the materialized schema for a specific class.
    Returns classes and relationships.
    """
    db = get_db()
    try:
        query = """
        MATCH (c:owl__Class)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
        WHERE c.rdfs__label = $label OR c.uri = $label
        MATCH (parent)-[r]->(target)
        WHERE r.materialized = true
        RETURN DISTINCT
          c.rdfs__label AS SourceClassLabel,
          c.uri AS SourceClassURI,
          c.skos__definition AS SourceClassDef,
          type(r) AS RelType,
          r.uri AS RelURI,
          r.skos__definition AS RelDef,
          r.cardinality AS Cardinality,
          r.requirement AS Requirement,
          coalesce(target.rdfs__label, target.uri, 'Resource') AS TargetClassLabel,
          target.uri AS TargetClassURI,
          target.skos__definition AS TargetClassDef
        ORDER BY SourceClassLabel, RelType
        """
        results = db.execute_cypher(query, params={"label": class_name}, name="get_class_schema")
        
        classes_dict = {}
        relationships = []
        
        for row in results:
            # Add source class
            src_label = row["SourceClassLabel"]
            if src_label not in classes_dict:
                classes_dict[src_label] = ClassInfo(
                    label=src_label,
                    uri=row["SourceClassURI"] or "",
                    definition=row.get("SourceClassDef")
                )
            
            # Add target class
            tgt_label = row["TargetClassLabel"]
            if tgt_label not in classes_dict and tgt_label != "Resource":
                classes_dict[tgt_label] = ClassInfo(
                    label=tgt_label,
                    uri=row["TargetClassURI"] or "",
                    definition=row.get("TargetClassDef")
                )
            
            # Add relationship
            relationships.append(RelationshipInfo(
                source_class=src_label,
                source_class_uri=row["SourceClassURI"] or "",
                relationship_type=row["RelType"],
                target_class=tgt_label,
                target_class_uri=row["TargetClassURI"] or "",
                definition=row.get("RelDef"),
                uri=row.get("RelURI"),
                cardinality=row.get("Cardinality"),
                requirement=row.get("Requirement")
            ))
        
        return ClassSchema(
            database="stagingdb",
            classes=list(classes_dict.values()),
            relationships=relationships
        )
    except Exception as e:
        logger.error(f"Error getting class schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat interface for AI-assisted schema review.
    Uses the LLM to provide guidance on schema modifications.
    """
    try:
        import openai
        
        client = openai.AsyncOpenAI()
        model = os.getenv("GPT_MODEL_NAME", "gpt-4o")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an ontology expert helping users understand and enhance database schemas. The user is working with FIBO (Financial Industry Business Ontology) schemas in a staging database. Provide helpful, concise guidance about schema design, relationships, and best practices."},
                {"role": "user", "content": request.message}
            ]
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            suggestions=None
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cypher", response_model=CypherResponse)
async def execute_cypher(request: CypherRequest):
    """
    Execute a read-only Cypher query against stagingdb.
    """
    db = get_db()
    try:
        # Basic safety check - only allow read operations
        query_upper = request.query.strip().upper()
        if any(keyword in query_upper for keyword in ["CREATE", "MERGE", "DELETE", "SET", "REMOVE", "DROP"]):
            raise HTTPException(
                status_code=400, 
                detail="Only read queries are allowed. Use MATCH to query data."
            )
        
        results = db.execute_cypher(
            request.query, 
            params=request.params or {},
            name="user_cypher_query"
        )
        
        return CypherResponse(
            results=results,
            count=len(results)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing Cypher: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph-data/{class_name}")
async def get_graph_data(class_name: str):
    """
    Get graph data formatted for GoJS visualization.
    Returns nodes and links arrays.
    """
    db = get_db()
    try:
        query = """
        MATCH (c:owl__Class)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
        WHERE c.rdfs__label = $label OR c.uri = $label
        MATCH (parent)-[r]->(target)
        WHERE r.materialized = true
        RETURN DISTINCT
          c.rdfs__label AS SourceLabel,
          c.uri AS SourceURI,
          c.skos__definition AS SourceDef,
          type(r) AS RelType,
          r.uri AS RelURI,
          r.skos__definition AS RelDef,
          r.cardinality AS Cardinality,
          r.requirement AS Requirement,
          r.property_type AS PropType,
          coalesce(target.rdfs__label, target.uri, 'Resource') AS TargetLabel,
          target.uri AS TargetURI,
          target.skos__definition AS TargetDef
        ORDER BY SourceLabel, RelType
        """
        results = db.execute_cypher(query, params={"label": class_name}, name="get_graph_data")
        
        nodes = {}
        links = []
        
        for row in results:
            src_label = row["SourceLabel"]
            tgt_label = row["TargetLabel"]
            
            # Add source node
            if src_label not in nodes:
                nodes[src_label] = {
                    "key": src_label,
                    "label": src_label,
                    "uri": row["SourceURI"],
                    "definition": row.get("SourceDef"),
                    "category": "class"
                }
            
            # Add target node
            if tgt_label not in nodes:
                is_datatype = row.get("PropType") == "owl__DatatypeProperty" or "XMLSchema" in (row.get("TargetURI") or "")
                nodes[tgt_label] = {
                    "key": tgt_label,
                    "label": tgt_label,
                    "uri": row.get("TargetURI"),
                    "definition": row.get("TargetDef"),
                    "category": "datatype" if is_datatype else "class"
                }
            
            # Add link
            links.append({
                "from": src_label,
                "to": tgt_label,
                "relationship": row["RelType"],
                "uri": row.get("RelURI"),
                "definition": row.get("RelDef"),
                "cardinality": row.get("Cardinality"),
                "requirement": row.get("Requirement")
            })
        
        return {
            "nodes": list(nodes.values()),
            "links": links
        }
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
