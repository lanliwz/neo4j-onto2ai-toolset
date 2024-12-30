from langchain_neo4j import Neo4jGraph
import os
from langchain_neo4j import GraphCypherQAChain
from langchain_openai import ChatOpenAI

url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
database = os.getenv("Neo4jFinDBName")

graph = Neo4jGraph(
    url=url, username=username, password=password, database=database,enhanced_schema=True
)

# graph.refresh_schema()
# print(graph.schema)


llm = ChatOpenAI(model="gpt-4o", temperature=0)
chain = GraphCypherQAChain.from_llm(
    graph=graph, llm=llm, verbose=True, allow_dangerous_requests=True
)
response = chain.invoke({"query": "total account balance for account 556886 in year 2023?"})
print(response)
# enhanced_graph = Neo4jGraph(enhanced_schema=True)
# print(enhanced_graph.schema)

