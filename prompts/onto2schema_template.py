schema_template = """Task: Generate Cypher statement to query a graph database.
Instruction: Use only the provided relationship types and properties in the schema. Do not use any other relationship types or properties that are not provided.
Schema: {schema}
Note: Do not include any explanations or apologies in your responses.Do not respond to any questions that might ask anything else than for you to construct a Cypher statement. Do not include any text except the generated Cypher statement. 
"""

example_template = """
Example question: {example_question}
Example answer:  {example_answer}
"""

question_template = """
The question is: {question}
"""