from rdflib import Graph, URIRef
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, OWL

file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LEIEntities/'
# Load RDF data into a graph
sg = Graph()
sg.parse(file_path, format="xml")  # Load RDF data from file, adjust format if necessary

og = Graph()

# Define the SPARQL query
# only want to know the type of individual, not itself
query_str = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?individual ?type
    WHERE {
        ?individual a ?type ;
            a owl:NamedIndividual .
        FILTER (?type != owl:NamedIndividual)    
    }
"""

# Prepare the query
query = prepareQuery(query_str, initNs=dict(sg.namespaces()))

# Execute the query and retrieve results
results = sg.query(query)

# Iterate over results and print named individuals and their types
for row in results:
    individual = row.individual
    type_class = row.type
    # og.add((individual, RDF.type, type_class))
    print(f"Individual: {individual}, Type: {type_class}")
