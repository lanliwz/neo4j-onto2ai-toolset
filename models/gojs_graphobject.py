from pydantic import BaseModel, Field
from typing import Optional, Tuple, Union, List
from abc import ABC


class GraphObject(BaseModel, ABC):
    """Abstract base class for all GraphObjects, defining common properties including sizing, visibility, transformations, and positioning."""

    # Visibility properties
    background: Optional[str] = None
    visible: bool = True
    opacity: float = Field(1.0, ge=0.0, le=1.0)
    pickable: bool = True

    # Sizing properties
    desired_size: Optional[Tuple[float, float]] = None  # (width, height)
    min_size: Optional[Tuple[float, float]] = None
    max_size: Optional[Tuple[float, float]] = None
    width: Optional[float] = None  # Convenience setter for desired_size[0]
    height: Optional[float] = None  # Convenience setter for desired_size[1]

    # Transformation properties
    angle: float = 0.0  # Rotation in degrees
    scale: float = 1.0  # Scaling factor

    # Layout and stretching
    stretch: Optional[str] = None  # Enum-like behavior for stretch (e.g., "fill", "uniform", etc.)

    # Read-only computed bounds (set after measurement & arrangement)
    natural_bounds: Optional[Tuple[float, float, float, float]] = None  # (x, y, width, height)
    measured_bounds: Optional[Tuple[float, float, float, float]] = None
    actual_bounds: Optional[Tuple[float, float, float, float]] = None

    def is_visible_object(self) -> bool:
        """Determine if the object is visible based on its own visibility and opacity."""
        return self.visible and self.opacity > 0.0


class Panel(GraphObject):
    """A Panel manages the alignment, positioning, and layout of GraphObjects within it."""

    # Alignment & Positioning properties
    alignment: Optional[str] = None  # e.g., "TopLeft", "Center", "BottomRight"
    alignment_focus: Optional[str] = None  # e.g., "Center", "BottomLeft"

    # Grid/Table layout properties
    column: Optional[int] = None
    row: Optional[int] = None
    column_span: Optional[int] = None
    row_span: Optional[int] = None

    # Panel-specific properties
    is_panel_main: bool = False  # Indicates if this is the primary object in the panel
    margin: Optional[Tuple[float, float, float, float]] = None  # (top, right, bottom, left)
    position: Optional[Tuple[float, float]] = None  # (x, y) position within a Panel.Position panel


class Part(Panel):
    """A Part is a top-level object in the visual hierarchy, such as Nodes, Links, Groups, or Adornments."""

    position: Tuple[float, float] = (0.0, 0.0)  # (x, y) in document coordinates
    location: Optional[Tuple[float, float]] = None  # Optional alternative positioning method

    # Read-only properties for visual tree navigation
    panel: Optional[Panel] = None  # The Panel that directly contains this object
    part: Optional["Part"] = None  # The parent Part that contains this object (if applicable)
    layer: Optional[str] = None  # The Layer this Part belongs to
    diagram: Optional[str] = None  # The Diagram this Part's Layer belongs to

class Link(Part):
    """A Link is a Part that connects two Nodes directionally and connects to specific ports."""

    # Basic node connections
    from_node: Optional[Part] = None  # The starting Node of the link
    to_node: Optional[Part] = None  # The ending Node of the link
    from_port_id: Optional[str] = None  # The port ID in the from_node where the link starts
    to_port_id: Optional[str] = None  # The port ID in the to_node where the link ends

    # Additional link connection properties
    from_spot: Optional[str] = None  # Spot where the link exits from the "from" node
    to_spot: Optional[str] = None  # Spot where the link enters the "to" node
    from_end_segment_length: Optional[float] = None  # Length of the segment leaving from_node
    to_end_segment_length: Optional[float] = None  # Length of the segment entering to_node
    from_short_length: Optional[float] = None  # Shortening of the segment from the "from" node
    to_short_length: Optional[float] = None  # Shortening of the segment towards the "to" node


class Node(Part):
    """A Node is a Part that may connect to other nodes via Links or belong to a Group."""
    links_connected: List[Part] = None  # List of links connected to this node
    group: Optional["Group"] = None  # The group this node belongs to


class Group(Node):
    """A Group is a Node that can contain other Nodes."""
    members: List[Node] = None  # List of Nodes that belong to this Group





class BalloonLink(Link):
    pass


class DimensioningLink(Link):
    pass


class FishboneLink(Link):
    pass


class ParallelRouteLink(Link):
    pass


class Adornment(Part):
    pass


class Shape(GraphObject):
    pass


class TextBlock(GraphObject):
    pass


class Picture(GraphObject):
    pass


class Placeholder(GraphObject):
    pass