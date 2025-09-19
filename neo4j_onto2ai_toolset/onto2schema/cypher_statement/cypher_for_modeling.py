NEO4j_SCHEMA_NODE_LABELS = """
match (n) 
unwind labels(n) as node 
unwind keys(n) as property 
return distinct node, collect(distinct property) as properties 
order by node
"""
NEO4J_SCHEMA_RELATIONSHIP_TYPES = """
MATCH (a)-[r]->(b) 
unwind  labels(a) AS start_label
unwind  labels(b) AS end_label
with start_label,type(r) AS relationship,end_label, keys(r) as property
return distinct start_label,relationship, end_label, collect(distinct property) as properties
ORDER BY start_label,relationship, end_label
"""

NEO4J_LABEL_PROPERTY = """
MATCH (n)
UNWIND labels(n) AS label
RETURN label, COLLECT(DISTINCT keys(n)) AS propertyKeySets
"""

NEO4J_RELATIONSHIP_TYPE_PROPERTY = """
MATCH ()-[r]->()
UNWIND keys(r) AS key
RETURN type(r) AS relType, COLLECT(DISTINCT key) AS propertyKeys
ORDER BY relType
"""


schema_base_class = '''
MATCH (n:owl__Class)
WHERE 1=1
'''

schema_base_class2any = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype|owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
'''


schema_base_cls2cls = '''
MATCH (n:owl__Class)-[r]->(m:owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
'''
schema_base_cls2datatype = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
'''

node2node_relationship_return = '''
WITH r,[word IN apoc.text.split(n.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS start_node_raw,
[word IN apoc.text.split(m.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS end_node_raw
RETURN distinct apoc.text.join(start_node_raw, '') AS start_node,
type(r) as relationship,
apoc.text.join(end_node_raw, '') AS end_node
'''

relationships_return = '''
RETURN DISTINCT type(r) as relationship, properties(r) as annotation_properties
'''

start_nodes_return  = '''
WITH n,[word IN apoc.text.split(n.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS start_node_raw
RETURN DISTINCT apoc.text.join(start_node_raw, '') AS start_node, 
apoc.map.removeKeys(properties(n), ['embedding']) as annotation_properties
'''

start_nodes_dataproperty_return = '''
WITH r,[word IN apoc.text.split(n.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS start_node_raw,
[word IN apoc.text.split(m.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS end_node_raw
RETURN distinct apoc.text.join(start_node_raw, '') AS start_node,
type(r) as relationship,
apoc.text.join(end_node_raw, '') AS end_node
'''

end_nodes_return = '''
WITH m,[word IN apoc.text.split(m.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS end_node_raw
RETURN distinct apoc.text.join(end_node_raw, '') AS end_node, 
apoc.map.removeKeys(properties(m), ['embedding']) as annotation_properties
'''

def query_schema(label=None):
    # Base query
    query = schema_base_cls2cls
    # Parameters dictionary

    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause
    query += " RETURN n, r, m"
    return query

def query_start_nodes(label=None):
    # Base query
    query = schema_base_class
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += start_nodes_return
    return query

def query_end_nodes(label=None):
    # Base query
    query = schema_base_cls2cls
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += end_nodes_return
    return query

def query_cls2cls_relationship(label=None):
    query = schema_base_cls2cls
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += node2node_relationship_return
    return query
def query_relationships(label=None):
    query = schema_base_cls2cls
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += relationships_return
    return query

def query_dataproperty(label=None):
    query = schema_base_cls2datatype
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += start_nodes_dataproperty_return
    return query

