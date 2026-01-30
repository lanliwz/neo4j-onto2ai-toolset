import json
import sys
import os
from typing import List, Union, Optional, Dict, Any

# Add project root to sys.path to allow running as a script
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from neo4j_onto2ai_toolset.onto2ai_tool_config import semanticdb, get_llm, get_staging_db
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger
from neo4j_onto2ai_toolset.onto2schema.schema_types import DataModel, Node, Relationship, Property

mcp = FastMCP("Onto2AI")

@mcp.tool()
async def get_materialized_schema(
    class_names: Union[str, List[str]], 
    database: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieve the materialized schema for one or more ontology classes.
    
    Args:
        class_names: One or more class labels to query (e.g., "person" or ["person", "account"])
        database: Optional database name to query. Defaults to the main ontology database.
                  Use "stagingdb" to query the staging database.
    
    Formatting Instructions (CRITICAL):
    - ALWAYS show the output in two distinct sections: (1) Classes and (2) Relationships.
    - Render both sections as Markdown TABLES.
    - Section 1: Use the 'Label' as a clickable Markdown link to its 'URI'.
    - Section 2: Use the 'Relationship Type' as a clickable Markdown link to its 'URI'.
    - Do not show URIs in separate columns unless labels are missing.
    
    Returns:
        Section 1: Classes with labels, definitions, and URIs.
        Section 2: Relationships with definitions, URIs, source/target, and constraints.
    """
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    
    # Use specified database or default to semanticdb
    db = get_staging_db(database) if database else semanticdb
    
    query = """
    MATCH (c:owl__Class)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels
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
      coalesce(target.rdfs__label, target.uri, "Resource") AS TargetClassLabel,
      target.uri AS TargetClassURI,
      target.skos__definition AS TargetClassDef
    ORDER BY SourceClassLabel, RelType
    """
    
    logger.info(f"Fetching enhanced materialized schema for: {labels} from database: {database or 'default'}")
    try:
        results = db.execute_cypher(query, params={"labels": labels}, name="get_materialized_schema_tool")
        
        classes_section = {}
        relationships_section = []
        
        for row in results:
            # Add Source Class to section 1
            src_label = row['SourceClassLabel']
            if src_label not in classes_section:
                classes_section[src_label] = {
                    "label": src_label,
                    "uri": row['SourceClassURI'],
                    "definition": row['SourceClassDef']
                }
            
            # Add Target Class to section 1
            tgt_label = row['TargetClassLabel']
            if tgt_label not in classes_section and tgt_label != "Resource":
                classes_section[tgt_label] = {
                    "label": tgt_label,
                    "uri": row['TargetClassURI'],
                    "definition": row['TargetClassDef']
                }
            
            # Add Relationship to section 2
            relationships_section.append({
                "source_class": src_label,
                "source_class_uri": row['SourceClassURI'],
                "relationship_type": row['RelType'],
                "target_class": tgt_label,
                "target_class_uri": row['TargetClassURI'],
                "definition": row['RelDef'],
                "uri": row['RelURI'],
                "cardinality": row['Cardinality'],
                "requirement": row['Requirement']
            })
            
        return {
            "database": database or "default",
            "section_1_classes": list(classes_section.values()),
            "section_2_relationships": relationships_section
        }
    except Exception as e:
        logger.error(f"Error fetching enhanced materialized schema: {e}")
        return {"error": str(e)}
    finally:
        # Close the connection if using a custom database
        if database:
            db.close()

@mcp.tool()
async def get_ontological_schema(class_names: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Retrieve the raw ontological schema (meta-model view) for one or more classes.
    
    Formatting Instructions (CRITICAL):
    - ALWAYS show the output in two distinct sections: (1) Classes and (2) Ontological Definitions.
    - Render both sections as Markdown TABLES.
    - Section 1: Use the 'Label' as a clickable Markdown link to its 'URI'.
    - Section 2: Use the 'Property' name as a clickable Markdown link to its 'Property URI'.
    - Do not show URI or Property URI in separate columns unless labels/names are missing.
    
    Returns:
        Section 1: Classes/Ranges with labels, definitions, and URIs.
        Section 2: Ontological mappings with full logic, URIs, and constraints.
    """
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    
    query = """
    MATCH (c:owl__Class)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels

    // Domain-based properties (Direct)
    OPTIONAL MATCH (directProp)-[:rdfs__domain|rdfs__subClassOf*0..1]->(parent)
    WHERE directProp:owl__ObjectProperty OR directProp:owl__DatatypeProperty
    OPTIONAL MATCH (directProp)-[:rdfs__range]->(directRange)

    // Restriction-based properties (Logic/Constraints)
    OPTIONAL MATCH (parent)-[:rdfs__subClassOf]->(rest:owl__Restriction)-[:owl__onProperty]->(restProp)
    OPTIONAL MATCH (rest)-[:owl__someValuesFrom|owl__allValuesFrom|owl__onClass|owl__onDataRange]->(restRange)
    OPTIONAL MATCH (rest)-[r_some:owl__someValuesFrom]->()

    WITH c, parent,
         coalesce(directProp, restProp) AS property, 
         coalesce(directRange, restRange) AS range,
         rest,
         r_some IS NOT NULL AS hasSome

    WHERE property IS NOT NULL

    WITH c, parent, property, range, rest,
         CASE 
           WHEN rest.owl__cardinality IS NOT NULL THEN toString(rest.owl__cardinality)
           WHEN rest.owl__qualifiedCardinality IS NOT NULL THEN toString(rest.owl__qualifiedCardinality)
           WHEN rest.owl__minCardinality IS NOT NULL OR rest.owl__maxCardinality IS NOT NULL OR rest.owl__minQualifiedCardinality IS NOT NULL OR rest.owl__maxQualifiedCardinality IS NOT NULL OR hasSome
           THEN 
             coalesce(toString(rest.owl__minCardinality), toString(rest.owl__minQualifiedCardinality), CASE WHEN hasSome THEN "1" ELSE "0" END) + 
             ".." + 
             coalesce(toString(rest.owl__maxCardinality), toString(rest.owl__maxQualifiedCardinality), 
                      CASE WHEN property:owl__FunctionalProperty THEN "1" ELSE "*" END)
           ELSE 
             CASE WHEN property:owl__FunctionalProperty THEN "0..1" ELSE "0..*" END
         END AS Cardinality

    WITH c, parent, property, range, Cardinality,
         CASE 
           WHEN Cardinality STARTS WITH "0.." THEN "Optional"
           WHEN Cardinality CONTAINS ".." THEN 
             CASE WHEN split(Cardinality, "..")[0] = "0" THEN "Optional" ELSE "Mandatory" END
           WHEN Cardinality = "0" THEN "Optional"
           ELSE "Mandatory" 
         END AS Requirement

    RETURN DISTINCT
      c.rdfs__label AS RequestedClass,
      c.uri AS RequestedClassURI,
      c.skos__definition AS RequestedClassDef,
      parent.rdfs__label AS DefinitionSource,
      parent.uri AS DefinitionSourceURI,
      property.rdfs__label AS PropertyLabel,
      property.uri AS PropertyURI,
      property.skos__definition AS PropertyDef,
      coalesce(range.rdfs__label, range.uri, "Resource") AS RangeLabel,
      range.uri AS RangeURI,
      range.skos__definition AS RangeDef,
      Cardinality,
      Requirement
    ORDER BY RequestedClass, DefinitionSource, PropertyLabel
    """
    
    logger.info(f"Fetching enhanced ontological schema for: {labels}")
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="get_ontological_schema_tool")
        
        classes_section = {}
        ontological_section = []
        
        for row in results:
            # Add Requested Class/Source Class to section 1
            req_label = row['RequestedClass']
            if req_label not in classes_section:
                classes_section[req_label] = {
                    "label": req_label,
                    "uri": row['RequestedClassURI'],
                    "definition": row['RequestedClassDef']
                }
            
            # Add Definition Source (if different)
            src_label = row['DefinitionSource']
            if src_label not in classes_section:
                classes_section[src_label] = {
                    "label": src_label,
                    "uri": row['DefinitionSourceURI'],
                    "definition": None # Cypher can be expanded to get this if needed
                }

            # Add Range/Target to section 1
            rng_label = row['RangeLabel']
            if rng_label not in classes_section and rng_label != "Resource":
                classes_section[rng_label] = {
                    "label": rng_label,
                    "uri": row['RangeURI'],
                    "definition": row['RangeDef']
                }
            
            # Add Ontological Definition to section 2
            ontological_section.append({
                "requested_class": req_label,
                "requested_class_uri": row['RequestedClassURI'],
                "definition_source": src_label,
                "definition_source_uri": row['DefinitionSourceURI'],
                "property": row['PropertyLabel'],
                "property_uri": row['PropertyURI'],
                "property_definition": row['PropertyDef'],
                "range": rng_label,
                "range_uri": row['RangeURI'],
                "cardinality": row['Cardinality'],
                "requirement": row['Requirement']
            })
            
        return {
            "section_1_classes": list(classes_section.values()),
            "section_2_ontological_definitions": ontological_section
        }
    except Exception as e:
        logger.error(f"Error fetching enhanced ontological schema: {e}")
        return {"error": str(e)}

