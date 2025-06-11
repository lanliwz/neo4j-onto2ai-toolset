# Example usage:
from gojs_models.gogs_ft_binding import BindingComponents
from gojs_models.gojs_ft_template import TemplateComponents
from gojs_models.gojs_ft_theme_manager import *

theme = Theme(
    colors=Colors(
        femaleBadgeBackground='#FFCBEA',
        maleBadgeBackground='#A2DAFF',
        femaleBadgeText='#7A005E',
        maleBadgeText='#001C76',
        kingQueenBorder='#FEBA00',
        princePrincessBorder='#679DDA',
        civilianBorder='#58ADA7',
        personText='#383838',
        personNodeBackground='#FFFFFF',
        selectionStroke='#485670',
        counterBackground='#485670',
        counterBorder='#FFFFFF',
        counterText='#FFFFFF',
        link='#686E76'
    ),
    fonts=Fonts(
        badgeFont='bold 12px Poppins',
        birthDeathFont='14px Poppins',
        nameFont='500 18px Poppins',
        counterFont='14px Poppins'
    )
)

# print(theme.to_javascript())

# Example usage:
handlers = PartEventHandlers()
# print(handlers.to_javascript())

# Example usage:
bindings = BindingComponents()
# print(bindings.to_javascript())

# Example usage:
templates = TemplateComponents()
print(templates.to_javascript())

# Example usage:
# print(bindings.to_javascript())