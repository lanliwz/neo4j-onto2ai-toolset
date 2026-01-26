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
    ChatRequest, ChatResponse, GraphData,
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
    Uses GPT-5.2 with function calling to detect schema queries and return graph data.
    """
    try:
        import openai
        import json
        
        client = openai.AsyncOpenAI()
        model = os.getenv("GPT_MODEL_NAME", "gpt-4o")
        
        # Define the function for schema queries
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_class_schema",
                    "description": "Get the schema and graph visualization for a specific ontology class from the staging database. Use this when the user asks about a class, schema, or wants to see/visualize a class.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "class_name": {
                                "type": "string",
                                "description": "The name of the class to retrieve (e.g., 'person', 'account', 'payment', 'currency')"
                            }
                        },
                        "required": ["class_name"]
                    }
                }
            }
        ]
        
        # First API call with function calling
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": """You are an ontology expert helping users understand and enhance database schemas. 
The user is working with FIBO (Financial Industry Business Ontology) schemas in a staging database.
When users ask about a specific class or want to see a schema, use the get_class_schema function.
Provide helpful, concise guidance about schema design, relationships, and best practices."""},
                {"role": "user", "content": request.message}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        assistant_message = response.choices[0].message
        graph_data = None
        
        # Check if the model wants to call a function
        if assistant_message.tool_calls:
            tool_call = assistant_message.tool_calls[0]
            if tool_call.function.name == "get_class_schema":
                # Parse the function arguments
                args = json.loads(tool_call.function.arguments)
                class_name = args.get("class_name", "").lower()
                
                # Fetch graph data from stagingdb
                db = get_db()
                query = """
                MATCH (c:owl__Class)
                WHERE toLower(c.rdfs__label) = toLower($label) OR c.uri = $label
                OPTIONAL MATCH (c)-[:owl__subClassOf*0..2]->(parent:owl__Class)
                WITH DISTINCT coalesce(parent, c) AS classNode, c
                
                OPTIONAL MATCH (classNode)-[r_out]->(target)
                WHERE r_out.materialized = true
                
                OPTIONAL MATCH (source)-[r_in]->(classNode)
                WHERE r_in.materialized = true
                
                WITH c, classNode,
                     collect(DISTINCT {rel: r_out, other: target, dir: 'out'}) AS outRels,
                     collect(DISTINCT {rel: r_in, other: source, dir: 'in'}) AS inRels
                
                UNWIND (outRels + inRels) AS relData
                WITH c, classNode, relData
                WHERE relData.rel IS NOT NULL
                
                RETURN DISTINCT
                  coalesce(classNode.rdfs__label, classNode.uri, 'Unknown') AS SourceLabel,
                  classNode.uri AS SourceURI,
                  classNode.skos__definition AS SourceDef,
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
                results = db.execute_cypher(query, params={"label": class_name}, name="chat_get_graph_data")
                
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
                            "category": "class",
                            "isCenter": True
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
                
                if nodes:
                    graph_data = GraphData(
                        nodes=list(nodes.values()),
                        links=links,
                        query=query.replace("$label", f"'{class_name}'").strip()
                    )
                
                # Make a second API call to get the response with function result
                function_result = f"Found schema for '{class_name}' with {len(nodes)} classes and {len(links)} relationships."
                
                response2 = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": """You are an ontology expert helping users understand and enhance database schemas. 
