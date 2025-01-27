from langchain_openai import ChatOpenAI
from ai_tools.extract_pdf_data import *

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o",temperature=0)

# Custom function to extract a knowledge graph
def generate_schema4taxbill(file, llm):
    text = extract_pdf_data(file)
    prompt = f"""
    Task: Generate Cypher Schema.
    Cypher Syntax Hint: CREATE CONSTRAINT FOR ... REQUIRE ... IS UNIQUE;
    Instruction: Extract node and relationship from Content, with properties, pay attention to tax statement, levy, owner, payment etc. 
    Note: Do not include any explanations or apologies in your responses, code only. 
    Pages and tables are only for structure, do not create page and table as node or relationship.
    
    Content: {text}
    """
    response = llm(prompt)
    return response.content

def generate_cypher4taxbill(file,llm):
    text = extract_pdf_data(file)
    prompt = f"""
    Task: Generate Cypher script.

    Neo4j Schema:
    (:TaxStatement) REQUIRE year IS UNIQUE
    (:Levy) REQUIRE uuid IS UNIQUE
    (:Payment) REQUIRE payment_date IS UNIQUE
    (:Owner) REQUIRE name IS UNIQUE
    (:Property) REQUIRE address IS UNIQUE
    (:TaxStatement)-[:INCLUDES]->(:Levy)
    (:TaxStatement)-[:HAS_PAYMENT]->(:Payment)
    (:Property)-[:HAS_TAX_STATEMENT]->(:TaxStatement)
    (:Owner)-[:OWNS]->(:Property)
    (:Levy) has properties 
        "uuid"	["String"]	mandatory, 
        "description"	["String"] mandatory, 
        "tax_amount_with_exemptions"	["Double"] mandatory,
        "tax_amount_without_exemptions"	["Double"]	optional;
    (:TaxStatement) has properties
        "year"	["String"]	mandatory
    
    Cypher Syntax Examples:
    CREATE CONSTRAINT IF NOT EXISTS FOR ... REQUIRE ... IS UNIQUE;

    
    
    
    
    Instruction: Extract node and relationship from Content.
    Generate id for each Levy node using tax year, property address and Levy description, hash the value, WITH *, apoc.util.md5([data.year, data.address, levy_data.description]) AS levy_uuid
    ALWAYS add WITH
     between MERGE and UNWIND.
    No ";" before WITH statement.
    Do not re-use the same variable.
    Never use CALL statement for apoc.util.md5.
    Instead of CREATE new node, user MERGE instead.
    Pages and tables are only for structure, do not create page and table as node or relationship.
    Content: {text}
    Note: Do not include  any explanations or apologies, or any markdown, like ``` in your responses. 
    """
    response = llm(prompt)
    return response.content
# Explicitly includes all variables, especially TaxStatement, tax year, property address and owner name in each following WITH statement.
# Check if (:Owner) and (:Property) exist first, only create them if not exists.
# create the node if not exist.
# instead of merge node, check if exists, create the node only not exists, then match again.

def generate_pydantic4taxbill(file,llm):
    text = extract_pdf_data(file)
    prompt = f"""
    Task: generate Pydantic Classes.
    Instruction: Extract schema from Content as Pydantic class.
    Need to include Tax Year, Levy Description.
    Create example.
    Pages and tables are only for structure, do not create page and table class.
    Note: Do not include any explanations or apologies in your responses, code only.
    Content: {text}
    """
    response = llm(prompt)
    return response.content

# file_path = "../resource/TaxBillView-2024-2025-f.pdf"
# file_path = "../resource/62N-2022-2-23-TaxBillView.pdf"
# file_path = "../resource/62-2019-2020-taxbill.pdf"
# file_path = "../resource/propertyTax_2021-62NCountryRd.pdf"
# file_path = "../resource/62N-tax-2023-2024.pdf.pdf"
# print(generate_schema4taxbill(file_path,llm).pretty_print())
# print(generate_cypher4taxbill(file_path,llm).split(";"))