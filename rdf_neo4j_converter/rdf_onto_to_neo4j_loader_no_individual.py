# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
import os
import urllib

from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from rdf_neo4j_converter.utility import get_rdf_data
from rdf_statement import *

neo4j_bolt_url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
neo4j_db_name = 'rdf'

auth_data = {'uri': neo4j_bolt_url,
             'database': neo4j_db_name,
             'user': username,
             'pwd': password}

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


file_path ='https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LegalPersons/'

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


neo4j_aura.close(True)



