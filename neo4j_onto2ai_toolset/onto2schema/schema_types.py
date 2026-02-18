from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Property(BaseModel):
    name: str
    type: str = "STRING"
    description: Optional[str] = None
    mandatory: bool = False
    cardinality: str = "0..1"
    uri: Optional[str] = None

class Node(BaseModel):
    label: str
    type: str = "owl__Class"
    properties: List[Property] = []
    description: Optional[str] = None
    uri: Optional[str] = None

class Relationship(BaseModel):
    type: str
    start_node_label: str
    end_node_label: str
    properties: List[Property] = []
    cardinality: str = "0..1"
    requirement: Optional[str] = None
    description: Optional[str] = None
    uri: Optional[str] = None

class DataModel(BaseModel):
    nodes: List[Node] = []
    relationships: List[Relationship] = []
    metadata: Dict[str, Any] = {}
