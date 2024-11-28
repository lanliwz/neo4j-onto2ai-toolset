schema = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype|owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
RETURN  n,r,m
'''
node2node_relationship = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype|owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
WITH r,[word IN split(n.rdfs__label, ' ') | toUpper(left(word, 1)) + substring(word, 1)] AS start_node_raw,
[word IN split(m.rdfs__label, ' ') | toUpper(left(word, 1)) + substring(word, 1)] AS end_node_raw
RETURN distinct apoc.text.join(start_node_raw, '') AS start_node,
type(r) as relationship,
apoc.text.join(end_node_raw, '') AS end_node
'''

relationships = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype|owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
RETURN 
distinct type(r) as relationship, properties(r) as annotation_properties
'''

start_nodes = '''
MATCH (n:owl__Class)-[r]->(m:rdfs__Datatype|owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
WITH n,[word IN split(n.rdfs__label, ' ') | toUpper(left(word, 1)) + substring(word, 1)] AS start_node_raw
RETURN DISTINCT apoc.text.join(start_node_raw, '') AS start_node, 
apoc.map.removeKey(properties(n), 'rdfs__label') as annotation_properties
'''

end_nodes = '''
MATCH (:owl__Class)-[r]->(n:rdfs__Datatype|owl__Class)
WHERE NOT type(r) IN ['rdfs__subClassOf', 'owl__isDefinedBy', 'owl__disjointWith','owl__equivalentClass']
WITH n,[word IN split(n.rdfs__label, ' ') | toUpper(left(word, 1)) + substring(word, 1)] AS start_node_raw
RETURN distinct apoc.text.join(start_node_raw, '') AS end_node, 
apoc.map.removeKey(properties(n), 'rdfs__label') as annotation_properties
'''