async def _extract_data_model(class_names: Union[str, List[str]]) -> DataModel:
    """Internal helper to extract a DataModel from the ontology."""
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    
    query = """
    // Match the requested class
    MATCH (c:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels
    
    // Optional inheritance chain - make rdfs__subClassOf optional
    OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
    WITH c, coalesce(parent, c) AS classNode
    
    // Get materialized relationships to owl__Class targets
    MATCH (classNode)-[r]->(target:owl__Class)
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
      r.property_type AS PropMetaType,
      coalesce(target.rdfs__label, target.uri, "Resource") AS TargetClassLabel,
      target.uri AS TargetClassURI,
      target.skos__definition AS TargetClassDef
    
    UNION
    
    // Match the requested class again for rdfs__Datatype targets
    MATCH (c:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels
    
    OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
    WITH c, coalesce(parent, c) AS classNode
    
    // Get materialized relationships to rdfs__Datatype targets
    MATCH (classNode)-[r]->(target:rdfs__Datatype)
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
      r.property_type AS PropMetaType,
      coalesce(target.rdfs__label, target.uri, "Resource") AS TargetClassLabel,
      target.uri AS TargetClassURI,
      target.skos__definition AS TargetClassDef
    
    ORDER BY SourceClassLabel, RelType
    """
    
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="internal_extract_data_model")
        
        nodes_dict = {}
        relationships = []
        
        for row in results:
            cls_name = row['SourceClassLabel']
            if cls_name not in nodes_dict:
                nodes_dict[cls_name] = Node(
                    label=cls_name, 
                    description=row['SourceClassDef'],
                    properties=[],
                    uri=row['SourceClassURI']
                )
            
            is_rel = (row['PropMetaType'] == 'owl__ObjectProperty')
            
            prop_obj = Property(
                name=row['RelType'],
                type=row['TargetClassLabel'],
                description=row['RelDef'],
                mandatory=(row['Requirement'] == 'Mandatory'),
                cardinality=row['Cardinality'],
                uri=row['RelURI']
            )
            
            if is_rel:
                relationships.append(Relationship(
                    type=row['RelType'],
                    start_node_label=cls_name,
                    end_node_label=row['TargetClassLabel'],
                    description=row['RelDef'],
                    uri=row['RelURI']
                ))
            else:
                nodes_dict[cls_name].properties.append(prop_obj)
        
        return DataModel(
            nodes=list(nodes_dict.values()),
            relationships=relationships,
            metadata={"source_classes": labels, "engine": "Onto2AI-Materialized"}
        )
    except Exception as e:
        logger.error(f"Error in internal extraction: {e}")
        raise

