from typing import Optional, List
from pydantic import BaseModel

class TreeNodePersonData(BaseModel):
    name: str
    gender: str
    status: str
    born: str
    death: str
    parent: Optional[str] = None

class TreePersonDataArray(BaseModel):
    nodes: List[TreeNodePersonData]

    def to_javascript(self) -> str:
        nodes_js = ",\n".join([
            "  {" + ", ".join(f"{key}: '{value}'" for key, value in node.dict(exclude_none=True).items()) + "}"
            for node in self.nodes
        ])
        return f"const familyData = [\n{nodes_js}\n];"

# Example usage:
tree_data = TreePersonDataArray(
    nodes=[
        TreeNodePersonData(name='King George V', gender='M', status='king', born='1865', death='1936'),
        TreeNodePersonData(name='King Edward VIII', gender='M', status='king', born='1894', death='1972', parent='King George V'),
        TreeNodePersonData(name='King George VI', gender='M', status='king', born='1895', death='1952', parent='King George V'),
        TreeNodePersonData(name='Princess Mary, Princess Royal and Countess of Harewood', gender='F', status='princess', born='1897', death='1965', parent='King George V'),
        TreeNodePersonData(name='Prince Henry, Duke of Gloucester', gender='M', status='prince', born='1900', death='1974', parent='King George V')
    ]
)


