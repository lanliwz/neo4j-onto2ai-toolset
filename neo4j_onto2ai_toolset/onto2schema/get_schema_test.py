from neo4j_utility import SemanticGraphDB, get_schema,get_node4schema
from neo4j_onto2ai_toolset.schema_chatbot.onto2schema_connect import *

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)


start_node ='graph object'
    # 'person'
# print(get_node4schema(start_node,db))
print(get_schema(start_node,db))