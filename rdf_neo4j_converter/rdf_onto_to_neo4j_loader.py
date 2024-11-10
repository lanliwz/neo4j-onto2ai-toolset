# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
import urllib

from rdflib import Graph,URIRef
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from neo4j_db import auth_data
from rdf_neo4j_converter.utility import get_rdf_data
from rdf_statement import *




# Define your custom mappings & store config


config = Neo4jStoreConfig(auth_data=auth_data,
                          custom_prefixes=prefixes,
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.SHORTEN,
                          batching=True)
already_loaded = set()


def load_ontology(graph: Graph, uri, format):
    """
    Recursively load an ontology and all its imports into a graph.
    :param format:
    :param graph: A rdflib.Graph instance.
    :param uri: URI of the ontology to load.
    """
    try:
        if uri in already_loaded:
            None
        else:
            print(f"Loading: {uri}")
            rdfdata = get_rdf_data(uri)
            graph.parse(data=rdfdata, format=format)
            already_loaded.add(uri)

            # Find all import statements in the currently loaded ontology.
            for _, _, imported_uri in graph.triples((None, OWL.imports, None)):
                load_ontology(graph, imported_uri, format)
    except FileNotFoundError:
        print(f"Error: The file at '{uri}' was not found.")
    except urllib.error.HTTPError as e:
        print(f"HTTP error encountered: {e}")
    except BadSyntax as e:
        print(f"Syntax error in the ontology file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")




# file_path = 'https://github.com/jbarrasa/gc-2022/raw/main/search/onto/concept-scheme-skos.ttl'
# format="ttl"
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/FunctionalEntities.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/ClientsAndAccounts.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/CodesAndCodeSets.rdf'
# file_path = 'https://www.omg.org/spec/Commons/Designators/'
# file_path =  'https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LEIEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/FormalBusinessOrganizations/'
file_path ='https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LegalPersons/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/MetadataBELegalEntities/LegalEntitiesModule'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/NorthAmericanEntities/USExampleEntities/'
format = "application/rdf+xml"

# Create the RDF Graph, parse & ingest the data to Neo4j, and close the store(If the field batching is set to True in the Neo4jStoreConfig, remember to close the store to prevent the loss of any uncommitted records.)
neo4j_aura = Graph(store=Neo4jStore(config=config))
# Calling the parse method will implictly open the store
# neo4j_aura.parse(file_path, format=format)
g = Graph()
load_ontology(g, file_path, format)

for url in already_loaded:
    rdfdata = get_rdf_data(url)
    neo4j_aura.parse(data=rdfdata, format=format)

from rdflib.plugins.sparql import prepareQuery

# load individuals
query4individuals = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?individual ?type
    WHERE {
        ?individual a ?type ;
            a owl:NamedIndividual .
        FILTER (?type != owl:NamedIndividual)    
    }
"""

# Prepare the query
query = prepareQuery(query4individuals, initNs=dict(g.namespaces()))

# Execute the query and retrieve results
results = g.query(query)

# Iterate over results and print named individuals and their types
for row in results:
    individual = row.individual
    type_class = row.type
    neo4j_aura.add((individual, RDF.type, type_class))
    print(f"Individual: {individual}, Type: {type_class}")

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

# Prepare the query
query = prepareQuery(query4dataprop, initNs=dict(g.namespaces()))

# Execute the query and retrieve results
results = g.query(query)

# Iterate over results and print named individuals and their types
for row in results:
    clz = row.clz
    type_class = row.datatype
    prop = row.property
    neo4j_aura.add((clz, prop, type_class))
    print(f"subj: {clz}, pred: {prop}, Type: {type_class}")

neo4j_aura.close(True)