@mcp.tool()
async def enhance_schema(class_names: Union[str, List[str]], instructions: str) -> DataModel:
    """
    Extract a model from ontology and enhance it using AI instructions.
    Returns the updated DataModel (JSON).
    """
    try:
        data_model = await _extract_data_model(class_names)
        
        prompt = f"""
        You are a data architect. Modify the following Neo4j DataModel based on these instructions: "{instructions}"
        
        Current DataModel (JSON):
        {data_model.model_dump_json(indent=2)}
        
        Return ONLY a valid JSON object matching the DataModel schema. 
        Ensure PascalCase for labels and SCREAMING_SNAKE_CASE for relationship types if adding new ones.
        Do not include markdown fences or any explanation.
        """
        
        response = await get_llm().ainvoke(prompt)
        content = str(response.content).strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
            
        updated_model_dict = json.loads(content)
        return DataModel(**updated_model_dict)
    except Exception as e:
        logger.error(f"Error enhancing schema: {e}")
        raise

@mcp.tool()
async def generate_schema_code(
    class_names: Union[str, List[str]], 
    target_type: str = "pydantic", 
    instructions: Optional[str] = None
) -> str:
    """
    Generate production-ready code (SQL, Pydantic, Neo4j) for one or more ontology classes.
    Optional 'instructions' allows on-the-fly AI enhancement of the base ontology schema.
    """
    try:
        # 1. Extract base model
        if instructions:
            data_model = await enhance_schema(class_names, instructions)
        else:
            data_model = await _extract_data_model(class_names)
            
        # 2. Generate code
        prompt = f"""
        You are a code generation expert. Generate {target_type} code for the following DataModel.
        
        DataModel (JSON):
        {data_model.model_dump_json(indent=2)}
        
        Constraints:
        - If 'pydantic', generate Python classes using Pydantic v2.
        - If 'sql', generate Oracle-compatible DDL.
        - If 'neo4j', generate Cypher CREATE CONSTRAINT/INDEX statements.
        
        Documentation Style (CRITICAL):
        - For Pydantic: Class definitions MUST be rendered as Python DOCSTRINGS (triple quotes) inside the class.
        - For SQL: Table definitions MUST be rendered using 'COMMENT ON TABLE [name] IS ...' statements.
        - Property and Relationship definitions MUST be included as INLINE COMMENTS (# for Python, -- for SQL, // for Cypher) next to the field or constraint.
        - Definitions should be for ANNOTATION ONLY; do not include them as functional data fields.
        
        Format:
        - Return ONLY the code. No explanations, no markdown fences.
        """
        
        response = await get_llm().ainvoke(prompt)
        return str(response.content).strip()
    except Exception as e:
        logger.error(f"Error generating schema code: {e}")
        return f"Error: {e}"

