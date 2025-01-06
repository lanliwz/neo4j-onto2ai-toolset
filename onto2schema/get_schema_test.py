from neo4j_utility import SemanticGraphDB
from neo4j_connect import *
from cypher_statement.get_schema import *
from neo4j_utility import get_schema


db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)

# def get_schema(start_node:str):
#     schema = ("\n".join(db.get_node2node_relationship(start_node)) + '\n'
#               + "\n".join(db.get_end_nodes(start_node)) + '\n'
#               + "\n".join(db.get_start_nodes(start_node)) + '\n'
#               + "\n".join(db.get_relationships(start_node)) + '\n'
#               )
#
#     return schema

start_node ='person'
    # 'person'
print(get_schema(start_node,db))