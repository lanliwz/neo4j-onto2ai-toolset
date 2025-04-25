from pydantic import BaseModel, constr
from typing import List

class ThemeColors(BaseModel):
    primary: constr(pattern=r'^#[0-9a-fA-F]{6}$')  # Primary color
    green: constr(pattern=r'^#[0-9a-fA-F]{6}$')    # Green accent
    blue: constr(pattern=r'^#[0-9a-fA-F]{6}$')     # Blue accent
    purple: constr(pattern=r'^#[0-9a-fA-F]{6}$')   # Purple accent
    red: constr(pattern=r'^#[0-9a-fA-F]{6}$')      # Red accent

class Theme(BaseModel):
    name: str
    colors: ThemeColors

    def to_javascript(self) -> str:
        colors_js = ',\n      '.join(f"{key}: '{value}'" for key, value in self.colors.dict().items())
        js_snippet = f"""myDiagram.themeManager.set('{self.name}', {{
  colors: {{
      {colors_js}
  }}
}});"""
        return js_snippet

class DiagramThemes(BaseModel):
    themes: List[Theme]

    def to_javascript(self) -> str:
        return "\n\n".join(theme.to_javascript() for theme in self.themes)

