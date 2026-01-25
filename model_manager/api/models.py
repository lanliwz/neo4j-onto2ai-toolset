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


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    suggestions: Optional[List[str]] = None


class CypherRequest(BaseModel):
    """Cypher query request."""
    query: str
    params: Optional[Dict[str, Any]] = None


class CypherResponse(BaseModel):
    """Cypher query response."""
    results: List[Dict[str, Any]]
    count: int


class PropertyUpdate(BaseModel):
    """Property update request."""
    property_name: str
    new_value: Any


class ClassUpdateRequest(BaseModel):
    """Request to update class properties."""
    updates: List[PropertyUpdate]
