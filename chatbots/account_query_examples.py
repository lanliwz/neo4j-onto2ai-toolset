from langchain_core.example_selectors import SemanticSimilarityExampleSelector
# from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

examples = [
    {
        "question": "total account balance for account 12345 in year 2023?'",
        "query": """MATCH (a:Account {Account: 12345})<-[:BILL_FOR]-(j:JerseyCityTaxBilling {Year: "2023"}) RETURN SUM(j.Billed)+SUM(j.Paid)  AS totalBalance""",
    },
    {
        "question": "what is the account paid for account address start with 105 in the year 2024",
        "query": "MATCH (a:Account)<-[:BILL_FOR]-(j:JerseyCityTaxBilling {Year: '2024'}) WHERE a.address STARTS WITH '105' RETURN a.Account, SUM(j.Paid) as totalPaid",
    },
    {
        "question": "what are the account payments in the year 2024, group by account?",
        "query": "MATCH (a:Account)<-[:BILL_FOR]-(j:JerseyCityTaxBilling {Year: '2024'}) \nRETURN a.Account, SUM(j.Paid) as totalPayments \nORDER BY a.Account",
    },
]

import os
url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
database = os.getenv("Neo4jFinDBName")

# neo4jvector = Neo4jVector(url=url, username=username, password=password, database=database,embedding=OpenAIEmbeddings())

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), Chroma, k=1, input_keys=["question"]
)