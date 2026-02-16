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
from neo4j_onto2ai_toolset.onto2ai_utility import get_full_schema, get_schema

mcp = FastMCP("Onto2AI")

# --- UTILITIES ---
def to_camel_case(text):
    if not text: return text
    import re
    text_str = str(text)
    
    # Check for all caps
    if text_str.isupper():
        # Just split by underscore or non-word chars
        parts = [p.lower() for p in re.split(r'[^a-zA-Z0-9]+', text_str) if p]
    else:
        # Mixed case: Transition from lowercase/number to uppercase
        s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text_str)
        # Split and lowercase
        parts = [p.lower() for p in re.split(r'[^a-zA-Z0-9]+', s) if p]
        
    if not parts: return text_str
    # Return camelCase
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

# --- MCP TOOLS ---

MATERIALIZED_SCHEMA_QUERY = """
    // Match the requested class
    MATCH (c:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels
    
    // Optional inheritance chain
    OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
    WITH c, coalesce(parent, c) AS classNode
    
    // Path 1: Relationships to owl__Class or owl__NamedIndividual targets
    MATCH (classNode)-[r]->(target)
    WHERE (target:owl__Class OR target:owl__NamedIndividual)
      AND (r.materialized = true OR r.materialized IS NULL) // Relaxed for stagingdb
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
      coalesce(r.property_type, "owl__ObjectProperty") AS PropMetaType, // Default to ObjectProperty
      coalesce(target.rdfs__label, target.uri, "Resource") AS TargetClassLabel,
      target.uri AS TargetClassURI,
      target.skos__definition AS TargetClassDef
    
    UNION
    
    // Path 2: Relationships to rdfs__Datatype targets
    MATCH (c:owl__Class)
    WHERE c.rdfs__label IN $labels OR c.uri IN $labels
    
    OPTIONAL MATCH (c)-[:rdfs__subClassOf*0..]->(parent:owl__Class)
    WITH c, coalesce(parent, c) AS classNode
    
    MATCH (classNode)-[r]->(target:rdfs__Datatype)
    WHERE (r.materialized = true OR r.materialized IS NULL) // Relaxed for stagingdb
    RETURN DISTINCT
      c.rdfs__label AS SourceClassLabel,
      c.uri AS SourceClassURI,
      c.skos__definition AS SourceClassDef,
      type(r) AS RelType,
      r.uri AS RelURI,
      r.skos__definition AS RelDef,
      coalesce(r.cardinality, "0..1") AS Cardinality,
      r.requirement AS Requirement,
      coalesce(r.property_type, "owl__DatatypeProperty") AS PropMetaType, // Default to DatatypeProperty
      coalesce(target.rdfs__label, target.uri, "Resource") AS TargetClassLabel,
      target.uri AS TargetClassURI,
      target.skos__definition AS TargetClassDef
    
    ORDER BY SourceClassLabel, RelType
"""

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
    - **VISUALIZATION RULE**: When generating UML Class diagrams from this result:
        - Render relationships to `rdfs__Datatype` nodes or `owl__Class` enumeration nodes as **PROPERTIES** inside class boxes.
        - Render relationships to other core classes as **ARROWS/ASSOCIATIONS**.
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
    
    logger.info(f"Fetching enhanced materialized schema for: {labels} from database: {database or 'default'}")
    try:
        results = db.execute_cypher(MATERIALIZED_SCHEMA_QUERY, params={"labels": labels}, name="get_materialized_schema_tool")
        
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

