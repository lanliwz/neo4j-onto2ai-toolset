from neo4j_utility import SemanticGraphDB
from neo4j_connect import *
from cypher_statement.get_schema import *

start_node ='asset'
db = SemanticGraphDB(neo4j_bolt_url ,username,password,neo4j_db_name)

nodes_rels = db.get_node2node_relationship(start_node)

for n in nodes_rels:
    print(n)

end_nodes = db.get_end_nodes(start_node)

for n in end_nodes:
    print(n)

start_nodes = db.get_start_nodes(start_node)

for n in start_nodes:
    print(n)

rels = db.get_relationships(start_node)
for n in rels:
    print(n)
