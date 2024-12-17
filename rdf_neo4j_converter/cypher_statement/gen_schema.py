del_all_node =  '''
MATCH (n) DETACH DELETE n
'''
del_all_relationship =  '''
MATCH ()-[n]-() DETACH DELETE n
'''
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
allValueFrom_01 = '''
match (cls:owl__Class)-[link]->(cls1:owl__Class) 
with cls,link,cls1 
match (cls)-[sub:rdfs__subClassOf]->(restriction)-[some:owl__allValuesFrom]->(cls1) 
SET link.inferred_by='allValuesFrom'
DELETE sub,some
DELETE restriction
'''
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
someValueFrom_01 = '''
match (cls:owl__Class)-[link]->(cls1:owl__Class) 
with cls,link,cls1 
match (cls)-[sub:rdfs__subClassOf]->(restriction)-[some:owl__someValuesFrom]->(cls1) 
SET link.inferred_by='someValuesFrom'
DELETE sub,some
DELETE restriction
'''
domain_range_1 = '''
//CREATE REL domain-range 
match (n:owl__Class)<-[d:rdfs__domain]-(op:owl__ObjectProperty)-[r:rdfs__range]->(c:owl__Class) 
WITH n,op,c,d,r
CALL apoc.create.relationship(n, last(split(properties(op).uri,"/")), properties(op), c)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='domain-range'
DELETE d,r
'''
domain_range_2 = '''
//CREATE REL domain-range 
match (n:owl__Class)<-[d:rdfs__domain]-(op:owl__DatatypeProperty)-[r:rdfs__range]->(c:Resource) 
WITH n,op,c,d,r
CALL apoc.create.relationship(n, last(split(properties(op).uri,"/")), properties(op), c)
YIELD rel
SET rel.property_type='owl__DatatypeProperty', rel.inferred_by='domain-range'
DELETE d,r
'''
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
union_of_datatype = '''
MATCH (dt:rdfs__Datatype)-[ui:owl__unionOf]->(rs)
MATCH path=(rs)-[:rdf__first|rdf__rest*1..]->(xsdtp:rdfs__Datatype)
WITH xsdtp, dt, rs,ui
MATCH (ddt:rdfs__Datatype)-[eq:owl__equivalentClass]->(dt)
with ddt, collect(xsdtp.rdfs__label) AS xsdtp_collection,eq,ui
set ddt.owl__unionOf = xsdtp_collection
DELETE eq,ui
'''
# WIP
union_of_class = '''
MATCH (sub:owl__Class)-[r]->(mid1:owl__Class)-[midr:owl__unionOf]->(mid)-[f:rdf__first]->(obj) 
with sub,obj,r,f
CALL apoc.create.relationship(sub, type(r), {}, obj) yield rel 
set rel.owl__objectProperty='rdf__unionOf'
DELETE f
'''

union_of_class_1 = '''
// CREATE REL unionOf
MATCH (sub:owl__Class)-[r]->(mid1:owl__Class)-[midr:owl__unionOf]->(mid)-[:rdf__rest]-()-[f:rdf__first]->(obj)
WITH sub, obj,  midr,mid1,r,type(r) AS relType,f
CALL apoc.create.relationship(sub, relType, {}, obj) yield rel 
set rel.owl__objectProperty='rdf__unionOf'
DELETE f,midr,r
DELETE mid1
'''

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
# delete duplicated hasFactor
del_dup_rels = '''
MATCH (a)-[r]->(b)
//WITH a, b, type(r) AS relType, properties(r) AS relProps, COLLECT(r) AS rels
WITH a, b, type(r) AS relType, r.uri AS relProps, COLLECT(r) AS rels
WHERE SIZE(rels) > 1
FOREACH (r IN rels[1..] | DELETE r)
'''
# convert xsd datatypes
xsd_datatypes = '''
MATCH (n:Resource)
WHERE n.uri STARTS WITH 'http://www.w3.org/2001/XMLSchema#'
WITH n, 'xsd__'+substring(n.uri, size('http://www.w3.org/2001/XMLSchema#')) AS extractedString
CALL {
    WITH n, extractedString
    CALL apoc.create.addLabels(n, [extractedString,'rdfs__Datatype']) YIELD node
    RETURN node
}
with n,extractedString
SET n.rdfs__label = extractedString
REMOVE n:Resource
'''
# remove Resource label for owl__Class
rm_redounded_label='''
match (n:owl__Class|owl__ObjectProperty|owl__DatatypeProperty|owl__AnnotationProperty|owl__FunctionalProperty|owl__TransitiveProperty)
remove n:Resource
'''