@mcp.tool()
async def extract_data_model(
    class_names: Optional[Union[str, List[str]]] = None,
    database: Optional[str] = None
) -> DataModel:
    """
    Extract a structured DataModel (JSON) from the ontology.
    
    Args:
        class_names: One or more class labels. If None, extracts ALL classes from the database.
        database: Optional database name (e.g., 'stagingdb'). Defaults to 'semanticdb'.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db, semanticdb
    
    # Select database
    db = get_staging_db(database) if database else semanticdb
    
    # Logic: If class_names is None, fetch ALL class labels
    if not class_names:
        logger.info(f"No class_names provided. Fetching ALL classes from database: {database or 'semanticdb'}")
        query_all = "MATCH (n:owl__Class) RETURN n.rdfs__label as label"
        try:
            all_classes = db.execute_cypher(query_all, name="fetch_all_classes")
            class_names = [row['label'] for row in all_classes if row.get('label')]
            logger.info(f"Found {len(class_names)} classes to extract.")
        except Exception as e:
            logger.error(f"Error fetching all classes: {e}")
            raise
    
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    
    try:
        results = db.execute_cypher(MATERIALIZED_SCHEMA_QUERY, params={"labels": labels}, name="internal_extract_data_model")
        
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
            metadata={"source_classes": labels, "engine": "Onto2AI-Materialized", "database": database or "semanticdb"}
        )
    except Exception as e:
        logger.error(f"Error in extract_data_model: {e}")
        raise
    finally:
        if database:
            db.close()

@mcp.tool()
async def enhance_schema(
    class_names: Optional[Union[str, List[str]]] = None, 
    instructions: str = "",
    database: Optional[str] = None
) -> DataModel:
    """
    Extract a model from ontology and enhance it using AI instructions.
    Returns the updated DataModel (JSON).
    """
    try:
        data_model = await extract_data_model(class_names, database=database)
        
        prompt = f"""
        You are a data architect. Modify the following Neo4j DataModel based on these instructions: "{instructions}"
        
        Current DataModel (JSON):
        {data_model.model_dump_json(indent=2)}
        
        Return ONLY a JSON object. NO EXPLANATIONS.
        
        Example Structure:
        {{
          "nodes": [
            {{
              "label": "mailing address",
              "type": "owl__Class",
              "uri": "https://model.onto2ai.com/schema/mailingAddress",
              "properties": [{{
                "name": "cityName",
                "type": "string",
                "uri": "https://model.onto2ai.com/schema/cityName",
                "mandatory": false,
                "cardinality": "0..1"
              }}]
            }},
            {{
              "label": "postal code",
              "type": "rdfs__Datatype",
              "uri": "https://model.onto2ai.com/schema/postalCode",
              "properties": []
            }}
          ],
          "relationships": [
            {{
              "type": "isPlayedBy",
              "start_node_label": "mailing address",
              "end_node_label": "party",
              "uri": "https://model.onto2ai.com/schema/isPlayedBy"
            }}
          ]
        }}

        MANDATORY RULES (ZERO TOLERANCE):
        1. Node Type: Every node MUST have a 'type' field set to either 'owl__Class' or 'rdfs__Datatype'.
        2. Node Labels: MUST be lowercase with spaces (e.g. 'account holder'). FORBIDDEN: 'AccountHolder', 'ACCOUNT_HOLDER'.
        3. Relationship Types: MUST be camelCase only (e.g. 'isPlayedBy'). FORBIDDEN: 'IS_PLAYED_BY', 'has_amount'.
        4. Property Names: MUST be camelCase only (e.g. 'cityName').
        5. URIs: MUST start with 'https://model.onto2ai.com/schema/' followed by the name in camelCase.
           Note: Even if the label has spaces, the URI suffix MUST be camelCase.
           Example: label 'mailing address' -> URI 'https://model.onto2ai.com/schema/mailingAddress'
           FORBIDDEN: 'fibo...', 'cmns...', 'omg...', etc. REPLACE ALL OF THEM.
        6. RELATIONSHIP-BASED ATTRIBUTES: Instead of primitive properties on class nodes, domain-specific attributes (e.g., money, rates, dates, codes, or statuses) MUST be modeled as RELATIONSHIPS to 'rdfs__Datatype' nodes or 'owl__Class' enumeration nodes.
           Example: Instead of setting 'taxRate' as a property on 'tax authority', create a relationship 'hasTaxRate' from 'tax authority' to an 'rdfs__Datatype' node with label 'xsd:decimal'.

        Constraint: EVERY property in the 'properties' list MUST be an OBJECT (not a string).
        
        Do not include markdown fences.
        """
        
        response = await get_llm().ainvoke(prompt)
        content = str(response.content).strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
            
        updated_model_dict = json.loads(content)
        
        # Robustness: Fix common AI mistakes
        def fix_model(obj_list, is_node=True):
            for item in obj_list:
                # 1. Fix Labels (lowercase with space if node)
                if is_node and 'label' in item:
                    item['label'] = str(item['label']).lower().strip()
                
                # 2. Fix Relationship types (camelCase)
                if not is_node and 'type' in item:
                    item['type'] = to_camel_case(str(item['type']))

                # 3. Fix properties (objects instead of strings)
                if 'properties' in item and isinstance(item['properties'], list):
                    item['properties'] = [
                        {
                            "name": to_camel_case(p), 
                            "type": "STRING", 
                            "uri": f"https://model.onto2ai.com/schema/{to_camel_case(p)}",
                            "mandatory": False,
                            "cardinality": "0..1"
                        } 
                        if isinstance(p, str) else p 
                        for p in item['properties']
                    ]
                    # Also fix existing property names and URIs
                    for p in item['properties']:
                        if isinstance(p, dict):
                            if 'name' in p:
                                p['name'] = to_camel_case(p['name'])
                            if 'uri' not in p or not p['uri'] or 'model.onto2ai.com' not in p['uri']:
                                p['uri'] = f"https://model.onto2ai.com/schema/{p['name']}"

                # 4. Fix URIs (enforce mandatory prefix and camelCase name)
                name = item.get('label') if is_node else item.get('type')
                if name:
                    item['uri'] = f"https://model.onto2ai.com/schema/{to_camel_case(str(name))}"
                
                # 5. Fix Node Types
                if is_node and ('type' not in item or not item['type']):
                    item['type'] = "owl__Class"

        if 'nodes' in updated_model_dict:
            fix_model(updated_model_dict['nodes'], is_node=True)
        if 'relationships' in updated_model_dict:
            fix_model(updated_model_dict['relationships'], is_node=False)
            
        return DataModel(**updated_model_dict)
    except Exception as e:
        logger.error(f"Error enhancing schema: {e}")
        raise

@mcp.tool()
async def generate_schema_code(
    class_names: Optional[Union[str, List[str]]] = None, 
    target_type: str = "pydantic", 
    instructions: Optional[str] = None,
    database: Optional[str] = None
) -> str:
    """
    Generate production-ready code (SQL, Pydantic, Neo4j, GraphSchema) for one or more ontology classes.
    Optional 'instructions' allows on-the-fly AI enhancement of the base ontology schema.
    
    target_type options:
    - 'pydantic': Python Pydantic v2 models.
    - 'sql': Oracle-compatible DDL.
    - 'neo4j': Cypher CREATE CONSTRAINT/INDEX statements.
    - 'graph_schema': Textual description of the graph schema (Labels, Relationships, Metadata).
    """
    if target_type == "graph_schema":
        from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db, semanticdb
        db = get_staging_db(database) if database else semanticdb
        try:
            if not class_names:
                return get_full_schema(db)
            
            if isinstance(class_names, str):
                class_names = [class_names]
            
            # If specific classes requested, we construct the schema description iteratively
            parts = []
            for cls in class_names:
                parts.append(get_schema(start_node=cls, db=db))
            
            return "\n\n".join(parts)
        except Exception as e:
            logger.error(f"Error generating graph schema: {e}")
            return f"Error: {e}"
        finally:
            if database:
                db.close()

    try:
        # 1. Extract base model
        if instructions:
            data_model = await enhance_schema(class_names, instructions, database=database)
        else:
            data_model = await extract_data_model(class_names, database=database)
            
        # 2. Generate code
        prompt = f"""
        You are a code generation expert. Generate {target_type} code for the following DataModel.
        
        DataModel (JSON):
        {data_model.model_dump_json(indent=2)}
        
        Constraints:
        - If 'pydantic', generate Python classes using Pydantic v2.
        - If 'sql', generate Oracle-compatible DDL.
        - If 'neo4j', generate Cypher CREATE CONSTRAINT/INDEX statements.
        
        Pydantic Rendering Guidelines (CRITICAL):
        - RELATIONSHIP-BASED ATTRIBUTES: Relationships pointing to 'rdfs__Datatype' nodes or 'owl__Class' enumeration nodes MUST be rendered as simple class fields (properties).
        - DOCSTRINGS: Every class MUST include a triple-quoted Python docstring at the top of the class body using the 'definition' from the DataModel.
        - FIELD DESCRIPTIONS: Every field MUST use Pydantic's 'Field(description="...")' to include its ontological definition.
        
        SQL/Neo4j Documentation Style:
        - For SQL: Table definitions MUST be rendered using 'COMMENT ON TABLE [name] IS ...' statements.
        - For Neo4j/Cypher: 
            - DO NOT create constraints or indexes for metadata fields like 'uri', 'rdfs__label', or 'skos__definition'.
            - Inclusion Principle: Include 'uri', 'rdfs__label', and 'skos__definition' as // COMMENTS only above each class definition.
            - Structural Principles: Generate 'IS UNIQUE' constraints ONLY for functional identifiers if specified (otherwise ignore).
            - Existence Principles: Generate 'IS NOT NULL' constraints ONLY for properties where 'mandatory' is true.
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
async def generate_schema_constraints(
    database: Optional[str] = None
) -> str:
    """
    Generate Neo4j Cypher constraints and indexes for a database based on its metadata.
    
    This tool produces a deterministic Cypher script that includes:
    1. Existence constraints (IS NOT NULL) for all mandatory data properties.
    2. Comments providing URI, Label, and Definition metadata for AI semantic discovery.
    3. NO constraints or indexes for metadata fields like URI or Label (follows production separation principle).
    
    Args:
        database: Optional database name (e.g., 'stagingdb'). Defaults to 'semanticdb'.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db, semanticdb
    
    db = get_staging_db(database) if database else semanticdb
    try:
        query = """
        MATCH (n:owl__Class)
        OPTIONAL MATCH (n)-[r]->(m:rdfs__Datatype)
        RETURN n.rdfs__label as class_label, 
               n.skos__definition as class_definition, 
               n.uri as class_uri,
               type(r) as prop_name,
               r.cardinality as prop_cardinality
        ORDER BY class_label
        """
        results = db.execute_cypher(query, name="generate_schema_constraints")
        
        # Group by class
        schema_data = {}
        for row in results:
            cls_label = row['class_label']
            if cls_label not in schema_data:
                schema_data[cls_label] = {
                    "definition": row['class_definition'],
                    "uri": row['class_uri'],
                    "properties": []
                }
            if row['prop_name']:
                schema_data[cls_label]["properties"].append({
                    "name": row['prop_name'],
                    "cardinality": row['prop_cardinality']
                })

        cypher_output = [
            "// ===========================================================",
            f"// NEO4J SCHEMA CONSTRAINTS (Source: {database or 'semanticdb'})",
            "// Generated to enforce structural integrity while keeping metadata as comments.",
            "// ===========================================================\n"
        ]
        
        for cls_label, data in schema_data.items():
            actual_label = cls_label.replace(" ", "").replace("-", "")
            
            cypher_output.append(f"// Class: {cls_label}")
            if data['definition']:
                cypher_output.append(f"// Definition: {data['definition']}")
            if data['uri']:
                cypher_output.append(f"// URI: {data['uri']}")
            
            # Note: metadata fields like labels and URIs do not get physical constraints
            
            # Property constraints (Existence for mandatory fields)
            for prop in data['properties']:
                card = prop['cardinality'] or ""
                if card.startswith("1"):
                    constraint_name = f"{actual_label}_{prop['name']}_Required"
                    cypher_output.append(f"// Mandatory property: {prop['name']} (cardinality: {card})")
                    cypher_output.append(f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS FOR (n:{actual_label}) REQUIRE n.{prop['name']} IS NOT NULL;")
            
            cypher_output.append("")
            
        return "\n".join(cypher_output)
        
    except Exception as e:
        logger.error(f"Error generating schema constraints: {e}")
        return f"Error: {e}"
    finally:
        if database:
            db.close()

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
            data_model = await extract_data_model(class_names)
            
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
    staging_db_name: Optional[str] = None,
    flatten_inheritance: bool = False
) -> Dict[str, Any]:
    """
    Extract materialized schema for one or more ontology classes and copy 
    all involved classes and relationships to a staging Neo4j database.
    
    Args:
        class_names: One or more class labels to extract (e.g., "person" or ["person", "account"])
        staging_db_name: Target database name. Defaults to NEO4J_STAGING_DB_NAME env var.
        flatten_inheritance: If True, copy inherited relationships from parent classes 
                           directly to the requested classes. This makes each class 
                           self-contained without needing to traverse parent hierarchy.
    
    Returns:
        Summary of copied classes and relationships with counts.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
    
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    
    # Step 1: Extract materialized schema AND subclass hierarchy from source database
    # This query finds all classes in scope and extracts their full hierarchy and properties.
    # Key fix: We need to capture relationships for the ORIGINAL requested classes too,
    # not just from ancestors. We collect all classes (requested + ancestors + ranges)
    # and get ALL their materialized relationships.
    query = """
    // Start with requested classes
    MATCH (start:owl__Class)
    WHERE start.rdfs__label IN $labels OR start.uri IN $labels
    
    // Find the full ancestor chain for each starting class
    OPTIONAL MATCH (start)-[:rdfs__subClassOf*0..]->(ancestor:owl__Class)
    
    // Collect all classes in scope (start classes and their ancestors)
    WITH collect(DISTINCT start) + collect(DISTINCT ancestor) AS classScope
    
    // Now find all materialized relationships from classes in scope
    UNWIND classScope AS scopeClass
    OPTIONAL MATCH (scopeClass)-[r]->(target)
    WHERE r.materialized = true OR type(r) = "rdfs__subClassOf"
    
    // Also find any additional target classes that need to be included
    WITH scopeClass, r, target
    WHERE target IS NOT NULL
    
    // For class targets, also include THEIR ancestors and relationships
    OPTIONAL MATCH (target)-[:rdfs__subClassOf*0..]->(targetAncestor:owl__Class)
    WHERE target:owl__Class
    
    // Collect all relationships and targets
    WITH 
      scopeClass,
      r, 
      target,
      collect(DISTINCT targetAncestor) AS targetAncestors
    
    // Return the relationships
    RETURN DISTINCT
      scopeClass.rdfs__label AS SourceClassLabel,
      scopeClass.uri AS SourceClassURI,
      scopeClass.skos__definition AS SourceClassDef,
      type(r) AS RelType,
      r.uri AS RelURI,
      r.skos__definition AS RelDef,
      r.cardinality AS Cardinality,
      r.requirement AS Requirement,
      r.property_type AS PropertyType,
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
                "message": f"No materialized schema or hierarchy found for classes: {labels}",
                "classes_copied": 0,
                "relationships_copied": 0
            }
        
        # Helper to identify "blank" or anonymous nodes
        def is_blank_class(uri, label):
            if not uri: return True
            # Matches NSMNTX generated IDs like Na28bbacb13304b099a6294f8e65c278a
            if label == uri: return True
            if uri.startswith('_:'): return True
            # Often blank nodes start with 'N' followed by hex
            import re
            if re.match(r'^N[0-9a-f]{10,}$', uri): return True
            return False

        # Step 2: Collect unique classes, datatypes, individuals and relationships
        classes = {}
        datatypes = {}
        named_individuals = {}
        relationships = []
        
        for row in results:
            src_uri = row['SourceClassURI']
            src_label = row['SourceClassLabel']
            tgt_uri = row['TargetClassURI']
            tgt_label = row['TargetClassLabel']
            tgt_labels = row.get('TargetLabels', []) or []
            rel_type = row['RelType']

            # SKIP if either source or target is a blank class
            if is_blank_class(src_uri, src_label): continue
            
            # For class-to-class relationships, check the target too
            is_class_target = not ('rdfs__Datatype' in tgt_labels or 'owl__NamedIndividual' in tgt_labels or 'XMLSchema#' in str(tgt_uri))
            if is_class_target and is_blank_class(tgt_uri, tgt_label):
                continue

            # Collect source class
            if src_uri not in classes:
                classes[src_uri] = {
                    "uri": src_uri,
                    "label": str(src_label).lower().strip(),
                    "definition": row['SourceClassDef']
                }
            
            # Collect target based on its type
            if tgt_uri:
                is_xsd_datatype = 'XMLSchema#' in tgt_uri or 'XMLSchema/' in tgt_uri
                
                if 'rdfs__Datatype' in tgt_labels or is_xsd_datatype:
                    if tgt_uri not in datatypes:
                        if is_xsd_datatype:
                            short_label = tgt_uri.split('#')[-1] if '#' in tgt_uri else tgt_uri.split('/')[-1]
                            label = f"xsd:{short_label}"
                        else:
                            label = str(tgt_label).lower().strip()
                        datatypes[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": label,
                            "definition": row['TargetClassDef']
                        }
                elif 'owl__NamedIndividual' in tgt_labels:
                    if tgt_uri not in named_individuals:
                        named_individuals[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": str(tgt_label).lower().strip(),
                            "definition": row['TargetClassDef']
                        }
                else:
                    # Named Class
                    if tgt_uri not in classes:
                        classes[tgt_uri] = {
                            "uri": tgt_uri,
                            "label": str(tgt_label).lower().strip(),
                            "definition": row['TargetClassDef']
                        }
            
            # Normalize relationship type (except for rdfs__subClassOf)
            normalized_rel_type = rel_type
            if rel_type != "rdfs__subClassOf":
                normalized_rel_type = to_camel_case(rel_type)

            # Collect relationship
            relationships.append({
                "source_uri": src_uri,
                "target_uri": tgt_uri,
                "rel_type": normalized_rel_type,
                "rel_uri": row['RelURI'],
                "definition": row['RelDef'],
                "cardinality": row['Cardinality'],
                "requirement": row['Requirement'],
                "property_type": row.get('PropertyType'),
                "target_labels": tgt_labels
            })
        
        # Step 3: Connect to staging database
        staging_db = get_staging_db(staging_db_name)
        
        try:
            # Step 4: Insert nodes
            class_insert_query = """
            MERGE (c:owl__Class {uri: $uri})
            SET c.rdfs__label = $label,
                c.skos__definition = $definition
            """
            for cls in classes.values():
                staging_db.execute_cypher(class_insert_query, params=cls, name="staging_class_insert")
            
            datatype_insert_query = """
            MERGE (d:rdfs__Datatype {uri: $uri})
            SET d.rdfs__label = $label,
                d.skos__definition = $definition
            """
            for dt in datatypes.values():
                staging_db.execute_cypher(datatype_insert_query, params=dt, name="staging_datatype_insert")
            
            individual_insert_query = """
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i.skos__definition = $definition
            """
            for ind in named_individuals.values():
                staging_db.execute_cypher(individual_insert_query, params=ind, name="staging_individual_insert")

            # Step 5: Insert relationships
            rel_types_created = set()
            for rel in relationships:
                rel_type = rel["rel_type"]
                if not rel_type: continue
                
                tgt_labels = rel.get("target_labels", []) or []
                tgt_uri = rel.get("target_uri", "")
                is_xsd_datatype = 'XMLSchema#' in tgt_uri or 'XMLSchema/' in tgt_uri
                
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
                    r.property_type = $property_type
                """
                # Only set materialized if it's NOT a subClassOf link (hierarchy is intrinsic)
                if rel_type != "rdfs__subClassOf":
                    rel_insert_query += "\nSET r.materialized = true"

                staging_db.execute_cypher(rel_insert_query, params=rel, name="staging_rel_insert")
                rel_types_created.add(rel_type)
            
            logger.info(f"Inserted {len(relationships)} relationships into staging database")
            
            # Step 6: Flatten inheritance if requested
            inherited_relationships_copied = 0
            if flatten_inheritance:
                logger.info(f"Flattening inheritance for requested classes: {labels}")
                
                # For each originally requested class, copy relationships from its ancestors
                flatten_query = """
                // Find the requested class (handle label as string or array)
                MATCH (requested:owl__Class)
                WHERE any(lbl IN apoc.coll.flatten([requested.rdfs__label]) WHERE toLower(lbl) = toLower($label))
                
                // Find all its ancestors
                MATCH (requested)-[:rdfs__subClassOf*1..]->(parent:owl__Class)
                
                // Find all materialized relationships from parents
                MATCH (parent)-[r]->(target)
                WHERE r.materialized = true
                
                // Extract parent label as string (handle array case)
                WITH requested, parent, r, target, type(r) AS relType,
                     CASE WHEN parent.rdfs__label IS :: STRING THEN parent.rdfs__label ELSE head(parent.rdfs__label) END AS parentLabel
                
                // Create a copy on the requested class with the same type
                WITH requested, parent, r, target, relType, parentLabel,
                     apoc.map.merge(properties(r), {inherited_from: parentLabel}) AS props
                CALL apoc.create.relationship(requested, relType, props, target) YIELD rel
                
                RETURN count(rel) AS copied
                """
                
                for label in labels:
                    result = staging_db.execute_cypher(
                        flatten_query, 
                        params={"label": label}, 
                        name="flatten_inheritance"
                    )
                    if result and len(result) > 0:
                        copied = result[0].get("copied", 0)
                        inherited_relationships_copied += copied
                        logger.info(f"Copied {copied} inherited relationships to '{label}'")
            
        finally:
            staging_db.close()
        
        # Return summary
        result = {
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
        
        if flatten_inheritance:
            result["inherited_relationships_copied"] = inherited_relationships_copied
        
        return result
        
    except Exception as e:
        logger.error(f"Error staging materialized schema: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
async def consolidate_inheritance(
    class_names: Union[str, List[str]],
    staging_db_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consolidate inherited relationships by copying them directly to specified classes.
    This makes each class self-contained without needing to traverse parent hierarchy.
    
    Use this tool when you have already staged classes and want to flatten their 
    inheritance after the fact, rather than re-staging with flatten_inheritance=True.
    
    Args:
        class_names: One or more class labels to consolidate (e.g., "cardholder")
        staging_db_name: Target database name. Defaults to NEO4J_STAGING_DB_NAME env var.
    
    Returns:
        Summary of inherited relationships copied to each class.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
    
    if isinstance(class_names, str):
        class_names = [class_names]
    
    labels = [label.strip() for label in class_names]
    staging_db = get_staging_db(staging_db_name)
    
    try:
        results_by_class = {}
        total_copied = 0
        
        # Query to copy inherited relationships
        flatten_query = """
        // Find the requested class (handle label as string or array)
        MATCH (requested:owl__Class)
        WHERE any(lbl IN CASE WHEN requested.rdfs__label IS :: LIST<ANY> THEN requested.rdfs__label ELSE [requested.rdfs__label] END WHERE toLower(lbl) = toLower($label))
        
        // Find all its ancestors
        MATCH (requested)-[:rdfs__subClassOf*1..]->(parent:owl__Class)
        
        // Find all materialized relationships from parents
        MATCH (parent)-[r]->(target)
        WHERE r.materialized = true
        
        // Extract parent label as string (handle array case)
        WITH requested, parent, r, target, type(r) AS relType,
             CASE WHEN parent.rdfs__label IS :: STRING THEN parent.rdfs__label ELSE head(parent.rdfs__label) END AS parentLabel
        
        // Create a copy on the requested class with the same type
        WITH requested, parent, r, target, relType, parentLabel,
             apoc.map.merge(properties(r), {inherited_from: parentLabel}) AS props
        CALL apoc.create.relationship(requested, relType, props, target) YIELD rel
        
        RETURN parentLabel AS parentClass, type(rel) AS relType, count(rel) AS count
        """
        
        for label in labels:
            result = staging_db.execute_cypher(
                flatten_query, 
                params={"label": label}, 
                name="consolidate_inheritance"
            )
            
            if result:
                class_details = []
                class_total = 0
                for row in result:
                    copied = row.get("count", 0)
                    class_total += copied
                    class_details.append({
                        "parent_class": row.get("parentClass"),
                        "relationship_type": row.get("relType"),
                        "count": copied
                    })
                
                results_by_class[label] = {
                    "relationships_copied": class_total,
                    "details": class_details
                }
                total_copied += class_total
                logger.info(f"Copied {class_total} inherited relationships to '{label}'")
            else:
                results_by_class[label] = {
                    "relationships_copied": 0,
                    "message": "No inherited relationships found or class not found"
                }
        
        return {
            "status": "success",
            "database": staging_db_name or "stagingdb",
            "total_relationships_copied": total_copied,
            "classes": results_by_class
        }
        
    except Exception as e:
        logger.error(f"Error consolidating inheritance: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        staging_db.close()


@mcp.tool()
async def apply_data_model(
    data_model: Dict[str, Any],
    staging_db_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply a structured DataModel (JSON) to the staging database.
    Creates classes, datatypes, and relationships described in the model.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
    
    db = get_staging_db(staging_db_name)
    logger.info(f"Applying data model to staging database: {staging_db_name or 'default'}")
    
    try:
        nodes = data_model.get("nodes", [])
        relationships = data_model.get("relationships", [])
        
        created_nodes = 0
        created_rels = 0
        
        # 1. Create Nodes (Classes and Datatypes)
        for node in nodes:
            label = node.get("label")
            # Handle potential variation in label key (sometimes "rdfs__label" in raw outputs)
            if not label: 
                label = node.get("rdfs__label")
            
            uri = node.get("uri")
            definition = node.get("description") or node.get("definition") or node.get("skos__definition")
            node_type = node.get("type", "owl__Class")
            
            # Sanitize inputs
            if not uri or not label:
                logger.warning(f"Skipping node without URI or label: {node}")
                continue
                
            query = f"""
            MERGE (n:{node_type} {{uri: $uri}})
            SET n.rdfs__label = $label,
                n.skos__definition = $definition
            """
            
            db.execute_cypher(query, params={
                "uri": uri,
                "label": label,
                "definition": definition
            }, name="apply_model_node")
            created_nodes += 1
            
            # Handle inline properties (turn into relationships to datatypes)
            for prop in node.get("properties", []):
                prop_name = prop.get("name")
                prop_uri = prop.get("uri")
                prop_type = prop.get("type", "string")  # Target label (e.g. string, date)
                cardinality = prop.get("cardinality", "0..1")
                prop_def = prop.get("description")
                
                if not prop_name or not prop_uri:
                    continue
                    
                # Creating the datatype node if it doesn't exist
                dt_query = """
                MERGE (dt:rdfs__Datatype {uri: $prop_uri})
                SET dt.rdfs__label = $prop_type
                """
                db.execute_cypher(dt_query, params={"prop_uri": prop_uri, "prop_type": prop_type}, name="apply_model_prop_dt")
                
                # Linking class to datatype
                link_query = f"""
                MATCH (c:{node_type} {{uri: $class_uri}})
                MATCH (dt:rdfs__Datatype {{uri: $prop_uri}})
                MERGE (c)-[r:{to_camel_case(prop_name)}]->(dt)
                SET r.uri = $prop_uri,
                    r.skos__definition = $prop_def,
                    r.cardinality = $cardinality,
                    r.materialized = true,
                    r.property_type = 'owl__DatatypeProperty'
                """
                db.execute_cypher(link_query, params={
                    "class_uri": uri,
                    "prop_uri": prop_uri,
                    "prop_def": prop_def,
                    "cardinality": cardinality
                }, name="apply_model_prop_link")
                created_rels += 1

        # 2. Create Relationships (Object Properties)
        for rel in relationships:
            src_label = rel.get("start_node_label")
            tgt_label = rel.get("end_node_label")
            rel_type = rel.get("type")
            rel_uri = rel.get("uri")
            rel_def = rel.get("description")
            cardinality = rel.get("cardinality", "0..*")
            
            if not src_label or not tgt_label or not rel_type:
                continue
                
            # We match by Label since we might not have the URI handy in the relationship object
            # Ideally we should match by URI if available, but Label is often safer for cross-referencing in JSON
            
            query = f"""
            MATCH (source) WHERE source.rdfs__label = $src_label AND (source:owl__Class OR source:owl__NamedIndividual)
            MATCH (target) WHERE target.rdfs__label = $tgt_label AND (target:owl__Class OR target:owl__NamedIndividual)
            
            MERGE (source)-[r:{to_camel_case(rel_type)}]->(target)
            SET r.uri = $rel_uri,
                r.skos__definition = $rel_def,
                r.cardinality = $cardinality,
                r.materialized = true,
                r.property_type = 'owl__ObjectProperty'
            """
            
            db.execute_cypher(query, params={
                "src_label": src_label,
                "tgt_label": tgt_label,
                "rel_uri": rel_uri,
                "rel_def": rel_def,
                "cardinality": cardinality
            }, name="apply_model_rel")
            created_rels += 1
            
        return {
            "status": "success",
            "database": staging_db_name or "stagingdb",
            "nodes_created_or_updated": created_nodes,
            "relationships_created_or_updated": created_rels
        }
        
    except Exception as e:
        logger.error(f"Error applying data model: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@mcp.tool()
async def consolidate_staging_db(
    transformations: List[Dict[str, str]],
    staging_db_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consolidate classes in the staging database by converting them into datatypes.
    
    Args:
        transformations: List of dicts with keys:
            - 'old_label': The current label of the class (e.g., 'card verification code or value')
            - 'new_label': The simplified label (e.g., 'cvc')
            - 'xsd_type': The technical XSD type (e.g., 'xsd:string' or 'xsd:date')
        staging_db_name: Optional target database name. Defaults to the staging database.
    
    Returns:
        Summary of transformations applied.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
    
    db = get_staging_db(staging_db_name)
    logger.info(f"Consolidating staging database: {staging_db_name or 'default'} with {len(transformations)} transformations")
    
    try:
        # We perform everything in a single session/transaction conceptually if possible, 
        # but here we execute sequentially via the db wrapper.
        results = []
        for t in transformations:
            old_label = t.get('old_label')
            new_label = t.get('new_label')
            xsd_type = t.get('xsd_type', 'xsd:string')
            
            if not old_label or not new_label:
                results.append({"old_label": old_label, "status": "error", "message": "Missing old_label or new_label"})
                continue
                
            # Pre-step: Delete NamedIndividuals linked via rdf__type before consolidation
            cleanup_individuals_query = """
            MATCH (ind:owl__NamedIndividual)-[:rdf__type]->(n:owl__Class {rdfs__label: $old_label})
            DETACH DELETE ind
            RETURN count(ind) as deleted_count
            """
            cleanup_res = db.execute_cypher(cleanup_individuals_query, params={
                "old_label": old_label
            }, name="consolidate_cleanup_individuals")
            deleted_individuals = cleanup_res[0].get("deleted_count", 0) if cleanup_res else 0
            if deleted_individuals > 0:
                logger.info(f"Deleted {deleted_individuals} NamedIndividual(s) linked to '{old_label}'")

            query = """
            MATCH (n)
            WHERE (n:owl__Class OR n:rdfs__Datatype) AND n.rdfs__label = $old_label
            
            // 1. Tag incoming relationships as datatype properties for visualization
            WITH n
            OPTIONAL MATCH ()-[r_in]->(n)
            SET r_in.property_type = 'owl__DatatypeProperty'

            // 2. Remove outgoing (reversed) relationships
            WITH DISTINCT n
            OPTIONAL MATCH (n)-[r_out]->()
            DELETE r_out
            
            // 3. Transform the class node into a datatype node
            WITH DISTINCT n
            REMOVE n:owl__Class
            SET n:rdfs__Datatype,
                n.rdfs__label = $new_label,
                n.xsd_type = $xsd_type
                
            RETURN n.uri as uri, count(n) as count
            """
            
            res = db.execute_cypher(query, params={
                "old_label": old_label,
                "new_label": new_label,
                "xsd_type": xsd_type
            }, name="consolidate_transform")
            
            if res:
                result_entry = {
                    "old_label": old_label,
                    "new_label": new_label,
                    "uri": res[0].get("uri"),
                    "status": "success",
                    "nodes_affected": res[0].get("count", 1)
                }
                if deleted_individuals > 0:
                    result_entry["individuals_deleted"] = deleted_individuals
                results.append(result_entry)
            else:
                results.append({"old_label": old_label, "status": "not_found"})

        # --- CLEANUP STEP: Remove duplicates ---
        logger.info("Performing final de-duplication and cleanup in staging database")
        
        cleanup_queries = [
            # 1. Merge nodes with SAME URI (Absolute duplicates)
            """
            MATCH (n)
            WHERE n.uri IS NOT NULL
            WITH n.uri AS uri, collect(n) AS nodes
            WHERE size(nodes) > 1
            CALL apoc.refactor.mergeNodes(nodes, {properties: 'combine', mergeRels: true}) YIELD node
            RETURN count(node)
            """,
            # 2. Merge DATATYPES with SAME LABEL (Application-level consolidation)
            """
            MATCH (n:rdfs__Datatype)
            WHERE n.rdfs__label IS NOT NULL
            WITH n.rdfs__label AS label, collect(n) AS nodes
            WHERE size(nodes) > 1
            CALL apoc.refactor.mergeNodes(nodes, {properties: 'combine', mergeRels: true}) YIELD node
            RETURN count(node)
            """,
            # 3. Merge identical relationships (Same type, source, target)
            """
            MATCH (a)-[r]->(b)
            WITH a, b, type(r) AS t, collect(r) AS rels
            WHERE size(rels) > 1
            CALL apoc.refactor.mergeRelationships(rels, {properties: 'combine'}) YIELD rel
            RETURN count(rel)
            """
        ]
        
        for cq in cleanup_queries:
            try:
                db.execute_cypher(cq, name="consolidate_cleanup")
            except Exception as cleanup_err:
                logger.warning(f"Cleanup query failed (possibly missing APOC or permissions): {cleanup_err}")
                
        return {
            "status": "success",
            "database": staging_db_name or "stagingdb",
            "transformations": results
        }
    except Exception as e:
        logger.error(f"Error during consolidation: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@mcp.tool()
async def merge_semantic_individuals(
    label_pairs: List[Dict[str, str]],
    staging_db_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Merge local placeholder individuals with official FIBO nodes based on semantic equivalence.
    
    Args:
        label_pairs: List of dicts with:
            - 'fibo_uri': The official standard URI to keep.
            - 'local_uri': The local placeholder URI to be merged/deleted.
        staging_db_name: Optional target database name.
    
    Returns:
        Summary of merged pairs.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
    db = get_staging_db(staging_db_name)
    results = []
    
    try:
        for pair in label_pairs:
            fibo_uri = pair.get('fibo_uri')
            local_uri = pair.get('local_uri')
            
            if not fibo_uri or not local_uri:
                continue
                
            query = """
            MATCH (fibo:owl__NamedIndividual {uri: $fibo_uri})
            MATCH (local:owl__NamedIndividual {uri: $local_uri})
            CALL apoc.refactor.mergeNodes([fibo, local], {properties: 'overwrite', mergeRels: true}) YIELD node
            RETURN node.uri AS uri
            """
            
            res = db.execute_cypher(query, params={
                "fibo_uri": fibo_uri,
                "local_uri": local_uri
            }, name="merge_semantic_individual")
            
            if res:
                results.append({"fibo_uri": fibo_uri, "local_uri": local_uri, "status": "merged"})
            else:
                results.append({"fibo_uri": fibo_uri, "local_uri": local_uri, "status": "not_found"})
                
        return {
            "status": "success",
            "database": staging_db_name or "stagingdb",
            "merges": results
        }
    finally:
        db.close()

@mcp.tool()
async def get_ontology_schema_description(
    database: Optional[str] = None,
    use_heuristics: bool = True
) -> str:
    """
    Retrieve said database schema description (Nodes, Relationships, Properties) as a string.
    Useful for LLM context or schema management.
    
    Args:
        database: Optional database name (e.g., 'stagingdb'). Defaults to 'semanticdb'.
        use_heuristics: If True, filters out metadata classes (Enums/Datatypes) using instance counts and topology.
    """
    from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db, semanticdb
    
    db = get_staging_db(database) if database else semanticdb
    try:
        # get_full_schema now supports heuristics
        schema_text = get_full_schema(db, use_heuristics=use_heuristics)
        return schema_text
    except Exception as e:
        logger.error(f"Error getting ontology schema: {e}")
        return f"Error: {e}"
    finally:
        if database:
            db.close()

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
        
        mcp.settings.port = port
        mcp.settings.host = "localhost"
        
        print(f"Starting Onto2AI MCP Server on HTTP port {port}...", file=sys.stderr)
        mcp.run(transport="sse")
    else:
        # By default, run using stdio for MCP integration
        mcp.run()

