from pydantic import BaseModel, Field
from typing import List, Optional


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

