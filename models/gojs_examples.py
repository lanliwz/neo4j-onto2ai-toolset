from gojs_er_theme_manager import *
from models.gogs_er_node_template import NodeTemplate
from models.gojs_er_init import *
from models.gojs_er_item_template import ItemTemplate
from models.gojs_er_link_template import LinkTemplate
from models.gojs_er_data_model import *

# Example usage:
themes = DiagramThemes(
    themes=[
        Theme(
            name='light',
            colors=ThemeColors(
                primary="#c0d4a1",
                green="#4b429e",
                blue="#3999bf",
                purple="#7f36b0",
                red="#c41000"
            )
        ),
        Theme(
            name='dark',
            colors=ThemeColors(
                primary="#4a4a4a",
                green="#429e6f",
                blue="#3f9fc6",
                purple="#9951c9",
                red="#ff4d3d"
            )
        ),
    ]
)

# Generate JavaScript for all themes
# print(themes.to_javascript())


# Example instantiation using provided data:
diagram_model = ModelDataArray(
    nodeDataArray=[
        Node(
            key='Products',
            location=(250, 250),
            items=[
                NodeItem(name='ProductID', iskey=True, figure='Decision', color='purple'),
                NodeItem(name='ProductName', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='ItemDescription', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='WholesalePrice', iskey=False, figure='Circle', color='green'),
                NodeItem(name='ProductPhoto', iskey=False, figure='TriangleUp', color='red'),
            ],
            inheritedItems=[
                NodeItem(name='SupplierID', iskey=False, figure='Decision', color='purple'),
                NodeItem(name='CategoryID', iskey=False, figure='Decision', color='purple'),
            ],
        ),
        Node(
            key='Suppliers',
            location=(500, 0),
            items=[
                NodeItem(name='SupplierID', iskey=True, figure='Decision', color='purple'),
                NodeItem(name='CompanyName', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='ContactName', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='Address', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='ShippingDistance', iskey=False, figure='Circle', color='green'),
                NodeItem(name='Logo', iskey=False, figure='TriangleUp', color='red'),
            ]
        ),
        Node(
            key='Categories',
            location=(0, 30),
            items=[
                NodeItem(name='CategoryID', iskey=True, figure='Decision', color='purple'),
                NodeItem(name='CategoryName', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='Description', iskey=False, figure='Hexagon', color='blue'),
                NodeItem(name='Icon', iskey=False, figure='TriangleUp', color='red'),
            ],
            inheritedItems=[
                NodeItem(name='SupplierID', iskey=False, figure='Decision', color='purple'),
            ],
        ),
        Node(
            key='Order Details',
            location=(600, 350),
            items=[
                NodeItem(name='OrderID', iskey=True, figure='Decision', color='purple'),
                NodeItem(name='UnitPrice', iskey=False, figure='Circle', color='green'),
                NodeItem(name='Quantity', iskey=False, figure='Circle', color='green'),
                NodeItem(name='Discount', iskey=False, figure='Circle', color='green'),
            ],
            inheritedItems=[
                NodeItem(name='ProductID', iskey=False, figure='Decision', color='purple'),
            ],
        ),
    ],
    linkDataArray=[
        Link(from_node='Products', to_node='Suppliers', text='0..N', toText='1'),
        Link(from_node='Products', to_node='Categories', text='0..N', toText='1'),
        Link(from_node='Order Details', to_node='Products', text='0..N', toText='1'),
        Link(from_node='Categories', to_node='Suppliers', text='0..N', toText='1'),
    ]
)

# Generate JavaScript snippet exactly as provided:
# print(diagram_model.to_javascript())

# Example usage:
item_template = ItemTemplate()

# print(item_template.to_javascript())

# Example Usage:
link_template = LinkTemplate()

# print(link_template.to_javascript())

# Example usage:
node_template = NodeTemplate()
# print(node_template.to_javascript())

config = DiagramConfig(
    layout=ForceDirectedLayout(isInitial=False),
    themeManager_themeMap=[
        ThemeMapEntry(key="light", value="Modern"),
        ThemeMapEntry(key="dark", value="ModernDark")
    ],
    themeManager_changesDivBackground=True
)

# print(config.to_javascript())
# print(themes.to_javascript())
# print(item_template.to_javascript())
# print(node_template.to_javascript())
# print(link_template.to_javascript())
#
#
# print(diagram_model.to_javascript())
print(init())