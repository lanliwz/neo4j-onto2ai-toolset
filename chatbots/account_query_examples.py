from langchain_core.example_selectors import SemanticSimilarityExampleSelector
# from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

examples = [
    {
        "question": "total account balance for account 556886 in year 2023?'",
        "query": """MATCH (a:Account {Account: 556886})<-[:BILL_FOR]-(j:JerseyCityTaxBilling {Year: "2023"}) RETURN SUM(j.Billed)+SUM(j.Paid)  AS totalBalance""",
    },
]

import os
url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
database = os.getenv("Neo4jFinDBName")

# neo4jvector = Neo4jVector(url=url, username=username, password=password, database=database,embedding=OpenAIEmbeddings())

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), Chroma, k=5, input_keys=["question"]
)