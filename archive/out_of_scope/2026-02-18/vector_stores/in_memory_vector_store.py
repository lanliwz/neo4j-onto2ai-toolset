from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_pdffile_embeddings(file_path):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_documents(all_splits)
    return vector_store

file_path = "../resource/62N-2022-2-23-TaxBillView.pdf"
# store = load_pdffile_embeddings(file_path)
# print(store.similarity
# _search("how much paid?"))
loader = PyPDFLoader(file_path)
docs = loader.load()
print(docs)