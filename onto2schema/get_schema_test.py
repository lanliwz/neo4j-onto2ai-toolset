from neo4j_utility import SemanticGraphDB
from neo4j_connect import *
from cypher_statement.get_schema import *

start_node ='asset'
db = SemanticGraphDB(neo4j_bolt_url ,username,password,neo4j_db_name)

start_nodes = db.get_node2node_relationship(start_node)

for n in start_nodes:
    print(n)

