from langchain_core.prompts import PromptTemplate
from prompts.onto2schema_template import *
from onto2schema.neo4j_utility import *

def question2llm(question:str, schema:str, example_question = "", example_answer = ""):
    schema_final_prompt = (PromptTemplate.from_template(schema_template)
                           + PromptTemplate.from_template(example_template)
                           + PromptTemplate.from_template(question_template))
    return schema_final_prompt.invoke({"schema":schema,
                                       "example_question":example_question,
                                       "example_answer":example_answer,
                                       "question":question})

def gen_pydantic_class(start_node:str,db: SemanticGraphDB):
    schema = get_schema(start_node=start_node,db=db)
    final_template = PromptTemplate.from_template(gen_pydantic_class_template)
    return final_template.invoke(schema)

def gen_prompt4schema(start_node:str, db):
    schema = get_schema(start_node=start_node, db=db)

    if len(schema.strip()) == 0 or schema == None:
        schema = start_node
        final_template = PromptTemplate.from_template(crt_realworld_relationship_template)
    else:
        final_template = PromptTemplate.from_template(enh_realworld_relationship_template)


    return final_template.invoke(schema)

# db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)
# print(gen_prompt2enhance_schema("party",db))







