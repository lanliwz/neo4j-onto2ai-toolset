# Cypher query to delete all nodes and relationships in the database
del_all_node =  '''
MATCH (n) DETACH DELETE n
'''
# Cypher query to delete all relationships but keep nodes
del_all_relationship =  '''
MATCH ()-[n]-() DETACH DELETE n
'''
# 	•	matches specific restriction fillers (someValuesFrom, allValuesFrom, onClass)
# 	•	builds a safe relationship type from uri
# 	•	merges the relationship (no dupes)
# 	•	copies all *Cardinality* props
# 	•	deletes only the restriction node and the subClassOf edge (optional)
crt_rel__restrict_cardinality = '''
// ObjectProperty restriction -> relationship, copy cardinality props
MATCH (n:owl__Class)-[sub:rdfs__subClassOf]->(res:owl__Restriction)
MATCH (res)-[:owl__onProperty]->(onp:owl__ObjectProperty)

// pick the filler(s) you actually support
OPTIONAL MATCH (res)-[:owl__someValuesFrom|owl__allValuesFrom|owl__onClass]->(des:owl__Class)
WITH n, sub, res, onp, des
WHERE des IS NOT NULL

// compute a safe relationship type from the property URI (supports / or # namespaces)
WITH n, sub, res, onp, des,
     coalesce(
       apoc.text.regexGroups(onp.uri, '([^/#]+)$')[0][0],
       onp.rdfs__label
     ) AS rawType
WITH n, sub, res, onp, des,
     apoc.text.replace(rawType, '[^A-Za-z0-9_]', '_') AS relType

CALL (n, des, onp, res, relType) {
  // MERGE to avoid duplicates
  CALL apoc.merge.relationship(
    n,
    relType,
    { uri: onp.uri },          // identity key(s) for merge
    properties(onp),           // on create / set
    des,
    {}
  ) YIELD rel

  // copy ALL cardinality-ish keys
  WITH rel, res
  UNWIND [k IN keys(res) WHERE k CONTAINS 'Cardinality'] AS k
  WITH rel, k, res[k] AS v
  WHERE v IS NOT NULL
  CALL apoc.create.setRelProperty(rel, k, v) YIELD rel AS _
  RETURN rel
}
WITH res, sub
// safer cleanup: delete only the restriction and its subclass edge
DELETE sub
DETACH DELETE res
'''
# Create relationships from owl:Class with object property restrictions, copying cardinality from owl:Restriction (owl:onProperty + owl:Class)
crt_rel__restrict_cardinality_1 = '''
// relationship with cardinality 
MATCH (n:owl__Class)-[sub:rdfs__subClassOf]->(res:owl__Restriction)-[:owl__onProperty]->(onp:owl__ObjectProperty)  
WITH n,res,onp,sub 
MATCH (res)-[]->(des:owl__Class)
WITH n,onp,des,sub,res
CALL apoc.create.relationship(n, last(split(properties(onp).uri,"/")), properties(onp), des)
YIELD rel
WITH onp,rel,res, [key IN keys(res) WHERE key CONTAINS 'Cardinality'] AS cardinalityKeys where  res[head(cardinalityKeys)] is not null 
set rel[ head(cardinalityKeys)]=res[head(cardinalityKeys)]
//CLEAN ALL CONVERTED NODES
with res, onp
MATCH (res)-[DEL1]-(),(onp)-[DEL2]-()
DELETE DEL1,DEL2
DELETE res,onp
'''
# Create relationships from owl:Class with datatype property restrictions, copying cardinality from owl:Restriction (owl:onProperty + owl:onDataRange)
crt_rel__restrict_cardinality_2 = '''
// relationship with cardinality 
MATCH (n:owl__Class)-[sub:rdfs__subClassOf]-> (res:owl__Restriction)-[:owl__onDataRange]->(dtype:Resource) with n,res,dtype 
MATCH (res)-[:owl__onProperty]->(prop:owl__DatatypeProperty) with n,res,prop,dtype 
CALL apoc.create.relationship(n, last(split(properties(prop).uri,"/")), properties(prop), dtype)
YIELD rel
WITH prop,rel,res, [key IN keys(res) WHERE key CONTAINS 'Cardinality'] AS cardinalityKeys 
WHERE  res[head(cardinalityKeys)] is not null 
SET rel[ head(cardinalityKeys)]=res[head(cardinalityKeys)]
with res, prop
MATCH (res)-[DEL1]-(),(prop)-[DEL2]-()
DELETE DEL1,DEL2
DELETE res,prop
'''
# Create object property relationships inferred from owl:allValuesFrom restrictions and tag them with inferred_by='allValuesFrom'
allValueFrom = '''
//Create REL allValuesFrom
MATCH (n:owl__Class)-[sub:rdfs__subClassOf]->(res:owl__Restriction)-[:owl__onProperty]->(onp:owl__ObjectProperty)  
WITH n,res,onp,sub 
MATCH (res)-[some:owl__allValuesFrom]->(des:owl__Class)
WITH n,onp,des,sub,some,res
CALL apoc.create.relationship(n, last(split(properties(onp).uri,"/")), properties(onp), des)
YIELD rel
SET rel.inferred_by='allValuesFrom',rel.property_type='owl__ObjectProperty'
WITH sub,some
DELETE some
'''
# Tag existing relationships between classes as inferred_by='allValuesFrom' when supported by owl:allValuesFrom restrictions, then clean up restriction structure
allValueFrom_01 = '''
match (cls:owl__Class)-[link]->(cls1:owl__Class) 
with cls,link,cls1 
match (cls)-[sub:rdfs__subClassOf]->(restriction)-[some:owl__allValuesFrom]->(cls1) 
SET link.inferred_by='allValuesFrom'
DELETE sub,some
DELETE restriction
'''
# Create object property relationships inferred from owl:someValuesFrom restrictions and tag them with inferred_by='someValuesFrom'
someValueFrom = '''
//Create REL someValuesFrom
match (n:owl__Class)-[sub:rdfs__subClassOf]->(res:owl__Restriction)-[:owl__onProperty]->(onp:owl__ObjectProperty)  
WITH n,res,onp 
match (res)-[some:owl__someValuesFrom]->(des:owl__Class)
with n,onp,des,some
CALL apoc.create.relationship(n, last(split(properties(onp).uri,"/")), properties(onp), des)
YIELD rel
SET rel.inferred_by='someValuesFrom',rel.property_type='owl__ObjectProperty'
DELETE some
'''
# Tag existing relationships between classes as inferred_by='someValuesFrom' when supported by owl:someValuesFrom restrictions, then clean up restriction structure
someValueFrom_01 = '''
match (cls:owl__Class)-[link]->(cls1:owl__Class) 
with cls,link,cls1 
match (cls)-[sub:rdfs__subClassOf]->(restriction)-[some:owl__someValuesFrom]->(cls1) 
SET link.inferred_by='someValuesFrom'
DELETE sub,some
DELETE restriction
'''
# Materialize OWL ObjectProperty semantics into direct Neo4j relationships:
# - Use rdfs:domain/rdfs:range to connect owl__Class -> owl__Class
# - Relationship type is derived from the ObjectProperty URI local-name
# - Annotate inferred relationships and remove the original rdfs:domain/rdfs:range triples
domain_range_1 = '''
// Materialize ObjectProperty domain/range as property-graph edge
// Rel-type extraction supports both '/' and '#' URIs.
MATCH (n:owl__Class)<-[d:rdfs__domain]-(op:owl__ObjectProperty)-[r:rdfs__range]->(c:owl__Class)
WITH n, op, c, d, r,
     last(split(last(split(properties(op).uri, "#")), "/")) AS relType
CALL apoc.create.relationship(n, relType, properties(op), c)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='domain-range'
DELETE d, r
'''
# Materialize OWL DatatypeProperty semantics into direct Neo4j relationships:
# - Use rdfs:domain/rdfs:range to connect owl__Class -> Resource (typically XSD/rdfs datatypes)
# - Relationship type is derived from the DatatypeProperty URI local-name
# - Annotate inferred relationships and remove the original rdfs:domain/rdfs:range triples
domain_range_2 = '''
// Materialize DatatypeProperty domain/range as property-graph edge
// Rel-type extraction supports both '/' and '#' URIs.
MATCH (n:owl__Class)<-[d:rdfs__domain]-(op:owl__DatatypeProperty)-[r:rdfs__range]->(c:Resource)
WITH n, op, c, d, r,
     last(split(last(split(properties(op).uri, "#")), "/")) AS relType
CALL apoc.create.relationship(n, relType, properties(op), c)
YIELD rel
SET rel.property_type='owl__DatatypeProperty', rel.inferred_by='domain-range'
DELETE d, r
'''
# Create relationships from domain classes to restriction target classes via owl:onProperty + rdfs:subClassOf (object properties)
domain_onProperty = '''
// Materialize ObjectProperty semantics via OWL Restriction + onProperty + domain:
// - Find class n that is the rdfs:domain of an ObjectProperty op
// - Find restriction res that uses op via owl:onProperty
// - Find target class des such that des rdfs:subClassOf res
// - Create direct Neo4j relationship n -[:<relType>]-> des
// - Relationship type is derived from op.uri local-name (supports both '/' and '#')
// - Remove the original rdfs:domain edge (d) after materialization
MATCH (n:owl__Class)<-[d:rdfs__domain]-(op:owl__ObjectProperty)<-[:owl__onProperty]-(res:owl__Restriction)
WITH n, op, res, d,
     last(split(last(split(properties(op).uri, "#")), "/")) AS relType
MATCH (res)<-[:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(n, relType, properties(op), des)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='domain'
DELETE d
'''
range_onProperty = '''
// Materialize ObjectProperty semantics via OWL Restriction + onProperty + range:
// - Find class n that is the rdfs:range of an ObjectProperty op
// - Find restriction res that uses op via owl:onProperty
// - Find source class des such that des rdfs:subClassOf res
// - Create direct Neo4j relationship des -[:<relType>]-> n
// - Relationship type is derived from op.uri local-name (supports both '/' and '#')
// - Remove the original rdfs:range edge (d) after materialization
MATCH (n:owl__Class)<-[d:rdfs__range]-(op:owl__ObjectProperty)<-[:owl__onProperty]-(res:owl__Restriction)
WITH n, op, res, d,
     last(split(last(split(properties(op).uri, "#")), "/")) AS relType
MATCH (res)<-[:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(des, relType, properties(op), n)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='range'
DELETE d
'''
data_property_without_range = '''
// Materialize DatatypeProperty with domain but missing range:
// - For DatatypeProperty prop with rdfs:domain cls and NO rdfs:range
// - MERGE a shared placeholder datatype node (rdfs__Datatype {uri:'urn:onto2ai:datatype:undefined'})
// - Create cls -[:<relType>]-> placeholder relationship (relType derived from prop.uri; supports '/' and '#')
// - Remove all prop relationships and delete prop (destructive rewiring)
MATCH (prop:owl__DatatypeProperty)-[:rdfs__domain]->(cls:owl__Class)
WHERE NOT (prop)-[:rdfs__range]-()
WITH prop, cls,
     last(split(last(split(prop.uri, "#")), "/")) AS relType
MERGE (dtype:rdfs__Datatype {uri: 'urn:onto2ai:datatype:undefined'})
  ON CREATE SET dtype.rdfs__label = 'undefined'
WITH prop, cls, relType, dtype
CALL apoc.create.relationship(cls, relType, properties(prop), dtype)
YIELD rel
WITH prop
MATCH (prop)-[r]-()
DELETE r
DELETE prop
'''
object_property_without_range = '''
// Materialize ObjectProperty with domain but missing range:
// - For ObjectProperty prop with rdfs:domain cls and NO rdfs:range
// - Create a placeholder class node (owl__Class {rdfs__label:'undefined'})
// - Create cls -[:<relType>]-> undefinedClass relationship (relType derived from prop.uri)
// - Delete all existing relationships from prop and delete prop itself (destructive rewiring)
MATCH (prop:owl__ObjectProperty)-[:rdfs__domain]->(cls:owl__Class)
WHERE NOT (prop)-[:rdfs__range]-()
WITH prop, cls,
     last(split(last(split(prop.uri, "#")), "/")) AS relType
MERGE (target:owl__Class {uri:'urn:onto2ai:class:undefined'})
  ON CREATE SET target.rdfs__label='undefined'
WITH prop, cls, relType, target
CALL apoc.create.relationship(cls, relType, properties(prop), target)
YIELD rel
WITH prop
MATCH (prop)-[r]-()
DELETE r
DELETE prop
'''
range_onProperty_datarange = '''
// Materialize owl:onDataRange restriction into a direct relationship:
// - From class n to dtype node via the property used in the restriction
// - Relationship type derived from prop.uri local-name (supports both '/' and '#')
// - Tag inferred relationship with inferred_by='owl__onDataRange'
// - Remove owl__onDataRange edge (d) after materialization
MATCH (n:owl__Class)-[:rdfs__subClassOf]->(res:owl__Restriction)-[d:owl__onDataRange]-(dtype)
MATCH (res)-[:owl__onProperty]->(prop)
WITH n, dtype, d, prop,
     last(split(last(split(properties(prop).uri, "#")), "/")) AS relType
CALL apoc.create.relationship(n, relType, properties(prop), dtype)
YIELD rel
SET rel.property_type = prop.rdfs__label, rel.inferred_by='owl__onDataRange'
DELETE d
'''
range_onProperty_object = '''
// Materialize ObjectProperty range semantics via Restriction + subPropertyOf chain:
// - Find class n that is the rdfs:range of some ObjectProperty (or its super-properties)
// - Find restriction res that uses op (or sub-property) via owl:onProperty
// - Find source class des such that des rdfs:subClassOf res
// - Create des -[:<relType>]-> n where relType comes from op.uri (supports both '/' and '#')
// - Delete rdfs:range edge (d) after materialization
MATCH (n:owl__Class)<-[d:rdfs__range]-(:owl__ObjectProperty)<-[:rdfs__subPropertyOf*0..]-(op:owl__ObjectProperty)<-[:owl__onProperty]-(res:owl__Restriction)
WITH n, op, res, d,
     last(split(last(split(properties(op).uri, "#")), "/")) AS relType
MATCH (res)<-[:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(des, relType, properties(op), n)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='range'
DELETE d
'''
range_onProperty_datatype = '''
// Materialize DatatypeProperty range semantics via Restriction + subPropertyOf chain:
// - Find node n that is the rdfs:range of some DatatypeProperty (or its super-properties)
// - Find restriction res that uses op (or sub-property) via owl:onProperty
// - Find source class des such that des rdfs:subClassOf res
// - Create des -[:<relType>]-> n where relType comes from op.uri (supports both '/' and '#')
// - Delete rdfs:range edge (d) after materialization
MATCH (n)<-[d:rdfs__range]-(:owl__DatatypeProperty)<-[:rdfs__subPropertyOf*0..]-(op:owl__DatatypeProperty)<-[:owl__onProperty]-(res:owl__Restriction)
WITH n, op, res, d,
     last(split(last(split(properties(op).uri, "#")), "/")) AS relType
MATCH (res)<-[:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(des, relType, properties(op), n)
YIELD rel
SET rel.property_type='owl__DatatypeProperty', rel.inferred_by='range'
DELETE d
'''



