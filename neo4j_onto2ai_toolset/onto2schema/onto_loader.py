# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
import urllib
import logging

from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import clean_up_neo4j_graph, rdf_to_neo4j_graph, SemanticGraphDB
from neo4j_onto2ai_toolset.onto2schema.sparql_statement import query4dataprop
from neo4j_onto2ai_toolset.onto2schema.base_functions import get_rdf_data
from rdf_statement import *
from neo4j_onto2ai_toolset.onto2ai_tool_config import *

logger = logging.getLogger(__name__)

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
        logger.error("Ontology file not found", extra={"uri": uri})
    except urllib.error.HTTPError as e:
        logger.error("HTTP error while loading ontology", extra={"uri": uri, "error": str(e)})
    except BadSyntax as e:
        logger.error("Bad syntax in ontology file", extra={"uri": uri, "error": str(e)})
    except Exception as e:
        logger.exception("Unexpected error while loading ontology", extra={"uri": uri})




# file_path = 'http://www.w3.org/2004/02/skos/core/skos/'
# format="ttl"
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/FunctionalEntities.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/ClientsAndAccounts.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/CodesAndCodeSets.rdf'
# file_path = 'https://www.omg.org/spec/Commons/Designators/'
# file_path =  'https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LEIEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/FormalBusinessOrganizations/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LegalPersons/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/MetadataBELegalEntities/LegalEntitiesModule'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/NorthAmericanEntities/USExampleEntities/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/'
file_path ='https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/NorthAmericanJurisdiction/CAGovernmentEntitiesAndJurisdictions/'
format = "application/rdf+xml"

# Create the RDF Graph, parse & ingest the data to Neo4j, and close the store(If the field batching is set to True in the Neo4jStoreConfig, remember to close the store to prevent the loss of any uncommitted records.)
neo4j_aura = Graph(store=Neo4jStore(config=config))

neo4j_model = get_neo4j_model_config()

# clean up before loading
db = SemanticGraphDB(neo4j_model.url ,neo4j_model.username,neo4j_model.password,neo4j_model.database)

clean_up_neo4j_graph(db)

# Calling the parse method will implictly open the store
# neo4j_aura.parse(file_path, format=format)
g = Graph()
load_ontology(g, file_path, format)

for url in already_loaded:
    rdfdata = get_rdf_data(url)
    neo4j_aura.parse(data=rdfdata, format=format)

from rdflib.plugins.sparql import prepareQuery


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
# convert owl to neo4j model
rdf_to_neo4j_graph(db)

db.close()