@mcp.tool()
async def generate_shacl_for_modelling(
    class_names: Union[str, List[str]], 
    instructions: Optional[str] = None
) -> str:
    """
    Generate modeling-ready SHACL files for one or more ontology classes.
    
    SHACL Standard (CRITICAL):
    - EXACT NAMESPACES: Use official FIBO/CMNS URIs for sh:targetClass and sh:path.
    - LOCAL IDENTIFIERS: Use ex: namespace (http://example.org/shacl/) for NodeShapes and PropertyShapes.
    - NAMING CONVENTION: Identify shapes as 'xxx4Modelling' (e.g., Person4Modelling).
    - INCORPORATE: All definitions, datatypes, and cardinality from the ontology.
    """
    try:
        # Extract base model (includes URIs)
        if instructions:
            data_model = await enhance_schema(class_names, instructions)
        else:
            data_model = await _extract_data_model(class_names)
            
        prompt = f"""
        You are a semantic modeling expert. Generate SHACL code in Turtle format for the following DataModel.
        
        DataModel (JSON):
        {data_model.model_dump_json(indent=2)}
        
        Formatting Rules (MANDATORY):
        1. NAMESPACES: 
           - Use 'ex: <http://example.org/shacl/>' for the Shape identifiers.
           - Use official ontologies (fibo, cmns, lcc, etc.) for the targets. Define necessary prefixes.
        2. SHAPE NAMING:
           - NodeShape identifiers MUST end with '4Modelling' (e.g. ex:Person4Modelling).
           - PropertyShape identifiers MUST end with '4Modelling' (e.g. ex:HasName4Modelling).
        3. TARGETS:
           - sh:targetClass MUST use the official URI provided in the DataModel.
           - sh:path MUST use the official URI provided in the DataModel.
        4. CONSTRAINTS:
           - Use sh:datatype, sh:minCount, sh:maxCount, and sh:node based on the DataModel properties.
           - Include sh:description using the ontological definitions.
        
        Format:
        - Return ONLY the Turtle code. No explanations, no markdown fences.
        """
        
        response = await get_llm().ainvoke(prompt)
        return str(response.content).strip()
    except Exception as e:
        logger.error(f"Error generating SHACL: {e}")
        return f"Error: {e}"

