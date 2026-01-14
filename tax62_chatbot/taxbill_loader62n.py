from neo4j_onto2ai_toolset.onto2ai_tool_config import *
from ai_tools.pdf2graph import generate_cypher4taxbill
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import Neo4jDatabase
from langchain_openai import ChatOpenAI

neo4j_db_name = 'tax62n'
taxdb = Neo4jDatabase(neo4j_bolt_url, username, password, neo4j_db_name)
llm = ChatOpenAI(model="gpt-4o",temperature=0)

def load_all_taxfile(folder_path):
    """
    Iterates through all files in the provided folder and processes each file.
    """
    if not os.path.isdir(folder_path):
        print(f"The path '{folder_path}' is not a valid directory.")
        return

    # Iterate through all files in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                pdfcypher = generate_cypher4taxbill(file_path,llm)
                statements = pdfcypher.split(";")
                for s in statements:
                    try:
                        taxdb.execute_cypher(s)
                    except Exception as e:
                        print(f"Error executing:\n  {s}")
            except Exception as e:
                print(f"Error: {e}")

load_all_taxfile("/Users/weizhang/Downloads/tax-62n/")




