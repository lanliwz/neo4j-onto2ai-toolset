from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import Neo4jDatabase

def materialize_properties_as_relationships(db: Neo4jDatabase):
    """
    Materializes OWL ObjectProperties as native Neo4j relationships.
    This creates relationship types between Classes and Instances based on:
    1. Direct rdfs:domain and rdfs:range definitions.
    2. OWL Restrictions (someValuesFrom, allValuesFrom).
    
    It resolves relationship types from the URI local name and handles blank nodes.
    """
    
    # 1. Materialize relationships from rdfs:domain and rdfs:range
    # This connects Classes directly.
    domain_range_query = """
    MATCH (n:owl__Class)<-[d:rdfs__domain]-(op:owl__ObjectProperty)-[r:rdfs__range]->(c:Resource)
    WITH n, op, c, d, r,
         // Extract local name from URI (handling # or /)
         last(split(last(split(op.uri, '#')), '/')) AS relType
    WITH n, relType, op, c, d, r
    CALL apoc.merge.relationship(n, relType, properties(op), {inferred: true, cardinality: '0..*', requirement: 'Optional'}, c, {})
    YIELD rel
    SET rel.property_type = 'owl__ObjectProperty', rel.inferred_by = 'domain-range'
    DELETE d, r
    """

    # 2. Materialize relationships from OWL Restrictions
    # This captures logic like "Payment involves PaymentAmount"
    restriction_query = """
    MATCH (n:owl__Class)-[:rdfs__subClassOf]->(res:owl__Restriction)-[:owl__onProperty]->(onp:owl__ObjectProperty)
    OPTIONAL MATCH (res)-[:owl__someValuesFrom|owl__allValuesFrom|owl__onClass]->(des:Resource)
    OPTIONAL MATCH (res)-[r_some:owl__someValuesFrom]->()

    WITH n, onp, des, res, r_some IS NOT NULL AS hasSome,
         last(split(last(split(onp.uri, '#')), '/')) AS relType
    
    // Resolve Target: if des is missing or a blank node, use a generic Resource/Class placeholder
    WITH n, relType, onp, res, hasSome,
         coalesce(des, 
                  head([target IN [(onp)-[:rdfs__range]->(t) | t] | target])
         ) AS targetNode
         
    WHERE targetNode IS NOT NULL OR des IS NOT NULL
    
    // Calculate Cardinality and Requirement
    WITH n, relType, onp, res, targetNode,
         CASE 
           WHEN res.owl__cardinality IS NOT NULL THEN toString(res.owl__cardinality)
           WHEN res.owl__qualifiedCardinality IS NOT NULL THEN toString(res.owl__qualifiedCardinality)
           WHEN res.owl__minCardinality IS NOT NULL OR res.owl__maxCardinality IS NOT NULL OR res.owl__minQualifiedCardinality IS NOT NULL OR res.owl__maxQualifiedCardinality IS NOT NULL OR hasSome
           THEN 
             coalesce(toString(res.owl__minCardinality), toString(res.owl__minQualifiedCardinality), CASE WHEN hasSome THEN "1" ELSE "0" END) + 
             ".." + 
             coalesce(toString(res.owl__maxCardinality), toString(res.owl__maxQualifiedCardinality), "*")
           ELSE "0..*"
         END AS cardinality
    
    WITH n, relType, onp, res, targetNode, cardinality,
         CASE 
           WHEN cardinality STARTS WITH "0.." THEN "Optional"
           WHEN cardinality CONTAINS ".." THEN 
             CASE WHEN split(cardinality, "..")[0] = "0" THEN "Optional" ELSE "Mandatory" END
           WHEN cardinality = "0" THEN "Optional"
           ELSE "Mandatory" 
         END AS requirement

    CALL (n, relType, onp, targetNode, cardinality, requirement) {
        CALL apoc.merge.relationship(n, relType, properties(onp), {inferred: true, cardinality: cardinality, requirement: requirement}, targetNode, {})
        YIELD rel
        SET rel.property_type = 'owl__ObjectProperty', rel.inferred_by = 'restriction'
        RETURN rel
    }
    
    // Cleanup and metadata tagging
    WITH n, onp, targetNode, res, relType
    SET res.materialized = true
    RETURN count(*)
    """

    db.execute_cypher(domain_range_query, name="materialize_domain_range")
    db.execute_cypher(restriction_query, name="materialize_restrictions")



# if __name__ == "__main__":
#     # Example usage (requires environment variables to be set)
#     from neo4j_onto2ai_toolset.onto2ai_tool_config import semanticdb
#     materialize_properties_as_relationships(semanticdb)