union_of_datatype = '''
// Collapse owl:unionOf RDF list into an ordered array property on the equivalent datatype node
MATCH (dt:rdfs__Datatype)-[ui:owl__unionOf]->(rs)
MATCH (ddt:rdfs__Datatype)-[eq:owl__equivalentClass]->(dt)
WITH ddt, eq, ui, rs
// Enumerate RDF list cells in order via rdf__rest chain
MATCH p=(rs)-[:rdf__rest*0..]->(cell)
MATCH (cell)-[:rdf__first]->(xsdtp:rdfs__Datatype)
WITH ddt, eq, ui, length(p) AS idx, xsdtp
ORDER BY idx
WITH ddt, eq, ui, collect(xsdtp.rdfs__label) AS xsdtp_collection
SET ddt.owl__unionOf = xsdtp_collection
DELETE eq, ui
'''

union_of_class = '''
// Materialize owl:unionOf class expressions as direct relationships:
// - sub: subject class
// - mid1: intermediate class-expression node connected from sub via [r]
// - mid1 -[:owl__unionOf]-> rs (RDF list head)
// - list items are member classes
// - create sub -[:type(r)]-> member for each member
// - tag inferred relationship, then remove union scaffolding (relationships + intermediate node)
MATCH (sub:owl__Class)-[r]->(mid1:owl__Class)-[u:owl__unionOf]->(rs)
WITH sub, r, mid1, u, rs, type(r) AS relType

// Traverse full RDF list (includes first element via *0..)
MATCH (rs)-[:rdf__rest*0..]->(cell)
MATCH (cell)-[:rdf__first]->(obj:owl__Class)
WITH sub, relType, mid1, u, r, collect(DISTINCT obj) AS members

// Create relationships to each union member
UNWIND members AS obj
CALL apoc.create.relationship(sub, relType, {}, obj) YIELD rel
SET rel.owl__objectProperty = 'rdf__unionOf'

WITH mid1, u, r
// Clean up union scaffolding edges and the intermediate node
DELETE u, r
WITH mid1
// Only delete mid1 after its edges are removed
DETACH DELETE mid1
'''

