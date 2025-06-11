from pydantic import BaseModel

class BindingComponents(BaseModel):

    def to_javascript(self):
        return """const personBadge = () =>
  new go.Panel('Auto', {
    alignmentFocus: go.Spot.TopRight,
    alignment: new go.Spot(1, 0, -25, STROKE_WIDTH - 0.5)
  })
    .add(
      new go.Shape({
        figure: 'RoundedRectangle',
        parameter1: CORNER_ROUNDNESS,
        parameter2: 4 | 8, // round only the bottom
        desiredSize: new go.Size(NaN, 22.5),
        stroke: null
      })
        .bind('fill', genderProperty, genderToFillColor),
      new go.TextBlock({
        font: theme.fonts.badgeFont
      })
        .bind('stroke', genderProperty, genderToTextColor)
        .bind('text', genderProperty, genderToText)
    );

const personBirthDeathTextBlock = () =>
  new go.TextBlock({
    stroke: theme.colors.personText,
    font: theme.fonts.birthDeathFont,
    alignmentFocus: go.Spot.Top,
    alignment: new go.Spot(0.5, 1, 0, -35)
  })
    .bind('text', '', ({ born, death }) => {
      if (!born) return '';
      return `${born} - ${death ?? ''}`;
    });

// Panel to display the number of children a node has
const personCounter = () =>
  new go.Panel('Auto', {
    visible: false,
    alignmentFocus: go.Spot.Center,
    alignment: go.Spot.Bottom
  })
    .bindObject('visible', '', (obj) => obj.findLinksOutOf().count > 0)
    .add(
      new go.Shape('Circle', {
        desiredSize: new go.Size(29, 29),
        strokeWidth: STROKE_WIDTH,
        stroke: theme.colors.counterBorder,
        fill: theme.colors.counterBackground
      }),
      new go.TextBlock({
        alignment: new go.Spot(0.5, 0.5, 0, 1),
        stroke: theme.colors.counterText,
        font: theme.fonts.counterFont,
        textAlign: 'center'
      })
        .bindObject('text', '', (obj) => obj.findNodesOutOf().count)
    );

function pictureStyle(pic) {
  return pic
    .bind('source', '', ({ status, gender }) => {
      switch (status) {
        case 'king':
        case 'queen':
          return './images/king.svg';
        case 'prince':
        case 'princess':
          return './images/prince.svg';
        case 'civilian':
          return gender === 'M'
            ? './images/male-civilian.svg'
            : './images/female-civilian.svg';
        default:
          return './images/male-civilian.svg';
      }
    })
    .bind('desiredSize', 'status', status => {
      switch (status) {
        case 'king':
        case 'queen':
          return new go.Size(30, 20)
        case 'prince':
        case 'princess':
          return new go.Size(28, 20)
        case 'civilian':
        default:
          return new go.Size(24, 24)
      }
    });
}"""

