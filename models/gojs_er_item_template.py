from typing import Optional
from pydantic import BaseModel, constr

class ShapeTemplate(BaseModel):
    desiredSize: tuple[int, int] = (15, 15)
    strokeWidth: int = 0
    margin: tuple[int, int, int, int] = (0, 5, 0, 0)
    figureBinding: str = 'figure'
    themeFill: str = 'color'

class TextBlockTemplate(BaseModel):
    font: str = '14px sans-serif'
    stroke: constr(pattern=r'^#[0-9a-fA-F]{6}$') = '#000000'
    textBinding: str = 'name'
    fontBindingField: str = 'iskey'

class ItemTemplate(BaseModel):
    orientation: str = 'Horizontal'
    margin: tuple[int, int] = (2, 0)
    shape: ShapeTemplate = ShapeTemplate()
    textBlock: TextBlockTemplate = TextBlockTemplate()

    def to_javascript(self, template_name: str = 'itemTempl') -> str:
        js_code = f"""const {template_name} = new go.Panel('{self.orientation}', {{ margin: new go.Margin{self.margin} }})
  .add(
    new go.Shape({{
      desiredSize: new go.Size{self.shape.desiredSize},
      strokeWidth: {self.shape.strokeWidth},
      margin: new go.Margin{self.shape.margin}
    }})
    .bind('{self.shape.figureBinding}')
    .themeData('fill', '{self.shape.themeFill}'),
    new go.TextBlock({{
      font: '{self.textBlock.font}',
      stroke: '{self.textBlock.stroke}'
    }})
    .bind('text', '{self.textBlock.textBinding}')
    .bind('font', '{self.textBlock.fontBindingField}', (k) => (k ? 'italic 14px sans-serif' : '14px sans-serif'))
    .theme('stroke', 'text')
  );"""
        return js_code

