from langchain_core.prompts import PromptTemplate


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

def question2llm(question:str, schema:str, example_question = "", example_answer = ""):
    schema_final_prompt = (PromptTemplate.from_template(schema_template)
                           + PromptTemplate.from_template(example_template)
                           + PromptTemplate.from_template(question_template))
    return schema_final_prompt.invoke({"schema":schema,
                                       "example_question":example_question,
                                       "example_answer":example_answer,
                                       "question":question})


# print(question2llm("what is my balance",
#                    "my schema",
#                    example_question="how much money paid to account address, the address start with '100 Main Street', ignore case, confirmed on year 2023",
#                    example_answer="""MATCH (a:Account)<-[:FOR]-(p:Payment)-[:CONFIRMED_BY]->(c:Confirmation) WHERE toLower(a.address) STARTS WITH '100 main street' AND c.timestamp =~ '.*2023.*' RETURN SUM(p.amount)"""))






