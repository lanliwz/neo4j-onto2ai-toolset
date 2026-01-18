from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Property(BaseModel):
    name: str
    type: str = "STRING"
    description: Optional[str] = None
    mandatory: bool = False
    cardinality: str = "0..1"

class Node(BaseModel):
    label: str
    properties: List[Property] = []
    description: Optional[str] = None

class Relationship(BaseModel):
    type: str
    start_node_label: str
    end_node_label: str
    properties: List[Property] = []
    description: Optional[str] = None

class DataModel(BaseModel):
    nodes: List[Node] = []
    relationships: List[Relationship] = []
    metadata: Dict[str, Any] = {}
