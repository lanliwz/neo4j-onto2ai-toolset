from pydantic import BaseModel
from typing import List
from enum import Enum

def toJavascriptArray(array: List[BaseModel]) -> str:
    return f"[{', '.join([item.toJavascript() for item in array])}]"

class Figure(str, Enum):
    KEY = "Key"
    DECISION = "Decision"
    HEXAGON = "Hexagon"
    CIRCLE = "Circle"
    TRIANGLE_UP = "TriangleUp"


class Color(str, Enum):
    PURPLE = "purple"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"


class Item(BaseModel):
    name: str
    iskey: bool
    figure: Figure
    color: Color

    def toJavascript(self) -> str:
        return f"{{ name: '{self.name}', iskey: {str(self.iskey).lower()}, figure: '{self.figure.value}', color: '{self.color.value}' }}"


class Node(BaseModel):
    key: str
    location: tuple[int, int]
    items: List[Item]
    inheritedItems: List[Item]

    def toJavascript(self) -> str:
        items_js = ', '.join([item.toJavascript() for item in self.items])
        inherited_items_js = ', '.join([item.toJavascript() for item in self.inheritedItems])
        return f"{{ key: '{self.key}', location: new go.Point({self.location[0]}, {self.location[1]}), items: [{items_js}], inheritedItems: [{inherited_items_js}] }}"


class Link(BaseModel):
    from_: str
    to: str
    text: str
    toText: str

    def toJavascript(self) -> str:
        return f"{{ from: '{self.from_}', to: '{self.to}', text: '{self.text}', toText: '{self.toText}' }}"


