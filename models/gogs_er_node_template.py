from typing import Optional
from pydantic import BaseModel, constr

class NodeShape(BaseModel):
    figure: str = 'RoundedRectangle'
    stroke: constr(pattern=r'^#[0-9a-fA-F]{6}$') = '#e8f1ff'
    strokeWidth: int = 3
    fillTheme: str = 'primary'

class NodeText(BaseModel):
    font: str = 'bold 18px sans-serif'
    strokeTheme: str = 'text'

class PanelExpanderButton(BaseModel):
    target: str
    alignment: str = 'go.Spot.TopRight'
    strokeTheme: str = 'text'

class NodeTemplate(BaseModel):
    selectionAdorned: bool = True
    resizable: bool = True
    layoutConditions: str = 'go.LayoutConditions.Standard & ~go.LayoutConditions.NodeSized'
    fromSpot: str = 'go.Spot.LeftRightSides'
    toSpot: str = 'go.Spot.LeftRightSides'

    shape: NodeShape = NodeShape()
    headerText: NodeText = NodeText()
    listExpanderButton: PanelExpanderButton = PanelExpanderButton(target='LIST')

    def to_javascript(self, diagram_name: str = 'myDiagram') -> str:
        js = f"""{diagram_name}.nodeTemplate = new go.Node('Auto', {{
  selectionAdorned: {str(self.selectionAdorned).lower()},
  resizable: {str(self.resizable).lower()},
  layoutConditions: {self.layoutConditions},
  fromSpot: {self.fromSpot},
  toSpot: {self.toSpot}
}})
.bindTwoWay('location')
.bindObject('desiredSize', 'visible', v => new go.Size(NaN, NaN), undefined, 'LIST')
.add(
  new go.Shape('{self.shape.figure}', {{
    stroke: '{self.shape.stroke}',
    strokeWidth: {self.shape.strokeWidth}
  }}).theme('fill', '{self.shape.fillTheme}'),
  new go.Panel('Table', {{
    margin: 8,
    stretch: go.Stretch.Fill
  }})
  .addRowDefinition(0, {{ sizing: go.Sizing.None }})
  .add(
    new go.TextBlock({{
      row: 0,
      alignment: go.Spot.Center,
      margin: new go.Margin(0, 24, 0, 2),
      font: '{self.headerText.font}'
    }})
    .bind('text', 'key')
    .theme('stroke', '{self.headerText.strokeTheme}'),
    go.GraphObject.build('PanelExpanderButton', {{
      row: 0,
      alignment: {self.listExpanderButton.alignment}
    }}, '{self.listExpanderButton.target}')
    .theme('ButtonIcon.stroke', '{self.listExpanderButton.strokeTheme}')
  )
);"""
        return js

