from pydantic import BaseModel, constr
from typing import Literal, Optional


class NodeShape(BaseModel):
    figure: str = 'RoundedRectangle'
    stroke: constr(pattern=r'^#[0-9a-fA-F]{6}$') = '#e8f1ff'
    strokeWidth: int = 3
    fillTheme: str = 'primary'


class NodeText(BaseModel):
    font: str = 'bold 18px sans-serif'
    strokeTheme: str = 'text'
    margin: str = 'new go.Margin(0, 24, 0, 2)'  # as JS expression


class SectionTitleText(BaseModel):
    text: str
    font: str = 'bold 15px sans-serif'
    strokeTheme: str = 'text'
    margin: str = 'new go.Margin(3, 24, 3, 2)'


class PanelExpanderButton(BaseModel):
    target: str
    alignment: str = 'go.Spot.Right'
    strokeTheme: str = 'text'
    bindVisibleTo: Optional[str] = None  # optional binding for `inheritedItems` visibility


class NodeTemplate(BaseModel):
    selectionAdorned: bool = True
    resizable: bool = True
    layoutConditions: str = 'go.LayoutConditions.Standard & ~go.LayoutConditions.NodeSized'
    fromSpot: str = 'go.Spot.LeftRightSides'
    toSpot: str = 'go.Spot.LeftRightSides'

    shape: NodeShape = NodeShape()
    headerText: NodeText = NodeText()
    listExpanderButton: PanelExpanderButton = PanelExpanderButton(target='LIST', alignment='go.Spot.TopRight')
    sectionTitle: SectionTitleText = SectionTitleText(text='data properties')
    nonInheritedExpander: PanelExpanderButton = PanelExpanderButton(target='NonInherited')
    inheritedTitle: SectionTitleText = SectionTitleText(text='Inherited Attributes')
    inheritedExpander: PanelExpanderButton = PanelExpanderButton(
        target='Inherited',
        bindVisibleTo='inheritedItems'
    )

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
      margin: {self.headerText.margin},
      font: '{self.headerText.font}'
    }})
    .bind('text', 'key')
    .theme('stroke', '{self.headerText.strokeTheme}'),

    go.GraphObject.build('PanelExpanderButton', {{
      row: 0,
      alignment: {self.listExpanderButton.alignment}
    }}, '{self.listExpanderButton.target}')
    .theme('ButtonIcon.stroke', '{self.listExpanderButton.strokeTheme}'),

    new go.Panel('Table', {{
      name: 'LIST',
      row: 1,
      alignment: go.Spot.TopLeft
    }})
    .add(
      new go.TextBlock('{self.sectionTitle.text}', {{
        row: 0,
        alignment: go.Spot.Left,
        margin: {self.sectionTitle.margin},
        font: '{self.sectionTitle.font}'
      }})
      .theme('stroke', '{self.sectionTitle.strokeTheme}'),

      go.GraphObject.build('PanelExpanderButton', {{
        row: 0,
        alignment: {self.nonInheritedExpander.alignment}
      }}, '{self.nonInheritedExpander.target}')
      .theme('ButtonIcon.stroke', '{self.nonInheritedExpander.strokeTheme}'),

      new go.Panel('Vertical', {{
        row: 1,
        name: 'NonInherited',
        alignment: go.Spot.TopLeft,
        defaultAlignment: go.Spot.Left,
        itemTemplate: itemTempl
      }})
      .bind('itemArray', 'items'),

      new go.TextBlock('{self.inheritedTitle.text}', {{
        row: 2,
        alignment: go.Spot.Left,
        margin: {self.inheritedTitle.margin},
        font: '{self.inheritedTitle.font}'
      }})
      .bind('visible', 'inheritedItems', arr => Array.isArray(arr) && arr.length > 0)
      .theme('stroke', '{self.inheritedTitle.strokeTheme}'),

      go.GraphObject.build('PanelExpanderButton', {{
        row: 2,
        alignment: {self.inheritedExpander.alignment}
      }}, '{self.inheritedExpander.target}')
      .bind('visible', 'inheritedItems', arr => Array.isArray(arr) && arr.length > 0)
      .theme('ButtonIcon.stroke', '{self.inheritedExpander.strokeTheme}'),

      new go.Panel('Vertical', {{
        row: 3,
        name: 'Inherited',
        alignment: go.Spot.TopLeft,
        defaultAlignment: go.Spot.Left,
        itemTemplate: itemTempl
      }})
      .bind('itemArray', 'inheritedItems')
    )
  )
);"""
        return js