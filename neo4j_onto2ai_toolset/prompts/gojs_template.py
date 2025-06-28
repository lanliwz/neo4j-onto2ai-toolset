gen_data_property_template="""
get accessors as property name and infer the type based on the link {document_url},
then generate Cypher statements to add relationship [:gojs__dataProperty] between (:owl__Class) and (:gojs__DataProperty),
The owl__Class can be identified by rdfs__label, always lower case,
with syntax like:
MATCH (g:owl__Class ...) 
FOREACH ...  
MERGE (p:gojs__DataProperty {name: prop.name,type:prop.type})
MERGE (n)-[:gojs__dataProperty]->(p)
"""