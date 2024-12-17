schema_base = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype|owl__Class)
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
apoc.map.removeKey(properties(n), 'rdfs__label') as annotation_properties
'''

end_nodes_return = '''
WITH m,[word IN apoc.text.split(m.rdfs__label, '[-\s]') | toUpper(left(word, 1)) + substring(word, 1)] AS end_node_raw
RETURN distinct apoc.text.join(end_node_raw, '') AS end_node, 
apoc.map.removeKey(properties(m), 'rdfs__label') as annotation_properties
'''

def query_schema(label=None):
    # Base query
    query = schema_base
    # Parameters dictionary

    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause
    query += " RETURN n, r, m"
    return query

def query_start_nodes(label=None):
    # Base query
    query = schema_base
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += start_nodes_return
    return query

def query_end_nodes(label=None):
    # Base query
    query = schema_base
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += end_nodes_return
    return query

def query_node2node_relationship(label=None):
    query = schema_base
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += node2node_relationship_return
    return query
def query_relationships(label=None):
    query = schema_base
    # Modify query if label is provided
    if label is not None:
        query += f"AND n.rdfs__label = '{label}'"

    # Append RETURN clause

    query += relationships_return
    return query