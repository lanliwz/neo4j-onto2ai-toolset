# langchain v0.3 +
import os
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models import init_chat_model

# model = init_chat_model("gpt-4o-mini", model_provider="openai", temperature=0)

model = init_chat_model(
    "gemini-1.5-pro", model_provider="google_vertexai", temperature=0
)


system_template = "Translate the following from English into {language}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

prompt = prompt_template.invoke({"language": "Italian", "text": "hi!"})


for token in model.stream(prompt):
    print(token.content, end="|")

print(model.invoke(prompt))




