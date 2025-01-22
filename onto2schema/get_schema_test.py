from neo4j_utility import SemanticGraphDB
from neo4j_connect import *

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)


# start_node ='adult'
#     # 'person'
# print(get_schema(start_node,db))