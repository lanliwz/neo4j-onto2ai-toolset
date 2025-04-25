from typing import List, Optional
from pydantic import BaseModel,Field


class NodeItem(BaseModel):
    name: str
    iskey: bool
    figure: str
    color: str

    def to_js(self) -> str:
        def format_value(value):
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return 'true' if value else 'false'
            else:
                return str(value)

        return (
            '{ '
            f'name: {format_value(self.name)}, '
            f'iskey: {format_value(self.iskey)}, '
            f'figure: {format_value(self.figure)}, '
            f'color: {format_value(self.color)} '
            '}'
        )

def node_items_to_js_array(items: List[NodeItem]) -> str:
    js_objects = [item.to_js() for item in items]
    return '[\n  ' + ',\n  '.join(js_objects) + '\n]'

class Location(BaseModel):
    b: float  # assuming numeric, use `int` if always integers
    k: float
    h: bool

class Node(BaseModel):
    key: str
    # location: tuple[int, int]
    location: Location
    items: List[NodeItem]
    inheritedItems: Optional[List[NodeItem]] = []

    def to_js(self):
        js_node = {
            'key': self.key,
            'location': f"new go.Point({self.location.b}, {self.location.k})",
            'items': node_items_to_js_array(self.items),
        }
        if self.inheritedItems:
            inh_items : List[NodeItem] = self.inheritedItems
            js_node['inheritedItems'] = node_items_to_js_array(inh_items)
        else:
            js_node['inheritedItems'] = []
        return js_node

class Link(BaseModel):
    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    text: Optional[str] = ''
    toText: Optional[str] = ''
    model_config = {
        "populate_by_name": True  # Needed if you're using from_node instead of 'from'
    }

    def to_js(self):
        return {
            'from': self.from_node,
            'to': self.to_node,
            'text': self.text,
            'toText': self.toText
        }

class ModelDataArray(BaseModel):
    nodeDataArray: List[Node]
    linkDataArray: List[Link]

    def to_javascript(self) -> str:
        node_array_js = ',\n  '.join([
            '{\n' +
            f"    key: '{node.key}',\n" +
            f"    location: {node.to_js()['location']},\n" +
            f"    items: {node.to_js()['items']},\n" +
            f"    inheritedItems: {node.to_js()['inheritedItems']}\n" +
            '  }'
            for node in self.nodeDataArray
        ])

        link_array_js = ',\n  '.join([
            '{ ' +
            f"from: '{link.from_node}', to: '{link.to_node}', text: '{link.text}', toText: '{link.toText}'" +
            ' }'
            for link in self.linkDataArray
        ])

        js_code = f"""nodeDataArray = [
  {node_array_js}
];

linkDataArray = [
  {link_array_js}
];"""

        return js_code

