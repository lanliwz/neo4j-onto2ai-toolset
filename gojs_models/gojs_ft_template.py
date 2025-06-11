from pydantic import BaseModel

class TemplateComponents(BaseModel):

    def to_javascript(self):
        return """const createNodeTemplate = () =>
  new go.Node('Spot', {
    selectionAdorned: false,
    mouseEnter: onMouseEnterPart,
    mouseLeave: onMouseLeavePart,
    selectionChanged: onSelectionChange
  })
    .add(
      new go.Panel('Spot')
        .add(
          personMainShape(),
          personNameTextBlock(),
          personBirthDeathTextBlock()
        ),
      personImage(),
      personBadge(),
      personCounter()
    );

const createLinkTemplate = () =>
  new go.Link({
    selectionAdorned: false,
    routing: go.Routing.Orthogonal,
    layerName: 'Background',
    mouseEnter: onMouseEnterPart,
    mouseLeave: onMouseLeavePart
  })
    .add(
      new go.Shape({
        stroke: theme.colors.link,
        strokeWidth: 1
      })
        .bindObject('stroke', 'isHighlighted', (isHighlighted) =>
          isHighlighted ? theme.colors.selectionStroke : theme.colors.link
        )
        .bindObject('stroke', 'isSelected', (selected) =>
          selected ? theme.colors.selectionStroke : theme.colors.link
        )
        .bindObject('strokeWidth', 'isSelected', (selected) => selected ? 2 : 1)
    );

const initDiagram = (divId) => {
  const diagram = new go.Diagram(divId, {
    layout: new go.TreeLayout({
      angle: 90,
      nodeSpacing: 20,
      layerSpacing: 50,
      layerStyle: go.TreeLayout.LayerUniform,
      treeStyle: go.TreeStyle.LastParents,
      alternateAngle: 90,
      alternateLayerSpacing: 35,
      alternateAlignment: go.TreeAlignment.BottomRightBus,
      alternateNodeSpacing: 20
    }),
    'toolManager.hoverDelay': 100,
    linkTemplate: createLinkTemplate(),
    model: new go.TreeModel({ nodeKeyProperty: 'name' })
  });

  diagram.nodeTemplate = createNodeTemplate();
  const nodes = familyData;
  diagram.model.addNodeDataCollection(nodes);

  diagram.addDiagramListener('InitialLayoutCompleted', () => {
    const root = diagram.findNodeForKey('King George V');
    if (!root) return;
    diagram.scale = 0.6;
    diagram.scrollToRect(root.actualBounds);
  });

  document.getElementById('zoomToFit').addEventListener('click', () => diagram.commandHandler.zoomToFit());

  document.getElementById('centerRoot').addEventListener('click', () => {
    diagram.scale = 1;
    diagram.commandHandler.scrollToPart(diagram.findNodeForKey('King George V'));
  });
};"""


