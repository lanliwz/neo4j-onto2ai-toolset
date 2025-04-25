from pydantic import BaseModel, Field
from typing import List, Dict, Any

from gojs_models.gojs_er_theme_manager import *
from gojs_models.gogs_er_node_template import NodeTemplate
from gojs_models.gojs_er_item_template import ItemTemplate
from gojs_models.gojs_er_link_template import LinkTemplate
from gojs_models.gojs_er_data_model import *


class ForceDirectedLayout(BaseModel):
    isInitial: bool = False

    def to_javascript(self) -> str:
        return f"new go.ForceDirectedLayout({{ isInitial: {str(self.isInitial).lower()} }})"


class ThemeMapEntry(BaseModel):
    key: str
    value: str

    def to_javascript(self) -> str:
        return f"{{ key: '{self.key}', value: {self.value} }}"


class DiagramConfig(BaseModel):
    allowDelete: bool = False
    allowCopy: bool = False
    layout: ForceDirectedLayout
    undoManager_isEnabled: bool = Field(default=True, alias='undoManager.isEnabled')
    themeManager_themeMap: List[ThemeMapEntry] = Field(alias='themeManager.themeMap')
    themeManager_changesDivBackground: bool = Field(alias='themeManager.changesDivBackground')
    themeManager_currentTheme: Optional[str] = Field(default=None, alias='themeManager.currentTheme')

    class Config:
        populate_by_name = True  # Allows using actual field names instead of aliases in __init__

    def to_javascript(self) -> str:
        theme_map_js = ",\n    ".join(entry.to_javascript() for entry in self.themeManager_themeMap)
        current_theme_js = (
            f"'{self.themeManager_currentTheme}'"
            if self.themeManager_currentTheme
            else "document.getElementById('theme').value"
        )
        return f"""myDiagram = new go.Diagram('myDiagramDiv', {{
  allowDelete: {str(self.allowDelete).lower()},
  allowCopy: {str(self.allowCopy).lower()},
  layout: {self.layout.to_javascript()},
  'undoManager.isEnabled': {str(self.undoManager_isEnabled).lower()},
  // use "Modern" themes from extensions/Themes
  'themeManager.themeMap': new go.Map([
    {theme_map_js}
  ]),
  'themeManager.changesDivBackground': {str(self.themeManager_changesDivBackground).lower()},
  'themeManager.currentTheme': {current_theme_js}
}});"""

class GraphLinksModelConfig(BaseModel):
    copiesArrays: bool = True
    copiesArrayObjects: bool = True
    nodeDataArray: List[Dict[str, Any]] = Field(default_factory=list)
    linkDataArray: List[Dict[str, Any]] = Field(default_factory=list)

    def to_javascript(self) -> str:
        return "\n".join([
            "myDiagram.model = new go.GraphLinksModel({ // return",
            f"  copiesArrays: {str(self.copiesArrays).lower()}, // return",
            f"  copiesArrayObjects: {str(self.copiesArrayObjects).lower()}, // return",
            f"  nodeDataArray: nodeDataArray, // return",
            f"  linkDataArray: linkDataArray // return",
            "}); // return"
        ])

def init():
    themes = DiagramThemes(
        themes=[
            Theme(
                name='light',
                colors=ThemeColors(
                    primary="#c0d4a1",
                    green="#4b429e",
                    blue="#3999bf",
                    purple="#7f36b0",
                    red="#c41000"
                )
            ),
            Theme(
                name='dark',
                colors=ThemeColors(
                    primary="#4a4a4a",
                    green="#429e6f",
                    blue="#3f9fc6",
                    purple="#9951c9",
                    red="#ff4d3d"
                )
            ),
        ]
    )
    item_template = ItemTemplate()
    link_template = LinkTemplate()
    node_template = NodeTemplate()
    go_links_model = GraphLinksModelConfig()
    config = DiagramConfig(
        layout=ForceDirectedLayout(isInitial=False),
        themeManager_themeMap=[
            ThemeMapEntry(key="light", value="Modern"),
            ThemeMapEntry(key="dark", value="ModernDark")
        ],
        themeManager_changesDivBackground=True
    )
    return ("function init() {" + '\n'
            + config.to_javascript() + '\n'
            + themes.to_javascript() + '\n'
            + item_template.to_javascript() + '\n'
            + node_template.to_javascript() + '\n'
            + link_template.to_javascript() + '\n'
            + go_links_model.to_javascript() + '\n};'
            )