The user is working with FIBO (Financial Industry Business Ontology) schemas in a staging database.
Provide helpful, concise guidance about schema design, relationships, and best practices."""},
                        {"role": "user", "content": request.message},
                        assistant_message,
                        {"role": "tool", "tool_call_id": tool_call.id, "content": function_result}
                    ]
                )
                
                return ChatResponse(
                    response=response2.choices[0].message.content,
                    suggestions=None,
                    graph_data=graph_data
                )
        
        # No function call - just return the text response
        return ChatResponse(
            response=assistant_message.content,
            suggestions=None,
            graph_data=None
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
        
        # If we have Neo4j nodes or relationships, build graph from them
        if has_nodes or has_relationships:
            nodes = {}
            links = []
            
            for row in results:
                # Process nodes
                for col in node_columns:
                    node_data = row.get(col)
                    if isinstance(node_data, dict) and node_data.get("_type") == "node":
                        node_id = node_data.get("_id", "")
                        labels = node_data.get("_labels", [])
                        label = node_data.get("rdfs__label") or node_data.get("label") or (labels[0] if labels else node_id[-8:])
                        
                        if node_id and node_id not in nodes:
                            # Determine category from labels
                            category = "class"
                            if "rdfs__Datatype" in labels:
                                category = "datatype"
                            elif "owl__NamedIndividual" in labels:
                                category = "individual"
                            
                            nodes[node_id] = {
                                "key": label,
                                "label": label,
                                "uri": node_data.get("uri"),
                                "definition": node_data.get("skos__definition"),
                                "category": category,
                                "_id": node_id
                            }
                
                # Process relationships and create nodes from start/end if needed
                for col in rel_columns:
                    rel_data = row.get(col)
                    if isinstance(rel_data, dict) and rel_data.get("_type") == "relationship":
                        start_id = rel_data.get("_start")
                        end_id = rel_data.get("_end")
                        rel_type = rel_data.get("_rel_type", "relates_to")
                        
                        if start_id and end_id:
                            # Create placeholder nodes if they don't exist
                            if start_id not in nodes:
                                placeholder_label = f"Node-{start_id[-8:]}"
                                nodes[start_id] = {
                                    "key": placeholder_label,
                                    "label": placeholder_label,
                                    "uri": None,
                                    "definition": None,
                                    "category": "class",
                                    "_id": start_id
                                }
                                
                            if end_id not in nodes:
                                placeholder_label = f"Node-{end_id[-8:]}"
                                nodes[end_id] = {
                                    "key": placeholder_label,
                                    "label": placeholder_label,
                                    "uri": None,
                                    "definition": None,
                                    "category": "class",
                                    "_id": end_id
                                }
                            
                            # Find node labels for start and end
                            start_label = nodes[start_id]["label"]
                            end_label = nodes[end_id]["label"]
                            
                            links.append({
                                "from": start_label,
                                "to": end_label,
                                "relationship": rel_type,
                                "uri": rel_data.get("uri")
                            })
            
            return CypherResponse(
                results=results,
                count=len(results),
                result_type="graph",
                graph_data=GraphData(
                    nodes=list(nodes.values()),
                    links=links,
                    query=request.query
                ),
                table_columns=columns
            )
        
        elif is_pattern_graph:
            # Build graph data from column patterns
            nodes = {}
            links = []
            
            for row in results:
                src_label = row.get(source_col)
                tgt_label = row.get(target_col)
                
                # Add source node
                if src_label and src_label not in nodes:
                    nodes[src_label] = {
                        "key": src_label,
                        "label": src_label,
                        "uri": row.get("SourceClassURI") or row.get("source_uri"),
                        "definition": row.get("SourceClassDef") or row.get("source_def"),
                        "category": "class",
                        "isCenter": True
                    }
                
                # Add target node
                if tgt_label and tgt_label not in nodes:
                    target_uri = row.get("TargetClassURI") or row.get("target_uri") or ""
                    prop_type = row.get("PropMetaType") or row.get("property_type") or ""
                    is_datatype = "Datatype" in prop_type or "XMLSchema" in target_uri
                    
                    nodes[tgt_label] = {
                        "key": tgt_label,
                        "label": tgt_label,
                        "uri": target_uri,
                        "definition": row.get("TargetClassDef") or row.get("target_def"),
                        "category": "datatype" if is_datatype else "class"
                    }
                
                # Add link
                if src_label and tgt_label:
                    links.append({
                        "from": src_label,
                        "to": tgt_label,
                        "relationship": row.get(rel_col) if rel_col else "relates_to",
                        "uri": row.get("RelURI") or row.get("rel_uri"),
                        "definition": row.get("RelDef") or row.get("rel_def"),
                        "cardinality": row.get("Cardinality") or row.get("cardinality"),
                        "requirement": row.get("Requirement") or row.get("requirement")
                    })
            
            return CypherResponse(
                results=results,
                count=len(results),
                result_type="graph",
                graph_data=GraphData(
                    nodes=list(nodes.values()),
                    links=links,
                    query=request.query
                ),
                table_columns=columns
            )
        else:
            # Tabular result
            return CypherResponse(
                results=results,
                count=len(results),
                result_type="table",
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
