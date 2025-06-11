from pydantic import BaseModel

class PersonShapeComponents(BaseModel):

    def to_javascript(self):
        return """const personImage = () =>
  new go.Panel('Spot', {
    alignmentFocus: go.Spot.Top,
    alignment: new go.Spot(0, 0, STROKE_WIDTH / 2, IMAGE_TOP_MARGIN)
  })
    .add(
      new go.Shape({
        figure: 'Circle',
        desiredSize: new go.Size(IMAGE_DIAMETER, IMAGE_DIAMETER)
      })
        .apply(strokeStyle),
      new go.Picture({ scale: 0.9 })
        .apply(pictureStyle)
    );

const personMainShape = () =>
  new go.Shape({
    figure: 'RoundedRectangle',
    desiredSize: new go.Size(215, 110),
    portId: '',
    parameter1: CORNER_ROUNDNESS
  })
    .apply(strokeStyle);

const personNameTextBlock = () =>
  new go.TextBlock({
    stroke: theme.colors.personText,
    font: theme.fonts.nameFont,
    desiredSize: new go.Size(160, 50),
    overflow: go.TextOverflow.Ellipsis,
    textAlign: 'center',
    verticalAlignment: go.Spot.Center,
    toolTip: go.GraphObject.build('ToolTip')
      .add(new go.TextBlock({ margin: 4 }).bind('text', nameProperty)),
    alignmentFocus: go.Spot.Top,
    alignment: new go.Spot(0.5, 0, 0, 25)
  })
    .bind('text', nameProperty);"""

# Example usage:
person_shapes = PersonShapeComponents()
print(person_shapes.to_javascript())
