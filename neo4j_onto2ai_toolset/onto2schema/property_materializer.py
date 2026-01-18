from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import Neo4jDatabase
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger

def materialize_properties(db: Neo4jDatabase, property_meta_type: str):
    """
    Generic function to materialize OWL properties (Object or Datatype) as native Neo4j relationships.
    property_meta_type: 'owl__ObjectProperty' or 'owl__DatatypeProperty'
    """
    is_object_prop = (property_meta_type == 'owl__ObjectProperty')
    prop_label = "ObjectProperty" if is_object_prop else "DatatypeProperty"
    
    # Common Cardinality and Requirement calculation block
    CARDINALITY_LOGIC = """
         CASE 
           WHEN res.owl__cardinality IS NOT NULL THEN toString(res.owl__cardinality)
           WHEN res.owl__qualifiedCardinality IS NOT NULL THEN toString(res.owl__qualifiedCardinality)
           WHEN res.owl__minCardinality IS NOT NULL OR res.owl__maxCardinality IS NOT NULL OR res.owl__minQualifiedCardinality IS NOT NULL OR res.owl__maxQualifiedCardinality IS NOT NULL OR hasSome
           THEN 
             coalesce(toString(res.owl__minCardinality), toString(res.owl__minQualifiedCardinality), CASE WHEN hasSome THEN "1" ELSE "0" END) + 
             ".." + 
             coalesce(toString(res.owl__maxCardinality), toString(res.owl__maxQualifiedCardinality), 
                      CASE WHEN onp:owl__FunctionalProperty THEN "1" ELSE "*" END)
           ELSE 
             CASE WHEN onp:owl__FunctionalProperty THEN "0..1" ELSE "0..*" END
         END AS cardinality
    
    WITH n, relType, onp, res, targetNode, cardinality,
         CASE 
           WHEN cardinality = "1" THEN "Mandatory"
           WHEN cardinality STARTS WITH "0.." THEN "Optional"
           WHEN cardinality CONTAINS ".." THEN 
             CASE WHEN split(cardinality, "..")[0] = "0" THEN "Optional" ELSE "Mandatory" END
           WHEN cardinality = "0" THEN "Optional"
           ELSE "Mandatory" 
         END AS requirement
    """

    # 1. Materialize relationships from rdfs:domain and rdfs:range
    domain_range_query = f"""
    MATCH (n:owl__Class)<-[d:rdfs__domain]-(op:{property_meta_type})-[r:rdfs__range]->(c:Resource)
    WITH n, op, c, d, r,
         last(split(last(split(op.uri, '#')), '/')) AS relType
    WITH n, relType, op, c, d, r,
         CASE WHEN op:owl__FunctionalProperty THEN "0..1" ELSE "0..*" END AS cardinality
    WITH n, relType, op, c, d, r, cardinality,
         CASE WHEN cardinality STARTS WITH "0" THEN "Optional" ELSE "Mandatory" END AS requirement
    CALL apoc.merge.relationship(n, relType, {{uri: op.uri}}, {{}}, c, {{}})
    YIELD rel
    SET rel += properties(op),
        rel.inferred = true,
        rel.cardinality = cardinality,
        rel.requirement = requirement,
        rel.materialized = true,
        rel.property_type = '{property_meta_type}',
        rel.inferred_by = 'domain-range'
    DELETE d, r
    """

    # 2. Materialize relationships from OWL Restrictions
    restriction_query = f"""
    MATCH (n:owl__Class)-[:rdfs__subClassOf]->(res:owl__Restriction)-[:owl__onProperty]->(onp:{property_meta_type})
    OPTIONAL MATCH (res)-[:owl__someValuesFrom|owl__allValuesFrom|owl__onClass|owl__onDataRange]->(des:Resource)
    OPTIONAL MATCH (res)-[r_some:owl__someValuesFrom]->()

    WITH n, onp, des, res, r_some IS NOT NULL AS hasSome,
         last(split(last(split(onp.uri, '#')), '/')) AS relType
    
    WITH n, relType, onp, res, hasSome,
         coalesce(des, head([target IN [(onp)-[:rdfs__range]->(t) | t] | target])) AS targetNode
         
    WHERE targetNode IS NOT NULL OR des IS NOT NULL
    
    WITH n, relType, onp, res, targetNode, hasSome,
    {CARDINALITY_LOGIC}

    CALL apoc.merge.relationship(n, relType, {{uri: onp.uri}}, {{}}, targetNode, {{}})
    YIELD rel
    SET rel += properties(onp),
        rel.inferred = true,
        rel.cardinality = cardinality,
        rel.requirement = requirement,
        rel.materialized = true,
        rel.property_type = '{property_meta_type}',
        rel.inferred_by = 'restriction'
    
    WITH res
    SET res.materialized = true
    RETURN count(*)
    """

    db.execute_cypher(domain_range_query, name=f"materialize_{prop_label}_domain_range")
    db.execute_cypher(restriction_query, name=f"materialize_{prop_label}_restrictions")

    db.execute_cypher(domain_range_query, name=f"materialize_{prop_label}_domain_range")
    db.execute_cypher(restriction_query, name=f"materialize_{prop_label}_restrictions")

def cleanup_duplicate_relationships(db: Neo4jDatabase):
    """
    Remove duplicate relationships between nodes where the URI and type are identical,
    focusing only on materialized relationships.
    """
    cleanup_query = """
    MATCH (a)-[r {materialized: true}]->(b)
    WITH a, b, type(r) AS relType, r.uri AS relUri, COLLECT(r) AS rels
    WHERE size(rels) > 1
    UNWIND rels[1..] AS toDelete
    DELETE toDelete
    RETURN count(toDelete) AS deletedCount
    """
    results = db.execute_cypher(cleanup_query, name="cleanup_duplicate_relationships")
    deleted_count = 0
    if results:
        deleted_count = results[0].get('deletedCount', 0)
    logger.info(f"Cleanup finished. Deleted {deleted_count} duplicate relationships.")

if __name__ == "__main__":
    from neo4j_onto2ai_toolset.onto2ai_tool_config import semanticdb
    materialize_properties(semanticdb, 'owl__ObjectProperty')
    materialize_properties(semanticdb, 'owl__DatatypeProperty')
    cleanup_duplicate_relationships(semanticdb)
