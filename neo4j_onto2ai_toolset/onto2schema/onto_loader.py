# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
from rdflib import Graph
import logging
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from neo4j_onto2ai_toolset.onto2schema.onto_db_initializer import reset_neo4j_db
from neo4j_onto2ai_toolset.onto2schema.onto_materializer import materialize_onto_db
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
imported_onto_set = set()


def load_ontology_with_imports(graph: Graph, uri, format=None):
    uri_str = str(uri)

    # normalize dedupe
    if uri_str in imported_onto_set:
        return

    logger.info("Loading ontology", extra={"op": "load_ontology", "uri": uri_str})
    logger.debug(
        "Ontology load state",
        extra={
            "op": "load_ontology",
            "uri": uri_str,
            "already_loaded_size": len(imported_onto_set),
        },
    )
    imported_onto_set.add(uri_str)

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


def load_neo4j_db(onto_uri: str, format: str, imports: set[str]) -> None:
    # In-memory RDF graph for reasoning & SPARQL
    rdf_reasoning_graph = Graph()
    load_ontology_with_imports(rdf_reasoning_graph, onto_uri, format)
    neo4j_rdf_graph = Graph(store=Neo4jStore(config=config))
    for url in imports:
        data = get_rdf_data(url)
        neo4j_rdf_graph.parse(data=data, format=format)
    neo4j_rdf_graph.close(True)

def load_neo4j_db_ext(sparQl, in_mem_graph,neo4j_graph):
    # Prepare the query
    query = prepareQuery(sparQl, initNs=dict(in_mem_graph.namespaces()))
    logger.info("RDF query prepared", extra={"op": "sparql_prepare", "query": sparQl})

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



if __name__ == "__main__":
    onto_uri = (
        "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/"
        "NorthAmericanJurisdiction/CAGovernmentEntitiesAndJurisdictions/"
    )
    rdf_format = "application/rdf+xml"

    reset_neo4j_db()
    load_neo4j_db(onto_uri=onto_uri, format=rdf_format, imports=imported_onto_set)
    # load_neo4j_db_ext(sparQl=query4dataprop, in_mem_graph=rdf_reasoning_graph, neo4j_graph=neo4j_rdf_graph)
    materialize_onto_db()

