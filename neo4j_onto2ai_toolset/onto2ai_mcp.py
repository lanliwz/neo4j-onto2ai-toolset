import json
from typing import List, Union, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from neo4j_onto2ai_toolset.onto2ai_tool_config import semanticdb, llm
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger
from neo4j_onto2ai_toolset.onto2schema.schema_types import DataModel, Node, Relationship, Property

mcp = FastMCP("Onto2AI")

@mcp.tool()
async def get_materialized_schema(class_names: Union[str, List[str]]) -> Dict[str, Any]:
    """
    Retrieve the materialized schema for one or more ontology classes.
    
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
    
    logger.info(f"Fetching enhanced materialized schema for: {labels}")
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="get_materialized_schema_tool")
        
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
            "section_1_classes": list(classes_section.values()),
            "section_2_relationships": relationships_section
        }
    except Exception as e:
        logger.error(f"Error fetching enhanced materialized schema: {e}")
        return {"error": str(e)}

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
                    properties=[]
                )
            
            is_rel = (row['PropMetaType'] == 'owl__ObjectProperty')
            
            prop_obj = Property(
                name=row['RelType'],
                type=row['TargetClassLabel'],
                description=row['RelDef'],
                mandatory=(row['Requirement'] == 'Mandatory'),
                cardinality=row['Cardinality']
            )
            
            if is_rel:
                relationships.append(Relationship(
                    type=row['RelType'],
                    start_node_label=cls_name,
                    end_node_label=row['TargetClassLabel'],
                    description=row['RelDef']
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
        
        response = await llm.ainvoke(prompt)
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
        
        response = await llm.ainvoke(prompt)
        return str(response.content).strip()
    except Exception as e:
        logger.error(f"Error generating schema code: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    # By default, run using stdio for MCP integration
    mcp.run()
