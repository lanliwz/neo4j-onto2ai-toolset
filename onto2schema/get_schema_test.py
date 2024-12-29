from neo4j_utility import SemanticGraphDB
from neo4j_connect import *
from cypher_statement.get_schema import *


db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)

def get_schema(start_node:str):
    schema = ("\n".join(db.get_node2node_relationship(start_node))
              + "\n".join(db.get_end_nodes(start_node))
              + "\n".join(db.get_start_nodes(start_node))
              + "\n".join(db.get_relationships(start_node))
              )

    return schema

# start_node ='person'
# print(get_schema(start_node))