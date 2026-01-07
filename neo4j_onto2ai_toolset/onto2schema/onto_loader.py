# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
import urllib
import logging

from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from neo4j_onto2ai_toolset.onto2schema.neo4j_utility import clean_up_neo4j_db
from neo4j_onto2ai_toolset.onto2schema.semantic_model_materializer import materialize_property_graph_model
from neo4j_onto2ai_toolset.onto2schema.sparql_statement import query4dataprop
from neo4j_onto2ai_toolset.onto2schema.base_functions import get_rdf_data
from rdf_statement import *
from neo4j_onto2ai_toolset.onto2ai_tool_config import *
from neo4j_onto2ai_toolset.onto2schema.prefixes import PREFIXES_CANON as prefixes
from rdflib.plugins.sparql import prepareQuery

# Use the application logger so messages follow the same handlers/formatters as the rest of the tool.
logger = logging.getLogger("onto2ai-toolset")

# Define your custom mappings & store config
config = Neo4jStoreConfig(auth_data=auth_data,
                          custom_prefixes=prefixes,
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.SHORTEN,
                          batching=True)
already_loaded = set()


def load_ontology_with_imports(graph: Graph, uri, format=None):
    uri_str = str(uri)

    # normalize dedupe
    if uri_str in already_loaded:
        return

    logger.info("Loading ontology", extra={"op": "load_ontology", "uri": uri_str})
    logger.debug("Ontology queued/loaded", extra={"op": "load_ontology", "uri": uri_str, "already_loaded_size": len(already_loaded)})
    already_loaded.add(uri_str)

    rdfdata = get_rdf_data(uri_str)

    # if you must keep `format`, at least add fallback
    formats_to_try = [format] if format else [None]
    if format:
        formats_to_try += ["xml", "turtle", "n3", "json-ld"]

    last_err = None
    for fmt in formats_to_try:
        try:
            if fmt is None:
                graph.parse(data=rdfdata)
            else:
                graph.parse(data=rdfdata, format=fmt)
            last_err = None
            break
        except Exception as e:
            last_err = e

    if last_err is not None:
        logger.exception(
            "Failed to parse ontology",
            extra={"op": "load_ontology", "uri": uri_str, "format": format},
        )
        raise last_err

    # recurse imports (normalize to str)
    for _, _, imported_uri in graph.triples((None, OWL.imports, None)):
         load_ontology_with_imports(graph, str(imported_uri), format=format)


def load_neo4j_db(graph, imports:set()):
    for url in imports:
        data = get_rdf_data(url)
        graph.parse(data=data, format=format)

def load_neo4j_db_ext(sparQl, in_mem_graph,neo4j_graph):
    # Prepare the query
    query = prepareQuery(sparQl, initNs=dict(in_mem_graph.namespaces()))
    logger.info(f"RDF query is {query4dataprop}")

    # Execute the query and retrieve results
    results = in_mem_graph.query(query)

    # Iterate over results and print named individuals and their types
    for row in results:
        clz = row.clz
        type_class = row.datatype
        prop = row.property
        neo4j_graph.add((clz, prop, type_class))
        logger.info(
            f"Datatype property discovered - {str(prop)}",
            extra={
                "op": "sparql_extract_datatype_property",
                "subject": str(clz),
                "predicate": str(prop),
                "datatype": str(type_class),
            },
        )
# file_path = 'http://www.w3.org/2004/02/skos/core/skos/'
# format="ttl"
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/FunctionalEntities.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/ClientsAndAccounts.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/CodesAndCodeSets.rdf'
# file_path = 'https://www.omg.org/spec/Commons/Designators/'
# file_path =  'https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LEIEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/ISO20275-CodeSet'
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

neo4j_model_db_config = get_neo4j_model_config()

# Operational Neo4j property graph
# Operational Neo4j property graph before loading new ontology
neo4j_model_db = SemanticGraphDB(
    neo4j_model_db_config.url,
    neo4j_model_db_config.username,
    neo4j_model_db_config.password,
    neo4j_model_db_config.database,
)
clean_up_neo4j_db(neo4j_model_db)

# In-memory RDF graph for reasoning & SPARQL
rdf_reasoning_graph = Graph()
load_ontology_with_imports(rdf_reasoning_graph, file_path, format)

# Neo4j-backed RDF staging graph
neo4j_rdf_graph = Graph(store=Neo4jStore(config=config))
load_neo4j_db(graph=neo4j_rdf_graph, imports=already_loaded)
# load_neo4j_db_ext(sparQl=query4dataprop,in_mem_graph=rdf_reasoning_graph,neo4j_graph=neo4j_rdf_graph)

# Materialize inferred OWL semantics into an operational Neo4j property graph
# (ObjectProperty/DataProperty relationships, domain/range, restrictions, cardinality, and remove duplicated things)
materialize_property_graph_model(neo4j_model_db)


neo4j_rdf_graph.close(True)
neo4j_model_db.close()
