from gojs_er_theme_manager import *
from models.gogs_er_node_template import NodeTemplate
from models.gojs_er_init import *
from models.gojs_er_data_model import *



# Example instantiation using provided data:
model_data_array = ModelDataArray(
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
print(model_data_array.to_javascript())
print(init())