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
//CREATE REL domain-onProperty Restriction 
match (n:owl__Class)<-[d:rdfs__domain]-(op:owl__ObjectProperty)<-[onp:owl__onProperty]-(res:owl__Restriction) 
WITH n,op,res,d
MATCH (res)<-[sub:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(n, last(split(properties(op).uri,"/")), properties(op), des)
YIELD rel
SET rel.property_type='owl__ObjectProperty',rel.inferred_by='domain'
DELETE d
'''
# Create relationships from restriction source classes to range classes via owl:onProperty + rdfs:range (object properties)
range_onProperty = '''
//CREATE REL range-onProperty Restriction 
match (n:owl__Class)<-[d:rdfs__range]-(op:owl__ObjectProperty)<-[onp:owl__onProperty]-(res:owl__Restriction) 
WITH n,op,res,d
MATCH (res)<-[sub:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(des, last(split(properties(op).uri,"/")), properties(op), n)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='range'
DELETE d
'''
# Handle datatype properties with a domain but no explicit range by creating an 'undefined' rdfs:Datatype node and re-wiring
data_property_without_range = '''
//  data property with domain without range
MATCH (prop:owl__DatatypeProperty)-[:rdfs__domain]->(cls:owl__Class) 
WHERE 
NOT (prop)-[:rdfs__range]-()
WITH prop,cls
CREATE (n:rdfs__Datatype) 
SET n.rdfs__label='undefined'
WITH cls,prop,n
CALL apoc.create.relationship(cls, last(split(properties(prop).uri,"/")),properties(prop), n)
YIELD rel
WITH cls,rel,n,prop
MATCH (prop)-[r]-()
DELETE r
DELETE prop
'''
# Handle object properties with a domain but no explicit range by creating an 'undefined' owl:Class node and re-wiring
object_property_without_range = '''
//  object property with domain without range
MATCH (prop:owl__ObjectProperty)-[:rdfs__domain]->(cls:owl__Class) 
WHERE 
NOT (prop)-[:rdfs__range]-()
WITH prop,cls
CREATE (n:owl__Class) 
SET n.rdfs__label='undefined'
WITH cls,prop,n
CALL apoc.create.relationship(cls, last(split(properties(prop).uri,"/")),properties(prop), n)
YIELD rel
WITH cls,rel,n,prop
MATCH (prop)-[r]-()
DELETE r
DELETE prop
'''
# Create relationships from classes to datatype nodes via owl:onDataRange restrictions and tag them with inferred_by='owl__onDataRange'
range_onProperty_datarange = '''
MATCH (n:owl__Class)-[:rdfs__subClassOf]->(res:owl__Restriction)-[d:owl__onDataRange]-(dtype) 
with n,res,dtype,d 
MATCH (res)-[:owl__onProperty]->(prop) 
with n,res,dtype,prop,d 
CALL apoc.create.relationship(n, last(split(properties(prop).uri,"/")), properties(prop), dtype)
YIELD rel
SET rel.property_type=prop.rdfs__label, rel.inferred_by='owl__onDataRange'
DELETE d
'''
# Create relationships from restriction source classes to range classes via owl:onProperty + rdfs:range (object properties, including subPropertyOf chains)
range_onProperty_object = '''
//CREATE REL range-onProperty Restriction 
match (n:owl__Class)<-[d:rdfs__range]-(:owl__ObjectProperty)<-[:rdfs__subPropertyOf*0..]-(op:owl__ObjectProperty)<-[onp:owl__onProperty]-(res:owl__Restriction) 
WITH n,op,res,d
MATCH (res)<-[sub:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(des, last(split(properties(op).uri,"/")), properties(op), n)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='range'
DELETE d
'''
# Create relationships from restriction source classes to range nodes via owl:onProperty + rdfs:range (datatype properties, including subPropertyOf chains)
range_onProperty_datatype = '''
//CREATE REL range-onProperty Restriction 
match (n)<-[d:rdfs__range]-(:owl__DatatypeProperty)<-[:rdfs__subPropertyOf*0..]-(op:owl__DatatypeProperty)<-[onp:owl__onProperty]-(res:owl__Restriction) 
WITH n,op,res,d
MATCH (res)<-[sub:rdfs__subClassOf]->(des:owl__Class)
WHERE n <> des
CALL apoc.create.relationship(des, last(split(properties(op).uri,"/")), properties(op), n)
YIELD rel
SET rel.property_type='owl__DatatypeProperty', rel.inferred_by='range'
DELETE d
'''
# Collapse owl:unionOf lists of rdfs:Datatype into a unionOf array property on the equivalent datatype node
union_of_datatype = '''
MATCH (dt:rdfs__Datatype)-[ui:owl__unionOf]->(rs)
MATCH path=(rs)-[:rdf__first|rdf__rest*1..]->(xsdtp:rdfs__Datatype)
WITH xsdtp, dt, rs,ui
MATCH (ddt:rdfs__Datatype)-[eq:owl__equivalentClass]->(dt)
with ddt, collect(xsdtp.rdfs__label) AS xsdtp_collection,eq,ui
set ddt.owl__unionOf = xsdtp_collection
DELETE eq,ui
'''
# Prototype: create relationships for owl:unionOf class expressions from subject class to each member class (first element)
union_of_class = '''
MATCH (sub:owl__Class)-[r]->(mid1:owl__Class)-[midr:owl__unionOf]->(mid)-[f:rdf__first]->(obj) 
with sub,obj,r,f
CALL apoc.create.relationship(sub, type(r), {}, obj) yield rel 
set rel.owl__objectProperty='rdf__unionOf'
DELETE f
'''
# Create relationships for owl:unionOf class expressions from subject class to each member class and clean up intermediate union structure
union_of_class_1 = '''
// CREATE REL unionOf
MATCH (sub:owl__Class)-[r]->(mid1:owl__Class)-[midr:owl__unionOf]->(mid)-[:rdf__rest]-()-[f:rdf__first]->(obj)
WITH sub, obj,  midr,mid1,r,type(r) AS relType,f
CALL apoc.create.relationship(sub, relType, {}, obj) yield rel 
set rel.owl__objectProperty='rdf__unionOf'
DELETE f,midr,r
DELETE mid1
'''
# Create 'oneOf' relationships from a class to each enumeration instance inferred from owl:oneOf + owl:equivalentClass
oneOf = '''
//Create REL oneOf
MATCH (cls:owl__Class)-[eq:owl__equivalentClass]->(mc:owl__Class)-[o1f:owl__oneOf]->(subject)-[`:rdf__first|:rdf__rest`*1..5]->(object)
WITH cls,o1f,object,eq,mc
MATCH ()-[:rdf__first]->(object)
WITH cls,o1f,object,eq,mc
CALL apoc.create.relationship(cls, 'oneOf', null,object)
YIELD rel
SET rel.inferred_by='oneOf'
DELETE o1f
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
WITH n, 'xsd__' + substring(n.uri, size('http://www.w3.org/2001/XMLSchema#')) AS extractedString
CALL apoc.create.addLabels(n, [extractedString, 'rdfs__Datatype']) YIELD node
SET node.rdfs__label = extractedString
REMOVE node:Resource
'''
# Remove redundant :Resource label from core OWL schema elements (Class, ObjectProperty, DatatypeProperty, etc.)
rm_redounded_label='''
match (n:owl__Class|owl__ObjectProperty|owl__DatatypeProperty|owl__AnnotationProperty|owl__FunctionalProperty|owl__TransitiveProperty)
remove n:Resource
'''
# Create owl:sameAs-style relationships between duplicate owl:Class nodes sharing the same rdfs__label, linking dup to base
crt_sameAs_rel= """
MATCH (a:owl__Class) 
WITH a.rdfs__label AS clsuri, COLLECT(a) AS dupclass 
WHERE SIZE(dupclass) > 1 
UNWIND dupclass AS dup
WITH dupclass[0] AS base, dup 
WHERE dup <> base
MERGE (dup)-[:sameAs]->(base);
"""
