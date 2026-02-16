import json
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin
from pydantic import BaseModel

class PydanticNeo4jBridge:
    """Utility to bridge Pydantic models with Neo4j graph data."""

    @staticmethod
    def to_neo4j_params(model: BaseModel) -> Dict[str, Any]:
        """
        Convert as Pydantic model to a flat dictionary of properties and a list of relationships.
        Recursively processes nested models.
        """
        properties = {}
        relationships = []
        
        # Get data using aliases (ontological names)
        data = model.model_dump(by_alias=True)
        
        for field_name, field_value in data.items():
            if field_value is None:
                continue
                
            # Handle Enums (use their value)
            if isinstance(field_value, Enum):
                properties[field_name] = field_value.value
            # Handle Dates (use ISO string)
            elif isinstance(field_value, date):
                properties[field_name] = field_value.isoformat()
            # Handle Decimals (use float or string)
            elif isinstance(field_value, Decimal):
                properties[field_name] = float(field_value)
            # Handle nested models (Relationships)
            elif isinstance(field_value, dict):
                # We extract properties from the dict (which might contain Decimals)
                # But to avoid Decimal issues in the target SET n += $props,
                # we must ensure the dict itself is clean.
                cleaned_target = PydanticNeo4jBridge._clean_data(field_value)
                relationships.append({
                    "type": field_name,
                    "target": cleaned_target,
                    "target_label": PydanticNeo4jBridge._get_model_label(model, field_name)
                })
            # Handle lists of nested models
            elif isinstance(field_value, list):
                target_label = PydanticNeo4jBridge._get_model_label(model, field_name)
                for item in field_value:
                    if isinstance(item, dict):
                        cleaned_item = PydanticNeo4jBridge._clean_data(item)
                        relationships.append({
                            "type": field_name,
                            "target": cleaned_item,
                            "target_label": target_label
                        })
                    else:
                        # Primitive list (like box12Codes)
                        properties[field_name] = field_value
            else:
                properties[field_name] = field_value
                
        return {"properties": properties, "relationships": relationships}

    @staticmethod
    def _clean_data(data: Any) -> Any:
        """Helper to recursively clean data for Neo4j (Decimals to floats, Enums to values)."""
        if isinstance(data, dict):
            return {k: PydanticNeo4jBridge._clean_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [PydanticNeo4jBridge._clean_data(i) for i in data]
        elif isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, Enum):
            return data.value
        elif isinstance(data, date):
            return data.isoformat()
        return data

    @staticmethod
    def _get_model_label(model: BaseModel, alias: str) -> str:
        """Helper to find the target Neo4j label for a nested field."""
        # Find the field by alias
        for name, field in model.model_fields.items():
            if field.alias == alias or name == alias:
                # Get the type
                field_type = field.annotation
                origin = get_origin(field_type)
                if origin is list or origin is Union:
                    args = get_args(field_type)
                    # Find the BaseModel in args
                    for arg in args:
                        if isinstance(arg, type) and issubclass(arg, BaseModel):
                            return arg.__name__
                elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                    return field_type.__name__
        return "Resource"

    @staticmethod
    def generate_merge_query(label: str, properties: Dict[str, Any], identifier_key: str = "uri") -> str:
        """Generate a MERGE query for a node."""
        props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        return f"MERGE (n:{label} {{ {identifier_key}: ${identifier_key} }}) SET n += $props RETURN n"

    @staticmethod
    def load_model_to_neo4j(db, model: BaseModel, label: str = None):
        """Recursively loads a Pydantic model into Neo4j."""
        if label is None:
            label = model.__class__.__name__
            
        data = PydanticNeo4jBridge.to_neo4j_params(model)
        props = data["properties"]
        rels = data["relationships"]
        
        # 1. Create/Identify the main node
        uri = props.get("uri") or f"local:node:{hash(json.dumps(props, sort_keys=True))}"
        props["uri"] = uri
        
        query = f"MERGE (n:{label} {{ uri: $uri }}) SET n += $props RETURN id(n) as node_id"
        res = db.execute_cypher(query, params={"uri": uri, "props": props}, name=f"load_{label}")
        node_id = res[0]["node_id"]
        
        # 2. Process relationships
        for rel in rels:
            target_label = rel["target_label"]
            target_data = rel["target"]
            rel_type = rel["type"]
            
            # Recursive load for target node
            # target_data is a dict (from model_dump). We need to load it.
            # We assume target_data has a uri or identifier.
            target_uri = target_data.get("uri") or f"local:node:{hash(json.dumps(target_data, sort_keys=True))}"
            target_data["uri"] = target_uri
            
            # Load target node
            t_query = f"MERGE (m:{target_label} {{ uri: $target_uri }}) SET m += $props RETURN id(m) as target_id"
            t_res = db.execute_cypher(t_query, params={"target_uri": target_uri, "props": target_data}, name=f"load_{target_label}")
            target_id = t_res[0]["target_id"]
            
            # Create relationship
            r_query = f"MATCH (n) WHERE id(n) = $node_id MATCH (m) WHERE id(m) = $target_id MERGE (n)-[r:{rel_type}]->(m) SET r.materialized = true"
            db.execute_cypher(r_query, params={"node_id": node_id, "target_id": target_id}, name=f"create_rel_{rel_type}")

