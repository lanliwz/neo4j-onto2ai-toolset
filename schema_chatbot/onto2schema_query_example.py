from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

examples = [
    {
        "question": "what are the account payments in the year 2023-2024 or 2023, group by account or by account",
        "query": """MATCH (t:TaxStatement {year: '2023-2024'})-[:HAS_PAYMENT]->(p:Payment) RETURN p.payor AS account, SUM(p.amount_paid) AS total_amount_paid""",
    },
    {   "question": "what is tax increase year over year from 2023 to 2024?",
        "query": """MATCH (t1:TaxStatement {year: '2023-2024'})-[:INCLUDES]->(l1:Levy) 
                    WITH SUM(l1.tax_amount_with_exemptions) AS y1_total_tax
                    MATCH  (t2:TaxStatement {year: '2024-2025'})-[:INCLUDES]->(l2:Levy) 
                    WITH  y1_total_tax,SUM(l2.tax_amount_with_exemptions) AS y2_total_tax
                    return  y1_total_tax,y2_total_tax"""
    },
]


example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), Chroma, k=4, input_keys=["question"]
)