oneOf = '''
// Create 'oneOf' relationships from a class to each enumeration member inferred from owl:oneOf + owl:equivalentClass
MATCH (cls:owl__Class)-[eq:owl__equivalentClass]->(mc:owl__Class)-[o1f:owl__oneOf]->(rs)

// Traverse RDF list: rs --(rdf__rest*)--> cell, cell --(rdf__first)--> member
MATCH (rs)-[:rdf__rest*0..]->(cell)
MATCH (cell)-[:rdf__first]->(member)

WITH cls, eq, o1f, collect(DISTINCT member) AS members
UNWIND members AS member
CALL apoc.create.relationship(cls, 'oneOf', {}, member) YIELD rel
SET rel.inferred_by = 'oneOf'

WITH eq, o1f
DELETE o1f, eq
'''

# Remove duplicate relationships between the same pair of nodes by keeping only the first one (using uri as grouping key)
del_dup_rels = '''
MATCH (a)-[r]->(b)
//WITH a, b, type(r) AS relType, properties(r) AS relProps, COLLECT(r) AS rels
WITH a, b, type(r) AS relType, r.uri AS relProps, COLLECT(r) AS rels
WHERE SIZE(rels) > 1
FOREACH (r IN rels[1..] | DELETE r)
'''
# Remove duplicate owl:Class nodes with the same uri, keeping a single representative and deleting the rest
del_dup_class = '''
MATCH (a:owl__Class) 
with a.uri as clsuri, collect(a) as dupclass 
WHERE size(dupclass) > 1 
FOREACH (dup in dupclass[1..] | DETACH DELETE dup)
'''
# Normalize XSD datatype nodes: relabel Resources under the XMLSchema namespace as xsd__* and rdfs__Datatype
xsd_datatypes = '''
MATCH (n:Resource)
WHERE n.uri STARTS WITH 'http://www.w3.org/2001/XMLSchema#'
WITH n, substring(n.uri, size('http://www.w3.org/2001/XMLSchema#')) AS localName
SET n:rdfs__Datatype
SET n.rdfs__label = 'xsd__' + localName
SET n.xsd_local_name = localName
REMOVE n:Resource
'''

# Remove redundant :Resource label from core OWL schema elements (Class, ObjectProperty, DatatypeProperty, etc.)
rm_redounded_label='''
match (n:owl__Class|owl__ObjectProperty|owl__DatatypeProperty|owl__AnnotationProperty|owl__FunctionalProperty|owl__TransitiveProperty)
remove n:Resource
'''
crt_sameAs_rel = """
MATCH (a:owl__Class)
WHERE a.rdfs__label IS NOT NULL AND trim(a.rdfs__label) <> ''
WITH a.rdfs__label AS cls_label, a
ORDER BY cls_label, a.uri
WITH cls_label, collect(a) AS dupclass
WHERE size(dupclass) > 1
WITH dupclass[0] AS base, dupclass
UNWIND dupclass AS dup
WITH base, dup
WHERE dup <> base
MERGE (dup)-[:sameAs]->(base)
"""
