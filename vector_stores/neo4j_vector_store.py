from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
import os

vector_db = 'rdfmodel'
# The Neo4jVector Module will connect to Neo4j and create a vector index if needed.

def load_textfile_embeddings(file_path):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    loader = TextLoader(file_path)
    docs = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    all_splits = text_splitter.split_documents(docs)
    vector_store = Neo4jVector.from_documents(
        docs,
        embeddings,
        url=os.getenv("Neo4jFinDBUrl"),
        username=os.getenv("Neo4jFinDBUserName"),
        password=os.getenv("Neo4jFinDBPassword"),
        database=vector_db,
    )
    vector_store.add_documents(all_splits)
    return vector_store


def load_pdffile_embeddings(file_path, db_name, index_name):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    vector_store = Neo4jVector.from_documents(
        docs,
        embeddings,
        url=os.getenv("Neo4jFinDBUrl"),
        username=os.getenv("Neo4jFinDBUserName"),
        password=os.getenv("Neo4jFinDBPassword"),
        database=db_name,
        index_name=index_name,
    )
    vector_store.add_documents(all_splits)
    return vector_store

def get_embedding_store(index_name:str, retrieval_query: str, vector_db:str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    store = Neo4jVector.from_existing_index(
        embeddings,
        url=os.getenv("Neo4jFinDBUrl"),
        username=os.getenv("Neo4jFinDBUserName"),
        password=os.getenv("Neo4jFinDBPassword"),
        database=vector_db,
        index_name=index_name,
        retrieval_query=retrieval_query,
    )
    return store

def load_from_graph_embeddings(index_name:str, node_label:str, properties:[str], vector_db):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    existing_graph = Neo4jVector.from_existing_graph(
        embedding=embeddings,
        url=os.getenv("Neo4jFinDBUrl"),
        username=os.getenv("Neo4jFinDBUserName"),
        password=os.getenv("Neo4jFinDBPassword"),
        database=vector_db,
        index_name=index_name,
        node_label=node_label,
        text_node_properties=properties,
        embedding_node_property="embedding",
    )
# file_path = "../resource/62N-2022-2-23-TaxBillView.pdf"
# store = load_pdffile_embeddings(file_path,'pdf','tax_index')
# retrieval_query = """
# RETURN node.text AS text, score, {start_index:node.start_index} AS metadata
# """
# store = get_embedding_store('tax_index',retrieval_query,'pdf')
# print(store.similarity_search("how much paid?"))


# store = load_from_graph_embeddings("transaction_index",'JerseyCityTaxBilling',['Description'])
# retrieval_query = """
#     RETURN node.Description AS text, score, {account:node.Account} AS metadata
#     """
# store = get_embeddings("transaction_index",retrieval_query,"financedb")
#
# print(store.similarity_search("MONTGORY"))

# 1. build the embeddings
# store = load_from_graph_embeddings("owl__Class_index",'owl__Class',['rdfs__label','skos__definition'],vector_db=vector_db)
# 2. do the similarity search
retrieval_query = """
RETURN node.rdfs__label AS text, score, {owl__Class: node.rdfs__label} AS metadata
"""
store = get_embedding_store("owl__Class_index", retrieval_query,"rdfmodel")

print(store.similarity_search("tax account"))