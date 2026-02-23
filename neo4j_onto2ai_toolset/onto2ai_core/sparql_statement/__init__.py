query4dataprop = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT DISTINCT ?clz ?property ?datatype
    WHERE {
      ?property rdfs:domain ?clz .
      ?property rdfs:range ?datatype .
      FILTER(STRSTARTS(STR(?datatype), STR(xsd:)))
    }
"""

# individuals and its owl__Class
query4individuals = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?individual ?type
    WHERE {
        ?individual a ?type ;
            a owl:NamedIndividual .
        FILTER (?type != owl:NamedIndividual)    
    }
"""