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

gen_pydantic_class_template = """
Task: generate Pydantic Classes.
Instruction: Create class based on node and create method based on the relationship in the schema, 
add class-level docstrings based on annotation properties , but not class member properties,
add member properties based on your real world knowledge.
all node start with xsd_ are primitive, not class. 
Schema: {schema}
Note: Do not include any explanations or apologies in your responses.
"""

enh_realworld_relationship_template = """
Task: generate Cypher statements to add additional relationship and owl__Class, output each statement as single line element of an array.
Instruction: The node in the schema is a owl__Class with rdfs_label, 
and the annotation properties are metadata for both node and relationship. Use real world knowledge to infer 
new relationship and generate Cypher statement to create the relationship, if possible, add relationship property owl__minQualifiedCardinality..
The new node or relationship should have uri with domain http://mydomain/ontology.
No change to exist node. To reference existing node, the node type is :owl__Class, the property rdfs__label is the one defined in annotation properties. 
rdfs__label always be lower case, with space between words.
relationship type is camel case with first character lower case.
no new owl__ObjectProperty created.
For each node and relationship, generate a skos__definition, which should not contain single quote character.
create the node if not exist.
instead of merge node, check if exists, create the node only not exists, then match again.
match only with rdfs__label.
Schema: {schema}
Note: Add many relationships you can find, do not include any explanations or apologies in your responses.
"""

crt_realworld_relationship_template = """
Task: generate Cypher statements to add relationship and owl__Class, output each statement as one element of an array.
Instruction: The node in the schema is a owl__Class with rdfs_label, 
and the annotation properties are metadata for both node and relationship. Use real world knowledge to infer 
generate Cypher statement to merge the node.
match the nodes and generate Cypher statement to create relationship, if possible, add relationship property owl__minQualifiedCardinality.
The new node or relationship should have uri with domain http://mydomain/ontology. 
rdfs__label always be lower case, with space between words.
relationship type is camel case with first character lower case.
For each node and relationship, generate a skos__definition, which should not contain single quote character.
match only with rdfs__label.
Schema: {schema}
Note: Add many relationships you can find, do not include any explanations or apologies in your responses.
"""

crt_schema_template = """
Task: generate Cypher statements to create relationship, node as owl__Class, class hierarchy as owl__subClassOf, output each statement as single line element of an array.
Instruction: The node in the schema is a owl__Class with rdfs_label, 
and the annotation properties are metadata for both node and relationship. Use real world knowledge to infer 
new relationship and generate Cypher statement to create the relationship, if possible, add relationship property owl__minQualifiedCardinality..
The new node or relationship should have uri with domain http://mydomain/ontology.
No change to exist node. To reference existing node, the node type is :owl__Class, the property rdfs__label is the one defined in annotation properties. 
rdfs__label always be lower case, with space between words.
relationship type is camel case with first character lower case.
no new owl__ObjectProperty created.
For each node and relationship, generate a skos__definition, which should not contain single quote character.
create the node if not exist.
instead of merge node, check if exists, create the node only not exists, then match again.
match only with rdfs__label.


Schema: {schema}
(:GraphObject) is a node
(:Part) is a node,  
(:Node) is a node, A Node is a Part that may connect to other nodes with Links, or that may be a member of a Group.
[:link] is a relationship
(:Node)-[:link]->(:Node)
(:Shape) is a node
(:TextBlock) is a node
(:Node)-[:contain]->[:Shape]
(:Node)-[:contain]->[:TextBlock]
(:Shape)-[:bind]->(:ModelData)
(:TextBlock)-[:bind]->(:ModelData)


Hierarchy: {hierarchy}
(:Panel) is sub class of (:GraphObject)
(:Shape) is sub class of (:GraphObject)
(:TextBlock) is sub class of (:GraphObject)
(:Picture) is sub class of (:GraphObject)
(:Placeholder) is sub class of (:GraphObject)

Note: Add many relationships you can find, do not include any explanations or apologies in your responses.
"""