@mcp.tool()
async def staging_materialized_schema(
    class_names: Union[str, List[str]],
    staging_db_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract materialized schema for one or more ontology classes and copy 
    all involved classes and relationships to a staging Neo4j database.
    
    Args:
        class_names: One or more class labels to extract (e.g., "person" or ["person", "account"])
        staging_db_name: Target database name. Defaults to NEO4J_STAGING_DB_NAME env var.
    
    Returns:
        Summary of copied classes and relationships with counts.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
    
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    
    # Step 1: Extract materialized schema from source database
    query = """
    MATCH (c:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels
    OPTIONAL MATCH (c)-[:owl__subClassOf*0..]->(parent:owl__Class)
    WITH coalesce(parent, c) AS classNode, c
    MATCH (classNode)-[r]->(target)
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
      coalesce(target.rdfs__label, target.uri, "Resource") AS TargetClassLabel,
      target.uri AS TargetClassURI,
      target.skos__definition AS TargetClassDef,
      labels(target) AS TargetLabels
    ORDER BY SourceClassLabel, RelType
    """
    
    logger.info(f"Extracting materialized schema for staging: {labels}")
    
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="staging_extract")
        
        if not results:
            return {
                "status": "warning",
                "message": f"No materialized schema found for classes: {labels}",
                "classes_copied": 0,
                "relationships_copied": 0
            }
        
        # Step 2: Collect unique classes, datatypes, individuals and relationships
        classes = {}
        datatypes = {}
        named_individuals = {}
        relationships = []
        
        for row in results:
            # Collect source class
            src_uri = row['SourceClassURI']
            if src_uri and src_uri not in classes:
                classes[src_uri] = {
                    "uri": src_uri,
                    "label": row['SourceClassLabel'],
                    "definition": row['SourceClassDef']
                }
            
            # Collect target based on its type
            tgt_uri = row['TargetClassURI']
            tgt_labels = row.get('TargetLabels', []) or []
            
            if tgt_uri:
                # Check for XSD datatypes by URI pattern (they may be labeled as Resource)
                is_xsd_datatype = 'XMLSchema#' in tgt_uri or 'XMLSchema/' in tgt_uri
                
                if 'rdfs__Datatype' in tgt_labels or is_xsd_datatype:
                    if tgt_uri not in datatypes:
                        # Extract short name for XSD types
                        if is_xsd_datatype:
                            short_label = tgt_uri.split('#')[-1] if '#' in tgt_uri else tgt_uri.split('/')[-1]
                            label = f"xsd:{short_label}"
                        else:
                            label = row['TargetClassLabel']
                        datatypes[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": label,
                            "definition": row['TargetClassDef']
                        }
                elif 'owl__NamedIndividual' in tgt_labels:
                    if tgt_uri not in named_individuals:
                        named_individuals[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": row['TargetClassLabel'],
                            "definition": row['TargetClassDef']
                        }
                elif 'owl__Class' in tgt_labels:
                    if tgt_uri not in classes:
                        classes[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": row['TargetClassLabel'],
                            "definition": row['TargetClassDef']
                        }
                else:
                    # Default to class for unknown types (non-XSD)
                    if tgt_uri not in classes:
                        classes[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": row['TargetClassLabel'],
                            "definition": row['TargetClassDef']
                        }
            
            # Collect relationship
            relationships.append({
                "source_uri": src_uri,
                "target_uri": tgt_uri,
                "rel_type": row['RelType'],
                "rel_uri": row['RelURI'],
                "definition": row['RelDef'],
                "cardinality": row['Cardinality'],
                "requirement": row['Requirement'],
                "target_labels": tgt_labels
            })
        
        # Step 3: Connect to staging database
        staging_db = get_staging_db(staging_db_name)
        
        try:
            # Step 4a: Insert classes into staging database
            class_insert_query = """
            MERGE (c:owl__Class {uri: $uri})
            SET c.rdfs__label = $label,
                c.skos__definition = $definition
            """
            
            for cls in classes.values():
                staging_db.execute_cypher(
                    class_insert_query,
                    params={
                        "uri": cls["uri"],
                        "label": cls["label"],
                        "definition": cls["definition"]
                    },
                    name="staging_class_insert"
                )
            
            logger.info(f"Inserted {len(classes)} classes into staging database")
            
            # Step 4b: Insert datatypes into staging database
            datatype_insert_query = """
            MERGE (d:rdfs__Datatype {uri: $uri})
            SET d.rdfs__label = $label,
                d.skos__definition = $definition
            """
            
            for dt in datatypes.values():
                staging_db.execute_cypher(
                    datatype_insert_query,
                    params={
                        "uri": dt["uri"],
                        "label": dt["label"],
                        "definition": dt["definition"]
                    },
                    name="staging_datatype_insert"
                )
            
            logger.info(f"Inserted {len(datatypes)} datatypes into staging database")
            
            # Step 4c: Insert named individuals into staging database
            individual_insert_query = """
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i.skos__definition = $definition
            """
            
            for ind in named_individuals.values():
                staging_db.execute_cypher(
                    individual_insert_query,
                    params={
                        "uri": ind["uri"],
                        "label": ind["label"],
                        "definition": ind["definition"]
                    },
                    name="staging_individual_insert"
                )
            
            logger.info(f"Inserted {len(named_individuals)} named individuals into staging database")
            
            # Step 5: Insert relationships into staging database
            rel_types_created = set()
            
            for rel in relationships:
                rel_type = rel["rel_type"]
                if not rel_type:
                    continue
                
                tgt_labels = rel.get("target_labels", []) or []
                tgt_uri = rel.get("target_uri", "")
                
                # Check for XSD datatypes by URI pattern
                is_xsd_datatype = 'XMLSchema#' in tgt_uri or 'XMLSchema/' in tgt_uri
                
                # Determine target label based on type
                if 'rdfs__Datatype' in tgt_labels or is_xsd_datatype:
                    target_label = "rdfs__Datatype"
                elif 'owl__NamedIndividual' in tgt_labels:
                    target_label = "owl__NamedIndividual"
                else:
                    target_label = "owl__Class"
                
                rel_insert_query = f"""
                MATCH (source:owl__Class {{uri: $source_uri}})
                MATCH (target:{target_label} {{uri: $target_uri}})
                MERGE (source)-[r:{rel_type}]->(target)
                SET r.uri = $rel_uri,
                    r.skos__definition = $definition,
                    r.cardinality = $cardinality,
                    r.requirement = $requirement,
                    r.materialized = true
                """
                
                staging_db.execute_cypher(
                    rel_insert_query,
                    params={
                        "source_uri": rel["source_uri"],
                        "target_uri": rel["target_uri"],
                        "rel_uri": rel["rel_uri"],
                        "definition": rel["definition"],
                        "cardinality": rel["cardinality"],
                        "requirement": rel["requirement"]
                    },
                    name="staging_rel_insert"
                )
                rel_types_created.add(rel_type)
            
            logger.info(f"Inserted {len(relationships)} relationships into staging database")
            
        finally:
            staging_db.close()
        
        # Return summary
        return {
            "status": "success",
            "staging_database": staging_db_name or "stagingdb",
            "classes_copied": len(classes),
            "datatypes_copied": len(datatypes),
            "named_individuals_copied": len(named_individuals),
            "relationships_copied": len(relationships),
            "class_labels": [c["label"] for c in classes.values()],
            "datatype_labels": [d["label"] for d in datatypes.values()],
            "individual_labels": [i["label"] for i in named_individuals.values()],
            "relationship_types": list(rel_types_created)
        }
        
    except Exception as e:
        logger.error(f"Error staging materialized schema: {e}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    # Support HTTP transport if requested via command line
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "http":
        port = 8082
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                pass
        
        # FastMCP.run() doesn't support host/port as kwargs.
        # Since the mcp object is already initialized at the top level,
        # we update its settings directly.
        mcp.settings.port = port
        mcp.settings.host = "localhost"
        
        print(f"Starting Onto2AI MCP Server on HTTP port {port}...", file=sys.stderr)
        mcp.run(transport="sse")
    else:
        # By default, run using stdio for MCP integration
        mcp.run()

