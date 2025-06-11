from pydantic import BaseModel, constr


from pydantic import BaseModel

class PartEventHandlers(BaseModel):

    def to_javascript(self):
        return """const nameProperty = 'name';
const genderProperty = 'gender';
const statusProperty = 'status';
const countProperty = 'count';
const ADORNMENT_STROKE_WIDTH = STROKE_WIDTH + 1;
const CORNER_ROUNDNESS = 12;
const IMAGE_TOP_MARGIN = 20;
const MAIN_SHAPE_NAME = 'mainShape';
const IMAGE_DIAMETER = 40;
const STROKE_WIDTH = 2;
const FONT_SIZE_LARGE = '18px';
const FONT_SIZE_MEDIUM = '14px';
const FONT_WEIGHT_BOLD = 'bold';
const FONT_FAMILY = 'Poppins';

const getStrokeForStatus = (status) => {
  switch (status) {
    case 'king':
    case 'queen':
      return theme.colors.kingQueenBorder;
    case 'prince':
    case 'princess':
      return theme.colors.princePrincessBorder;
    case 'civilian':
    default:
      return theme.colors.civilianBorder;
  }
};

function strokeStyle(shape) {
  return shape
    .set({
      fill: theme.colors.personNodeBackground,
      strokeWidth: STROKE_WIDTH
    })
    .bind('stroke', statusProperty, status => getStrokeForStatus(status))
    .bindObject('stroke', 'isHighlighted', (isHighlighted, obj) =>
      isHighlighted
        ? theme.colors.selectionStroke
        : getStrokeForStatus(obj.part.data.status))
}

const genderToText = (gender) => (gender === 'M' ? 'MALE' : 'FEMALE');

const genderToTextColor = (gender) =>
  gender === 'M' ? theme.colors.maleBadgeText : theme.colors.femaleBadgeText;

const genderToFillColor = (gender) =>
  gender === 'M'
    ? theme.colors.maleBadgeBackground
    : theme.colors.femaleBadgeBackground;

const onMouseEnterPart = (e, part) => part.isHighlighted = true;
const onMouseLeavePart = (e, part) => { if (!part.isSelected) part.isHighlighted = false; }
const onSelectionChange = (part) => { part.isHighlighted = part.isSelected; }"""






# create pydantic class for theme, and function to_javascript to generate java script based on
class Colors(BaseModel):
    femaleBadgeBackground: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    maleBadgeBackground: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    femaleBadgeText: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    maleBadgeText: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    kingQueenBorder: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    princePrincessBorder: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    civilianBorder: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    personText: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    personNodeBackground: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    selectionStroke: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    counterBackground: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    counterBorder: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    counterText: constr(pattern=r'^#[0-9a-fA-F]{6}$')
    link: constr(pattern=r'^#[0-9a-fA-F]{6}$')

class Fonts(BaseModel):
    badgeFont: str
    birthDeathFont: str
    nameFont: str
    counterFont: str

class Theme(BaseModel):
    colors: Colors
    fonts: Fonts

    def to_javascript(self):
        colors_js = ',\n'.join([f"      {key}: '{value}'" for key, value in self.colors.dict().items()])
        fonts_js = ',\n'.join([f"      {key}: '{value}'" for key, value in self.fonts.dict().items()])

        return f"""const theme = {{
  colors: {{
{colors_js}
  }},
  fonts: {{
{fonts_js}
  }}
}};"""

