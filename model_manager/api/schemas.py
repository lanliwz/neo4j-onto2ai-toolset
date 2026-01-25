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
        """Execute a Cypher query with pretty logging."""
        query_name = name or "unnamed_query"
        
        # Create executable query by substituting parameters
        executable_query = query.strip()
        if params:
            for key, value in params.items():
                if isinstance(value, str):
                    executable_query = executable_query.replace(f"${key}", f"'{value}'")
                else:
                    executable_query = executable_query.replace(f"${key}", str(value))
        
        # Pretty format the log output
        separator = "─" * 70
        print(f"\n┌{separator}┐")
        print(f"│ 🔍 CYPHER QUERY: {query_name}")
        print(f"├{separator}┤")
        print(f"│ 📋 Copy-paste ready query for Neo4j Browser:")
        print(f"└{separator}┘")
        print()
        print(executable_query)
        print()
        
        with self._driver.session(database=self._database) as session:
            result = session.run(query, params or {})
            records = [dict(record) for record in result]
            
            # Log result count
            print(f"✅ Returned {len(records)} record(s)")
            print(f"{'─' * 70}\n")
            
            return records


@router.get("/classes", response_model=List[ClassInfo])
async def list_classes():
    """
    List all owl:Class nodes in the stagingdb.
    Returns basic info: label, URI, definition.
    Filters out placeholder/empty nodes.
    """
    db = get_db()
    try:
        query = """
        MATCH (c:owl__Class)
        WHERE c.rdfs__label IS NOT NULL
          AND NOT c.rdfs__label =~ '^N[0-9a-f]{32}$'
          AND NOT c.rdfs__label =~ '^[0-9a-f]{8}-[0-9a-f]{4}-.*'
          AND size(c.rdfs__label) > 1
          AND 'owl__Class' IN labels(c)
        RETURN DISTINCT 
            c.rdfs__label AS label,
            c.uri AS uri,
            c.skos__definition AS definition,
            labels(c) AS nodeLabels
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
        MATCH (c:owl__Class)
        WHERE c.rdfs__label = $label OR c.uri = $label
        OPTIONAL MATCH (c)-[:owl__subClassOf*0..]->(parent:owl__Class)
        WITH coalesce(parent, c) AS classNode, c
        
        // Outbound relationships
        OPTIONAL MATCH (classNode)-[r_out]->(target)
        WHERE r_out.materialized = true
        
        // Inbound relationships
        OPTIONAL MATCH (source)-[r_in]->(classNode)
        WHERE r_in.materialized = true
        
        WITH c, classNode,
             collect(DISTINCT {rel: r_out, other: target, dir: 'out'}) AS outRels,
             collect(DISTINCT {rel: r_in, other: source, dir: 'in'}) AS inRels
        
        UNWIND (outRels + inRels) AS relData
        WITH c, classNode, relData
        WHERE relData.rel IS NOT NULL
        
        RETURN DISTINCT
          c.rdfs__label AS SourceLabel,
          c.uri AS SourceURI,
          c.skos__definition AS SourceDef,
          type(relData.rel) AS RelType,
          relData.rel.uri AS RelURI,
          relData.rel.skos__definition AS RelDef,
          relData.rel.cardinality AS Cardinality,
          relData.rel.requirement AS Requirement,
          relData.rel.property_type AS PropType,
          coalesce(relData.other.rdfs__label, relData.other.uri, 'Resource') AS TargetLabel,
          relData.other.uri AS TargetURI,
          relData.other.skos__definition AS TargetDef,
          relData.dir AS Direction
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
        
        # Include query for display in Query tab
        display_query = query.replace("$label", f"'{class_name}'")
        
        return {
            "nodes": list(nodes.values()),
            "links": links,
            "query": display_query.strip()
        }
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/node-focus/{node_label}")
async def get_node_focus_data(node_label: str):
    """
    Get a node and its direct in/out relationships for focused graph view.
    Returns the selected node plus all directly connected nodes.
    """
    db = get_db()
    try:
        query = """
        MATCH (center:owl__Class)
        WHERE center.rdfs__label = $label OR center.uri = $label
        OPTIONAL MATCH (center)-[r_out]->(target)
        WHERE r_out.materialized = true
        OPTIONAL MATCH (source)-[r_in]->(center)
        WHERE r_in.materialized = true
        WITH center, 
             collect(DISTINCT {
                rel: r_out, 
                node: target, 
                direction: 'out'
             }) AS outgoing,
             collect(DISTINCT {
                rel: r_in, 
                node: source, 
                direction: 'in'
             }) AS incoming
        RETURN center, outgoing, incoming
        """
        results = db.execute_cypher(query, params={"label": node_label}, name="get_node_focus_data")
        
        if not results:
            return {"nodes": [], "links": []}
        
        row = results[0]
        nodes = {}
        links = []
        
        # Add center node
        center = row["center"]
        center_label = center.get("rdfs__label", node_label)
        nodes[center_label] = {
            "key": center_label,
            "label": center_label,
            "uri": center.get("uri"),
            "definition": center.get("skos__definition"),
            "category": "class",
            "isCenter": True
        }
        
        # Process outgoing relationships
        for item in row["outgoing"]:
            if item["rel"] is None or item["node"] is None:
                continue
            rel = item["rel"]
            target = item["node"]
            tgt_label = target.get("rdfs__label") or target.get("uri") or "Resource"
            
            if tgt_label not in nodes:
                is_datatype = rel.get("property_type") == "owl__DatatypeProperty" or "XMLSchema" in (target.get("uri") or "")
                nodes[tgt_label] = {
                    "key": tgt_label,
                    "label": tgt_label,
                    "uri": target.get("uri"),
                    "definition": target.get("skos__definition"),
                    "category": "datatype" if is_datatype else "class"
                }
            
            links.append({
                "from": center_label,
                "to": tgt_label,
                "relationship": rel.type if hasattr(rel, 'type') else str(type(rel).__name__),
                "uri": rel.get("uri"),
                "definition": rel.get("skos__definition"),
                "cardinality": rel.get("cardinality"),
                "requirement": rel.get("requirement")
            })
        
        # Process incoming relationships
        for item in row["incoming"]:
            if item["rel"] is None or item["node"] is None:
                continue
            rel = item["rel"]
            source = item["node"]
            src_label = source.get("rdfs__label") or source.get("uri") or "Resource"
            
            if src_label not in nodes:
                nodes[src_label] = {
                    "key": src_label,
                    "label": src_label,
                    "uri": source.get("uri"),
                    "definition": source.get("skos__definition"),
                    "category": "class"
                }
            
            links.append({
                "from": src_label,
                "to": center_label,
                "relationship": rel.type if hasattr(rel, 'type') else str(type(rel).__name__),
                "uri": rel.get("uri"),
                "definition": rel.get("skos__definition"),
                "cardinality": rel.get("cardinality"),
                "requirement": rel.get("requirement")
            })
        
        # Include query for display in Query tab
        display_query = query.replace("$label", f"'{node_label}'")
        
        return {
            "nodes": list(nodes.values()),
            "links": links,
            "query": display_query.strip()
        }
    except Exception as e:
        logger.error(f"Error getting node focus data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
