import json

from langgraph.graph import END, START, StateGraph
from onto2schema_connect import *
from onto2schema_langraph_model import *

lg = StateGraph(OverallState, input=InputState, output=OutputState)

db = SemanticGraphDB(neo4j_bolt_url,username,password,neo4j_db_name)
# ask question
lg.add_node(more_question)

# extract exist schema and enhance it
def query_to_enhance_schema(state: OverallState):
    return generate_cypher(state=state,db=db,llm=llm)
lg.add_node(query_to_enhance_schema)

# add enhanced entity and relationship to current schema
def run_query(state: OverallState):
    execute_graph_query(state,graphdb)
lg.add_node(run_query)

def del_dups(state: OverallState):
    del_dup_cls_rels(state,graphdb)
lg.add_node(del_dups)
#
lg.add_edge(START,"more_question")
lg.add_edge("more_question","query_to_enhance_schema")
lg.add_edge("query_to_enhance_schema","run_query")
lg.add_edge("run_query","del_dups")
lg.add_edge("del_dups",END)
lg = lg.compile()

print(lg.invoke({"question": "enhance the schema of person based on the schema provide"}).get('database_records'))

# text = gen_prompt2enhance_schema("language",db)
# # text="\nTask: generate Cypher statement to add additional relationship and owl__Class.\nInstruction: The node in the schema is a owl__Class with rdfs_label, \nand the annotation properties are metadata for both node and relationship. Use real world knowledge to infer \nnew relationship and generate Cypher statement to create the relationship.\nThe new node or relationship should have uri with domain http://mydomain/ontology.\nNo change to exist node. To reference existing node, the node type is :owl__Class, the property rdfs__label is the one defined in annotation properties. \nrdfs__label always be lower case, with space between words.\nrelationship type is camel case with first character lower case.\nno new owl__ObjectProperty created.\nAdd with statement between Merge and Match.\nadd defined variable to each WITH statement.\nadd skos__definition to each node and relationship.\ncreate the node if not exist.\ninstead of merge node, check if exists, create the node only not exists, then match again.\nmatch only with rdfs__label.\nSchema: (:Party)-[:isAPartyTo]->(:Undefined)\n(:Undefined) is a node, annotation properties {'rdfs__label': 'undefined'}\n(:Party) is a node, annotation properties {'rdfs__label': 'party', 'skos__definition': 'person or organization', 'uri': 'https://www.omg.org/spec/Commons/PartiesAndSituations/Party'}\n[:isAPartyTo] is a relationship, annotation properties  {'rdfs__label': 'is a party to', 'skos__definition': 'identifies an agreement, contract, policy, regulation, situation, or other arrangement that a party is associated with', 'uri': 'https://www.omg.org/spec/Commons/PartiesAndSituations/isAPartyTo'}\n\nNote: Add many relationships you can find, do not include any explanations or apologies in your responses.\n"
# print(text.to_string())

