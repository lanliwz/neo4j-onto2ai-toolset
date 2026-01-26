"""
Pydantic models for API request/response validation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ClassInfo(BaseModel):
    """Basic class information."""
    label: str
    uri: str
    definition: Optional[str] = None


class RelationshipInfo(BaseModel):
    """Relationship information with constraints."""
    source_class: str
    source_class_uri: str
    relationship_type: str
    target_class: str
    target_class_uri: str
    definition: Optional[str] = None
    uri: Optional[str] = None
    cardinality: Optional[str] = None
    requirement: Optional[str] = None


class ClassSchema(BaseModel):
    """Complete class schema with relationships."""
    database: str
    classes: List[ClassInfo] = Field(default_factory=list)
    relationships: List[RelationshipInfo] = Field(default_factory=list)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    context: Optional[Dict[str, Any]] = None


class GraphData(BaseModel):
    """Graph visualization data for GoJS."""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    links: List[Dict[str, Any]] = Field(default_factory=list)
    query: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    suggestions: Optional[List[str]] = None
    graph_data: Optional[GraphData] = None


class CypherRequest(BaseModel):
    """Cypher query request."""
    query: str
    params: Optional[Dict[str, Any]] = None


class CypherResponse(BaseModel):
    """Cypher query response with result type detection."""
    results: List[Dict[str, Any]]
    count: int
    result_type: str = "table"  # "graph" or "table"
    graph_data: Optional[GraphData] = None
    table_columns: Optional[List[str]] = None


class PropertyUpdate(BaseModel):
    """Property update request."""
    property_name: str
    new_value: Any


class ClassUpdateRequest(BaseModel):
    """Request to update class properties."""
    updates: List[PropertyUpdate]
