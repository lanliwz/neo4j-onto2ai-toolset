import os
from langchain_neo4j import Neo4jGraph
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)

graph = Neo4jGraph(
    url=os.getenv("Neo4jFinDBUrl"),
    username=os.getenv("Neo4jFinDBUserName"),
    password=os.getenv("Neo4jFinDBPassword"),
    database=os.getenv("Neo4jFinDBName"),
    enhanced_schema=True
)

