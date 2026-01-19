import json
from typing import List, Union, Optional, Dict, Any
from mcp.server.fastmcp import FastMCP
from neo4j_onto2ai_toolset.onto2ai_tool_config import semanticdb, llm
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger
from neo4j_onto2ai_toolset.onto2schema.schema_types import DataModel, Node, Relationship, Property

mcp = FastMCP("Onto2AI")

@mcp.tool()
async def get_materialized_schema(class_names: Union[str, List[str]]) -> List[dict]:
    """
    Retrieve the materialized schema for one or more ontology classes.
    Returns direct and inherited properties that have been materialized as Neo4j relationships.
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
      c.rdfs__label AS RequestedClass,
      parent.rdfs__label AS DefinitionSource,
      type(r) AS Property,
      coalesce(target.rdfs__label, target.uri, "Resource") AS Target,
      r.cardinality AS Cardinality,
      r.requirement AS Requirement
    ORDER BY RequestedClass, DefinitionSource, Property
    """
    
    logger.info(f"Fetching materialized schema for classes: {labels}")
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="get_materialized_schema_tool")
        return results if results else []
    except Exception as e:
        logger.error(f"Error fetching materialized schema: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def get_ontological_schema(class_names: Union[str, List[str]]) -> List[dict]:
    """
    Retrieve the raw ontological schema (meta-model view) for one or more classes.
    Traverses OWL Restrictions, rdfs:domain/range, and the subClassOf hierarchy.
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

    WITH c, parent, property, range,
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
      parent.rdfs__label AS DefinitionSource,
      property.rdfs__label AS Property,
      coalesce(range.rdfs__label, range.uri, "Resource") AS Target,
      Cardinality,
      Requirement
    ORDER BY RequestedClass, DefinitionSource, Property
    """
    
    logger.info(f"Fetching ontological schema for classes: {labels}")
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="get_ontological_schema_tool")
        return results if results else []
    except Exception as e:
        logger.error(f"Error fetching ontological schema: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def extract_data_model(class_names: Union[str, List[str]]) -> DataModel:
    """
    Extract a structured DataModel from the ontology for one or more classes.
    Distinguishes between properties (attributes) and relationships (links to other classes).
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
      c.rdfs__label AS RequestedClass,
      type(r) AS PropName,
      coalesce(target.rdfs__label, target.uri) AS TargetName,
      labels(target) AS TargetLabels,
      r.cardinality AS Cardinality,
      r.requirement AS Requirement,
      r.property_type AS PropMetaType
    """
    
    try:
        results = semanticdb.execute_cypher(query, params={"labels": labels}, name="extract_data_model_tool")
        
        nodes_dict = {}
        relationships = []
        
        for row in results:
            cls_name = row['RequestedClass']
            if cls_name not in nodes_dict:
                nodes_dict[cls_name] = Node(label=cls_name, properties=[])
            
            is_rel = (row['PropMetaType'] == 'owl__ObjectProperty')
            
            prop_obj = Property(
                name=row['PropName'],
                type=row['TargetName'],
                mandatory=(row['Requirement'] == 'Mandatory'),
                cardinality=row['Cardinality']
            )
            
            if is_rel:
                relationships.append(Relationship(
                    type=row['PropName'],
                    start_node_label=cls_name,
                    end_node_label=row['TargetName'],
                    properties=[]
                ))
            else:
                nodes_dict[cls_name].properties.append(prop_obj)
        
        return DataModel(
            nodes=list(nodes_dict.values()),
            relationships=relationships
        )
    except Exception as e:
        logger.error(f"Error extracting data model: {e}")
        raise

@mcp.tool()
async def enhance_schema(data_model: DataModel, instructions: str) -> DataModel:
    """
    Enhance or modify a DataModel based on natural language instructions using AI.
    """
    prompt = f"""
    You are a data architect. Modify the following Neo4j DataModel based on these instructions: "{instructions}"
    
    Current DataModel (JSON):
    {data_model.model_dump_json(indent=2)}
    
    Return ONLY a valid JSON object matching the DataModel schema. 
    Ensure PascalCase for labels and SCREAMING_SNAKE_CASE for relationship types if adding new ones.
    Do not include markdown fences or any explanation.
    """
    
    try:
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
async def generate_schema_code(data_model: DataModel, target_type: str = "pydantic") -> str:
    """
    Generate code (SQL, Pydantic, Neo4j) for a given DataModel.
    target_type: 'sql', 'pydantic', 'neo4j'
    """
    prompt = f"""
    You are a code generation expert. Generate {target_type} code for the following DataModel.
    
    DataModel (JSON):
    {data_model.model_dump_json(indent=2)}
    
    Constraints:
    - If 'sql', generate Oracle-compatible DDL.
    - If 'pydantic', generate Python classes using Pydantic v2.
    - If 'neo4j', generate Cypher CREATE CONSTRAINT/INDEX statements.
    - Return ONLY the code. No explanations, no markdown fences.
    """
    
    try:
        response = await llm.ainvoke(prompt)
        return str(response.content).strip()
    except Exception as e:
        logger.error(f"Error generating schema code: {e}")
        return f"Error: {e}"

if __name__ == "__main__":
    # By default, run using stdio for MCP integration
    mcp.run()
