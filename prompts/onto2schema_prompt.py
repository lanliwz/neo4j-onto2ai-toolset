from langchain_core.prompts import PromptTemplate
from onto2schema_template import *
from onto2schema.neo4j_utility import SemanticGraphDB
from onto2schema.neo4j_connect import *

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)

def get_schema(start_node:str):
    schema = ("\n".join(db.get_node2node_relationship(start_node))
              + "\n".join(db.get_end_nodes(start_node))
              + "\n".join(db.get_start_nodes(start_node))
              + "\n".join(db.get_relationships(start_node))
              )

    return schema


def question2llm(question:str, schema:str, example_question = "", example_answer = ""):
    schema_final_prompt = (PromptTemplate.from_template(schema_template)
                           + PromptTemplate.from_template(example_template)
                           + PromptTemplate.from_template(question_template))
    return schema_final_prompt.invoke({"schema":schema,
                                       "example_question":example_question,
                                       "example_answer":example_answer,
                                       "question":question})


print(question2llm("what is my balance",
                   "my schema",
                   example_question="how much money paid to account address, the address start with '100 Main Street', ignore case, confirmed on year 2023",
                   example_answer="""MATCH (a:Account)<-[:FOR]-(p:Payment)-[:CONFIRMED_BY]->(c:Confirmation) WHERE toLower(a.address) STARTS WITH '100 main street' AND c.timestamp =~ '.*2023.*' RETURN SUM(p.amount)"""))






