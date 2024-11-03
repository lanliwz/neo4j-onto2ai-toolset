from neo4j import GraphDatabase


# The SematicGraphDB class is used to interact with a Neo4j database.
# It provides methods to create nodes, relationships, and execute arbitrary Cypher queries.
class SemanticGraphDB:
    # Initialize the FinGraphDB with the connection details to the Neo4j database.
    def __init__(self, uri, user, password, database_name):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), database=database_name)

    # Close the connection to the Neo4j database.
    def close(self):
        self._driver.close()

    # Create a node with the given label and properties.
    def create_node(self, label, properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node, label, properties)

    # Execute an arbitrary Cypher query.
    def execute_cypher(self, query):
        with self._driver.session() as session:
            session.execute_write(self._execute_cypher, query)

    # Helper method to create a node.
    @staticmethod
    def _create_node(tx, label, properties):
        query = f"CREATE (a:{label} {{properties}})"
        tx.run(query, properties=properties)

    # Helper method to execute a Cypher query.
    @staticmethod
    def _execute_cypher(tx, query):
        tx.run(query)

    # Create a node and a relationship between it and another node.
    def create_node_and_relationship(self, node1_label, node1_properties, relationship_type, node2_label,
                                     node2_properties):
        with self._driver.session() as session:
            session.execute_write(self._create_node_rel, node1_label, node1_properties, relationship_type, node2_label,
                                  node2_properties)

    # Helper method to create a node and a relationship.
    @staticmethod
    def _create_node_rel(tx, node1_label, node1_properties, relationship_type, node2_label, node2_properties):
        query = (
            f"CREATE (a:{node1_label} {{properties1}}) "
            f"-[:{relationship_type}]-> "
            f"(b:{node2_label} {{properties2}})"
        )
        tx.run(query, properties1=node1_properties, properties2=node2_properties)


restrict_cardinality = '''
// Cardinality key/value
MATCH (res:owl__Restriction)
WITH res, [key IN keys(res) 
WHERE key CONTAINS 'Cardinality'] AS cardinalityKeys 
WHERE  res[head(cardinalityKeys)] is not null 
RETURN res,head(cardinalityKeys), res[head(cardinalityKeys)]
'''


allValuesFrom = '''
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

domain_range = '''
//CREATE REL domain-range 
match (n:owl__Class)<-[d:rdfs__domain]-(op:owl__ObjectProperty)-[r:rdfs__range]->(c:owl__Class) 
WITH n,op,c,d,r
CALL apoc.create.relationship(n, last(split(properties(op).uri,"/")), properties(op), c)
YIELD rel
SET rel.property_type='owl__ObjectProperty', rel.inferred_by='domain-range'
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
MATCH (n)-[r]->(m)
WITH n,m,COUNT(r) AS relCount,COLLECT(r) as rels
WHERE relCount > 1
WITH n,m,rels
FOREACH (r IN rels[1..] | DELETE r)
'''
# convert xsd datatypes
xsd_datatypes = '''
MATCH (n:Resource)
WHERE n.uri STARTS WITH 'http://www.w3.org/2001/XMLSchema#'
WITH n, substring(n.uri, size('http://www.w3.org/2001/XMLSchema#')) AS extractedString
CALL {
    WITH n, extractedString
    CALL apoc.create.addLabels(n, ['xsd__'+extractedString]) YIELD node
    RETURN node
}
with n
remove n:Resource
'''
# remove Resource label for owl__Class
rm_redounded_label='''
match (n:owl__Class|owl__ObjectProperty|owl__DatatypeProperty|owl__AnnotationProperty|owl__FunctionalProperty|owl__TransitiveProperty)
remove n:Resource
'''