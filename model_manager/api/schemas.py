"""
Schema API endpoints for the Onto2AI Model Manager.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from functools import lru_cache
from fastapi import APIRouter, HTTPException
from neo4j import GraphDatabase

from .models import (
    ClassInfo, ClassSchema, RelationshipInfo,
    ChatRequest, ChatResponse, GraphData,
    CypherRequest, CypherResponse,
    ClassUpdateRequest, LLMStatus, LLMUpdateRequest
)

router = APIRouter(tags=["schemas"])
logger = logging.getLogger("onto2ai-toolset")

# Onto2AI MCP Client (Lazy Initialization)
from neo4j_onto2ai_toolset.onto2ai_client import Onto2AIClient
_onto2ai_client = None

async def get_onto2ai_client():
    global _onto2ai_client, _current_llm
    if _current_llm is None:
        _current_llm = os.getenv("LLM_MODEL_NAME") or "gemini-2.0-flash-exp"
        
    if _onto2ai_client is None:
        _onto2ai_client = Onto2AIClient(model_name=_current_llm)
        await _onto2ai_client.connect()
    return _onto2ai_client

# Lazy database connection
_db_connection = None

# LLM State
AVAILABLE_LLMS = ["gemini-2.0-flash-exp", "gemini-3-flash-preview-001", "gpt-4o-2024-05-13"]
_current_llm = None  # Lazy init in get_llm_status/get_onto2ai_client

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
            records = [self._serialize_record(record) for record in result]
            
            # Log result count
            print(f"✅ Returned {len(records)} record(s)")
            print(f"{'─' * 70}\n")
            
            return records
    
    def _serialize_record(self, record):
        """Convert a Neo4j record to a JSON-serializable dict."""
        from neo4j.graph import Node, Relationship, Path
        
        def serialize_value(val):
            if val is None:
                return None
            elif isinstance(val, Node):
                # Convert Node to dict with labels and properties
                return {
                    "_type": "node",
                    "_id": val.element_id,
                    "_labels": list(val.labels),
                    **dict(val)
                }
            elif isinstance(val, Relationship):
                # Convert Relationship to dict
                # Try multiple ways to get start/end node IDs for different driver versions
                start_node = getattr(val, "start_node", None)
                end_node = getattr(val, "end_node", None)
                
                # Fallback to .nodes tuple if properties are missing
                if (not start_node or not end_node) and hasattr(val, "nodes") and len(val.nodes) >= 2:
                    start_node = val.nodes[0]
                    end_node = val.nodes[1]
                
                start_id = getattr(start_node, "element_id", None) or getattr(start_node, "id", None)
                end_id = getattr(end_node, "element_id", None) or getattr(end_node, "id", None)
                
                return {
                    "_type": "relationship",
                    "_id": getattr(val, "element_id", None) or getattr(val, "id", None),
                    "_rel_type": getattr(val, "type", "relates_to"),
                    "_start": start_id,
                    "_end": end_id,
                    **dict(val)
                }
            elif isinstance(val, Path):
                # Convert Path to dict
                return {
                    "_type": "path",
                    "nodes": [serialize_value(n) for n in val.nodes],
                    "relationships": [serialize_value(r) for r in val.relationships]
                }
            elif isinstance(val, list):
                return [serialize_value(v) for v in val]
            elif isinstance(val, dict):
                return {k: serialize_value(v) for k, v in val.items()}
            else:
                return val
        
        return {key: serialize_value(value) for key, value in dict(record).items()}


def results_to_graph_data(results: List[Dict[str, Any]], query: Optional[str] = None) -> GraphData:
    """
    Robust helper to extract nodes and links from Cypher results.
    Uses Neo4j element IDs for de-duplication and consistent key resolution.
    """
    if not results:
        return GraphData(nodes=[], links=[], query=query)

    nodes_by_id = {}  # element_id -> node_data
    rels_by_id = {}   # element_id -> rel_data

    # Pass 1: Collect all distinct nodes and relationships from any column/structure
    def inspect(item):
        if not isinstance(item, dict):
            return
        
        item_type = item.get("_type")
        item_id = item.get("_id")
        if not item_id:
            return
            
        if item_type == "node":
            if item_id not in nodes_by_id:
                nodes_by_id[item_id] = item
        elif item_type == "relationship":
            if item_id not in rels_by_id:
                rels_by_id[item_id] = item
        elif item_type == "path":
            for n in item.get("nodes", []):
                inspect(n)
            for r in item.get("relationships", []):
                inspect(r)

    for row in results:
        for val in row.values():
            if isinstance(val, list):
                for v in val:
                    inspect(v)
            else:
                inspect(val)

    # Pass 2: Establish stable keys and create node objects
    nodes_out = {}    # key -> node_viz_obj
    id_to_key = {}    # element_id -> key
    
    # Sort IDs for stable key assignment (for collisions)
    for eid in sorted(nodes_by_id.keys()):
        node = nodes_by_id[eid]
        labels = node.get("_labels", [])
        
        # Get a human-friendly label
        raw_label = node.get("rdfs__label") or node.get("label") or (labels[0] if labels else eid[-8:])
        if isinstance(raw_label, list):
            label = str(raw_label[0]) if raw_label else "Unknown"
        else:
            label = str(raw_label)
            
        # Handle key collisions for distinct nodes with same name
        key = label
        if key in nodes_out:
            key = f"{label} ({eid[-4:]})"
            
        category = "class"
        if "rdfs__Datatype" in labels or "XMLSchema" in (node.get("uri") or ""):
            category = "datatype"
        elif "owl__NamedIndividual" in labels:
            category = "individual"
            
        node_obj = {
            "key": key,
            "label": label,
            "uri": node.get("uri"),
            "definition": node.get("skos__definition"),
            "category": category,
            "properties": {k: v for k, v in node.items() if not k.startswith("_")},
            "_id": eid
        }
        
        nodes_out[key] = node_obj
        id_to_key[eid] = key

    # Pass 3: Process relationships into unique links
    links_out = []
    seen_links = set() # (from, to, type) de-duplication
    
    # Sort by relationship ID for stability
    for rid in sorted(rels_by_id.keys()):
        rel = rels_by_id[rid]
        start_id = rel.get("_start")
        end_id = rel.get("_end")
        rel_type = rel.get("_rel_type", "relates_to")
        
        # Resolve node keys, using placeholders only if node was missing (shouldn't happen)
        from_key = id_to_key.get(start_id)
        if not from_key:
            from_key = f"Node-{start_id[-8:]}"
            if from_key not in nodes_out:
                nodes_out[from_key] = {"key": from_key, "label": from_key, "category": "class"}
        
        to_key = id_to_key.get(end_id)
        if not to_key:
            to_key = f"Node-{end_id[-8:]}"
            if to_key not in nodes_out:
                nodes_out[to_key] = {"key": to_key, "label": to_key, "category": "class"}

        # De-duplicate links between the same node pair of the same type
        # This prevents redundant lines for identical logical relationships
        link_id = (from_key, to_key, rel_type)
        if link_id in seen_links:
            continue
        seen_links.add(link_id)

        links_out.append({
            "from": from_key,
            "to": to_key,
            "relationship": rel_type,
            "uri": rel.get("uri"),
            "definition": rel.get("skos__definition"),
            "properties": {k: v for k, v in rel.items() if not k.startswith("_")}
        })

    return GraphData(nodes=list(nodes_out.values()), links=links_out, query=query)


def results_to_uml_data(results: List[Dict[str, Any]], query: Optional[str] = None) -> GraphData:
    """
    Heavily flattens Neo4j results for UML/Pydantic box visualization.
    Datatype properties and Enumeration relationships are pulled INSIDE the class boxes.
    """
    if not results:
        return GraphData(nodes=[], links=[], query=query)

    classes = {}  # element_id -> class_data
    attributes_by_class = {} # element_id -> list of attributes
    links = []
    seen_links = set()

    for row in results:
        # Extract source class
        src = row.get("c") or row.get("center")
        if not src:
            continue
            
        src_id = src.get("element_id") or src.get("_id")
        if not src_id:
            continue
            
        if src_id not in classes:
            classes[src_id] = {
                "key": src_id,
                "label": src.get("rdfs__label") or src.get("label") or "Class",
                "uri": src.get("uri"),
                "definition": src.get("skos__definition"),
                "category": "class",
                "attributes": []
            }
            attributes_by_class[src_id] = []

        # Extract relationship and target
        rel = row.get("r") or row.get("r_out")
        tgt = row.get("target")
        
        if not rel or not tgt:
            continue

        tgt_labels = tgt.get("_labels", []) or tgt.get("labels", [])
        is_attribute = "rdfs__Datatype" in tgt_labels or "owl__NamedIndividual" in tgt_labels or "XMLSchema" in (tgt.get("uri") or "")
        
        rel_type = rel.get("_rel_type") or rel.get("type") or "relates_to"
        tgt_label = tgt.get("rdfs__label") or tgt.get("label") or "Resource"

        if is_attribute:
            # Flatten into class as attribute
            cardinality = rel.get("cardinality") or "0..1"
            attributes_by_class[src_id].append({
                "name": rel_type,
                "type": tgt_label,
                "cardinality": cardinality,
                "definition": rel.get("skos__definition")
            })
        else:
            # Keep as edge to another class
            tgt_id = tgt.get("element_id") or tgt.get("_id")
            if not tgt_id:
                continue
                
            if tgt_id not in classes:
                 classes[tgt_id] = {
                    "key": tgt_id,
                    "label": tgt_label,
                    "uri": tgt.get("uri"),
                    "definition": tgt.get("skos__definition"),
                    "category": "class",
                    "attributes": []
                }
                 attributes_by_class[tgt_id] = attributes_by_class.get(tgt_id, [])

            link_key = (src_id, tgt_id, rel_type)
            if link_key not in seen_links:
                links.append({
                    "from": src_id,
                    "to": tgt_id,
                    "relationship": rel_type,
                    "uri": rel.get("uri"),
                    "definition": rel.get("skos__definition")
                })
                seen_links.add(link_key)

    # Attach attributes to classes
    final_nodes = []
    for cid, cdata in classes.items():
        cdata["attributes"] = attributes_by_class.get(cid, [])
        final_nodes.append(cdata)

    return GraphData(nodes=final_nodes, links=links, query=query)


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


@router.get("/relationships")
async def list_relationships():
    """
    List all distinct relationships between owl:Class nodes in the stagingdb.
    Returns relationship type, source/target class labels, URI, and cardinality.
    """
    db = get_db()
    try:
        query = """
        MATCH (source:owl__Class)-[r]->(target)
        WHERE (target:owl__Class OR target:owl__NamedIndividual OR target:rdfs__Datatype)
          AND type(r) <> 'rdfs__subClassOf'
          AND source.rdfs__label IS NOT NULL
          AND NOT source.rdfs__label =~ '^N[0-9a-f]{32}$'
        RETURN DISTINCT
            source.rdfs__label AS source_class,
            source.uri AS source_uri,
            type(r) AS relationship_type,
            coalesce(r.rdfs__label, type(r)) AS relationship_label,
            r.uri AS rel_uri,
            coalesce(r.cardinality, '0..1') AS cardinality,
            r.requirement AS requirement,
            coalesce(target.rdfs__label, target.uri, 'Resource') AS target_class,
            target.uri AS target_uri
        ORDER BY source_class, relationship_type
        """
        results = db.execute_cypher(query, name="list_relationships")
        return [
            {
                "source_class": row["source_class"],
                "relationship_type": row["relationship_type"],
                "relationship_label": row["relationship_label"],
                "target_class": row["target_class"],
                "cardinality": row["cardinality"],
                "requirement": row["requirement"],
                "uri": row.get("rel_uri"),
            }
            for row in results
        ]
    except Exception as e:
        logger.error(f"Error listing relationships: {e}")
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
        MATCH (c:owl__Class)
        WHERE any(lbl IN CASE WHEN c.rdfs__label IS :: LIST<ANY> THEN c.rdfs__label ELSE [c.rdfs__label] END WHERE toLower(toString(lbl)) = toLower($label)) OR c.uri = $label
        
        OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
        WITH c, coalesce(parent, c) AS classNode
        
        MATCH (classNode)-[r]->(target)
        WHERE (target:owl__Class OR target:owl__NamedIndividual OR target:rdfs__Datatype)
          AND (r.materialized = true OR r.materialized IS NULL)
          AND type(r) <> "rdfs__subClassOf"
        
        RETURN DISTINCT
          c.rdfs__label AS SourceClassLabel,
          c.uri AS SourceClassURI,
          c.skos__definition AS SourceClassDef,
          type(r) AS RelType,
          r.uri AS RelURI,
          r.skos__definition AS RelDef,
          coalesce(r.cardinality, "0..1") AS Cardinality,
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


def data_model_to_graph_data(dm: dict) -> GraphData:
    """Convert a DataModel (from extract_data_model tool) to GraphData format."""
    nodes = {}  # Use dict to avoid duplicates
    links = []
    
    # Process nodes (Classes and their Datatype Properties)
    for node in dm.get("nodes", []):
        src_label = node.get("label")
        if src_label not in nodes:
            nodes[src_label] = {
                "key": src_label,
                "label": src_label,
                "uri": node.get("uri"),
                "definition": node.get("description"),
                "category": "class"
            }
        
        # Datatype properties as separate nodes for visualization consistency
        for prop in node.get("properties", []):
            tgt_label = prop.get("type", "Resource")
            if tgt_label not in nodes:
                nodes[tgt_label] = {
                    "key": tgt_label,
                    "label": tgt_label,
                    "uri": prop.get("uri"),
                    "definition": prop.get("description"),
                    "category": "datatype"
                }
            
            links.append({
                "from": src_label,
                "to": tgt_label,
                "relationship": prop.get("name"),
                "uri": prop.get("uri"),
                "definition": prop.get("description"),
                "cardinality": prop.get("cardinality"),
                "requirement": "Mandatory" if prop.get("mandatory") else "Optional"
            })
        
    # Process relationships (Object Properties)
    for rel in dm.get("relationships", []):
        src_label = rel.get("start_node_label")
        tgt_label = rel.get("end_node_label")
        
        # Ensure nodes exist
        if src_label not in nodes:
            nodes[src_label] = {"key": src_label, "label": src_label, "category": "class"}
        if tgt_label not in nodes:
            nodes[tgt_label] = {"key": tgt_label, "label": tgt_label, "category": "class"}
            
        links.append({
            "from": src_label,
            "to": tgt_label,
            "relationship": rel.get("type"),
            "uri": rel.get("uri"),
            "definition": rel.get("description")
        })
        
    return GraphData(nodes=list(nodes.values()), links=links)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat interface for AI-assisted schema review.
    Uses the Onto2AI MCP client to leverage ontology tools.
    """
    try:
        client = await get_onto2ai_client()
        
        # Call the MCP-powered agent
        client_res = await client.chat(request.message)
        response_text = client_res.get("response", "")
        extracted_dm = client_res.get("data_model")
        
        # Ensure response_text is a string (defensive check)
        if not isinstance(response_text, str):
            logger.warning(f"Response text is not a string (type: {type(response_text)}). Converting to string.")
            response_text = str(response_text)

        graph_data = None

        # 1. Use explicitly extracted data model if available
        if extracted_dm:
            logger.info("Using explicitly extracted data model from tool results.")
            graph_data = data_model_to_graph_data(extracted_dm)
        
        # 2. Fallback to Smart Visualization if no data model extracted
        if not graph_data:
            # Extract potential class names (simple heuristic: common ontology terms or capitalized words)
            # We'll check the stagingdb to see if any of these are actual classes
            import re
            # Look for quoted strings or capitalised words that might be class names
            potential_classes = re.findall(r"['\"]([^'\"]+)['\"]", response_text)
            
            # Also check for common classes if they appear in the text
            db = get_db()
            # Get all classes currently in staging
            class_query = "MATCH (c:owl__Class) RETURN c.rdfs__label as label"
            staging_classes = {row["label"].lower() for row in db.execute_cypher(class_query) if row["label"]}
            
            detected_class = None
            # Check if any identified potential classes are in staging
            for p in potential_classes:
                if p.lower() in staging_classes:
                    detected_class = p
                    break
            
            # If no quoted class found, look for any staging class mentioned in text
            if not detected_class:
                words = set(re.findall(r'\b\w+\b', response_text.lower()))
                common_mentions = words.intersection(staging_classes)
                if common_mentions:
                    # Pick the most likely one (e.g. the one appearing first or just a stable pick)
                    detected_class = list(common_mentions)[0]

            if detected_class:
                logger.info(f"Smart visualization detected class: {detected_class}")
                # Fetch graph data for the detected class using a more robust pattern
                query = """
                MATCH (c:owl__Class)
                WHERE any(lbl IN CASE WHEN c.rdfs__label IS :: LIST<ANY> THEN c.rdfs__label ELSE [c.rdfs__label] END WHERE toLower(toString(lbl)) = toLower($label)) OR c.uri = $label
                
                OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
                WITH DISTINCT c, coalesce(parent, c) AS classNode
                
                // Materialized relationships (including inherited)
                OPTIONAL MATCH (classNode)-[r]->(target)
                WHERE (target:owl__Class OR target:owl__NamedIndividual OR target:rdfs__Datatype)
                  AND (r.materialized = true OR r.materialized IS NULL)
                  AND type(r) <> "rdfs__subClassOf"
                
                RETURN DISTINCT c, classNode, r, target
                """
                results = db.execute_cypher(query, params={"label": detected_class}, name="smart_chat_viz")
                graph_data = results_to_graph_data(results, query=query.replace("$label", f"'{detected_class}'").strip())
                
                # Mark original class as center
                if graph_data and graph_data.nodes:
                    for node in graph_data.nodes:
                        # Case-insensitive comparison for stable labeling
                        if node["label"].lower() == detected_class.lower():
                            node["isCenter"] = True
                        elif node["uri"] == detected_class:
                            node["isCenter"] = True

        return ChatResponse(
            response=response_text,
            suggestions=None,
            graph_data=graph_data
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cypher", response_model=CypherResponse)
async def execute_cypher(request: CypherRequest):
    """
    Execute a read-only Cypher query against stagingdb.
    Automatically detects if result is graph-like and provides visualization data.
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
        
        if not results:
            return CypherResponse(
                results=[],
                count=0,
                result_type="table",
                table_columns=[]
            )
        
        # Get column names from first result
        columns = list(results[0].keys()) if results else []
        
        # Check if any column contains serialized Neo4j nodes or relationships
        # Check first few rows in case of nulls in the first row
        has_nodes = False
        has_relationships = False
        node_columns = []
        rel_columns = []
        
        for col in columns:
            found_type = False
            for i in range(min(5, len(results))):
                val = results[i].get(col)
                if isinstance(val, dict):
                    if val.get("_type") == "node":
                        has_nodes = True
                        node_columns.append(col)
                        found_type = True
                        break
                    elif val.get("_type") == "relationship":
                        has_relationships = True
                        rel_columns.append(col)
                        found_type = True
                        break
        
        # Detect if this is a graph-like result (column-based patterns)
        graph_patterns = [
            ("SourceClassLabel", "TargetClassLabel", "RelType"),
            ("SourceClass", "TargetClass", "RelType"),
            ("source", "target", "type"),
            ("from", "to", "relationship"),
            ("sourceLabel", "targetLabel", "relType"),
        ]
        
        is_pattern_graph = False
        source_col, target_col, rel_col = None, None, None
        
        for src, tgt, rel in graph_patterns:
            if src in columns and tgt in columns:
                source_col, target_col = src, tgt
                rel_col = rel if rel in columns else None
                is_pattern_graph = True
                break
        
        # Determine if this query returns graph data
        has_graph_items = False
        for row in results:
            for val in row.values():
                if isinstance(val, dict) and val.get("_type") in ["node", "relationship", "path"]:
                    has_graph_items = True
                    break
                if isinstance(val, list) and any(isinstance(v, dict) and v.get("_type") in ["node", "relationship"] for v in val):
                    has_graph_items = True
                    break
            if has_graph_items: break

        graph_data = None
        result_type = "table"

        if has_graph_items:
            graph_data = results_to_graph_data(results, query=request.query)
            result_type = "graph"
        elif source_col and target_col:
            # Table-based graph fallback
            nodes = {}
            links = []
            for row in results:
                s = str(row.get(source_col, "Unknown"))
                t = str(row.get(target_col, "Unknown"))
                r = str(row.get(rel_col, "relates_to")) if rel_col else "relates_to"
                if s not in nodes: nodes[s] = {"key": s, "label": s, "category": "class"}
                if t not in nodes: nodes[t] = {"key": t, "label": t, "category": "class"}
                links.append({"from": s, "to": t, "relationship": r})
            graph_data = GraphData(nodes=list(nodes.values()), links=links, query=request.query)
            result_type = "graph"

        return CypherResponse(
            results=results,
            count=len(results),
            result_type=result_type,
            graph_data=graph_data,
            table_columns=columns
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing Cypher: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph-data/{class_name}")
async def get_graph_data(class_name: str):
    """
    Get graph data formatted for GoJS visualization using inheritance exploration.
    Uses the requested Cypher pattern to show base and superclass relationships.
    """
    db = get_db()
    try:
        # Optimized inheritance-aware query pattern matching get_materialized_schema logic
        query = """
        MATCH (c:owl__Class)
        WHERE any(lbl IN CASE WHEN c.rdfs__label IS :: LIST<ANY> THEN c.rdfs__label ELSE [c.rdfs__label] END WHERE toLower(toString(lbl)) = toLower($label)) OR c.uri = $label
        
        OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
        WITH DISTINCT c, coalesce(parent, c) AS classNode
        
        // Materialized relationships (including inherited)
        OPTIONAL MATCH (classNode)-[r]->(target)
        WHERE (target:owl__Class OR target:owl__NamedIndividual OR target:rdfs__Datatype)
          AND (r.materialized = true OR r.materialized IS NULL)
          AND type(r) <> "rdfs__subClassOf"
        
        RETURN DISTINCT c, classNode, r, target
        """
        results = db.execute_cypher(query, params={"label": class_name}, name="get_graph_data_enhanced")
        
        # Build graph data from results
        graph = results_to_graph_data(results, query=query.replace("$label", f"'{class_name}'").strip())
        
        # Mark center node
        for node in graph.nodes:
            if node["label"].lower() == class_name.lower():
                node["isCenter"] = True
        
        return graph
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
        # Query aligned with get_materialized_schema logic + incoming focus
        query = """
        MATCH (center:owl__Class)
        WHERE any(lbl IN CASE WHEN center.rdfs__label IS :: LIST<ANY> THEN center.rdfs__label ELSE [center.rdfs__label] END WHERE toLower(toString(lbl)) = toLower($label)) OR center.uri = $label
        
        // Inheritance for outgoing properties
        OPTIONAL MATCH (center)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
        WITH center, coalesce(parent, center) AS classNode
        
        // Outgoing materialized relationships (including inherited)
        OPTIONAL MATCH (classNode)-[r_out]->(target)
        WHERE (target:owl__Class OR target:owl__NamedIndividual OR target:rdfs__Datatype)
          AND (r_out.materialized = true OR r_out.materialized IS NULL)
          AND type(r_out) <> "rdfs__subClassOf"
        
        // Incoming relationships (to the focal class itself)
        OPTIONAL MATCH (source)-[r_in]->(center)
        WHERE (source:owl__Class OR source:owl__NamedIndividual)
          AND (r_in.materialized = true OR r_in.materialized IS NULL)
          AND type(r_in) <> "rdfs__subClassOf"
        
        RETURN center, classNode, r_out, target, source, r_in
        """
        results = db.execute_cypher(query, params={"label": node_label}, name="get_node_focus_data")
        
        graph = results_to_graph_data(results, query=query.replace("$label", f"'{node_label}'").strip())
        
        # Mark center node
        if graph and graph.nodes:
            for node in graph.nodes:
                if node["label"].lower() == node_label.lower():
                    node["isCenter"] = True
                elif node["uri"] == node_label:
                    node["isCenter"] = True
        
        return graph
    except Exception as e:
        logger.error(f"Error getting node focus data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/uml-data/{class_name}")
async def get_uml_data(class_name: str):
    """
    Get graph data optimized for UML/Pydantic box visualization.
    Datatypes are flattened into attributes of the class node.
    """
    db = get_db()
    try:
        # Robust query pattern matching get_materialized_schema logic
        query = """
        MATCH (c:owl__Class)
        WHERE any(lbl IN CASE WHEN c.rdfs__label IS :: LIST<ANY> THEN c.rdfs__label ELSE [c.rdfs__label] END WHERE toLower(toString(lbl)) = toLower($label)) OR c.uri = $label
        
        OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
        WITH DISTINCT c, coalesce(parent, c) AS classNode
        
        // Materialized relationships (including inherited)
        OPTIONAL MATCH (classNode)-[r]->(target)
        WHERE (target:owl__Class OR target:owl__NamedIndividual OR target:rdfs__Datatype)
          AND (r.materialized = true OR r.materialized IS NULL)
          AND type(r) <> "rdfs__subClassOf"
        
        RETURN DISTINCT c, classNode, r, target
        """
        results = db.execute_cypher(query, params={"label": class_name}, name="get_uml_data")
        
        # Build UML data (flattened)
        uml_graph = results_to_uml_data(results, query=query.replace("$label", f"'{class_name}'").strip())
        
        # Mark center node
        for node in uml_graph.nodes:
            # In UML data, keys are element IDs, but we might still want to check labels
            if node["label"].lower() == class_name.lower():
                node["isCenter"] = True
                
        return uml_graph
    except Exception as e:
        logger.error(f"Error getting UML data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm", response_model=LLMStatus)
async def get_llm_status():
    """Get the current LLM and available options."""
    global _current_llm
    
    # Refresh from env if not manually set yet
    env_model = os.getenv("LLM_MODEL_NAME")
    if _current_llm is None:
        _current_llm = env_model or "gemini-2.0-flash-exp"
        
    # Ensure current model is in available list
    if _current_llm not in AVAILABLE_LLMS:
        AVAILABLE_LLMS.append(_current_llm)
        
    return LLMStatus(
        current_llm=_current_llm,
        available_llms=AVAILABLE_LLMS
    )


@router.post("/llm", response_model=LLMStatus)
async def update_llm(request: LLMUpdateRequest):
    """Switch the current LLM."""
    global _current_llm, _onto2ai_client
    
    # Allow any model name to be set via API
    _current_llm = request.llm_name
    if _current_llm not in AVAILABLE_LLMS:
        AVAILABLE_LLMS.append(_current_llm)
    logger.info(f"Switched LLM to: {_current_llm}")
    
    # Reset onto2ai client to use the new LLM
    _onto2ai_client = None
    
    return LLMStatus(
        current_llm=_current_llm,
        available_llms=AVAILABLE_LLMS
    )
