from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

examples = [
    {
        "question": "what are the account payments in the year 2023-2024 or 2023, group by account or by account",
        "query": """MATCH (t:TaxStatement {year: '2023-2024'})-[:HAS_PAYMENT]->(p:Payment) RETURN p.payor AS account, SUM(p.amount_paid) AS total_amount_paid""",
    },
]


example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples, OpenAIEmbeddings(), Chroma, k=4, input_keys=["question"]
)