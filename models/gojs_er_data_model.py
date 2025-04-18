from typing import List, Optional
from pydantic import BaseModel

class NodeItem(BaseModel):
    name: str
    iskey: bool
    figure: str
    color: str

    def to_js(self):
        return {
            'name': self.name,
            'iskey': self.iskey,
            'figure': self.figure,
            'color': self.color
        }

class Node(BaseModel):
    key: str
    location: tuple[int, int]
    items: List[NodeItem]
    inheritedItems: Optional[List[NodeItem]] = []

    def to_js(self):
        js_node = {
            'key': self.key,
            'location': f"new go.Point({self.location[0]}, {self.location[1]})",
            'items': [item.to_js() for item in self.items],
        }
        if self.inheritedItems:
            js_node['inheritedItems'] = [item.to_js() for item in self.inheritedItems]
        else:
            js_node['inheritedItems'] = []
        return js_node

class Link(BaseModel):
    from_node: str
    to_node: str
    text: Optional[str] = ''
    toText: Optional[str] = ''

    def to_js(self):
        return {
            'from': self.from_node,
            'to': self.to_node,
            'text': self.text,
            'toText': self.toText
        }

class DiagramModel(BaseModel):
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

        js_code = f"""const nodeDataArray = [
  {node_array_js}
];

const linkDataArray = [
  {link_array_js}
];"""

        return js_code

