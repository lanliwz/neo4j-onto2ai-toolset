# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
from rdflib import Graph, Namespace, OWL
import logging
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from neo4j_onto2ai_toolset.onto2schema.onto_db_initializer import reset_neo4j_db
from neo4j_onto2ai_toolset.onto2schema.onto_materializer import materialize_onto_db
from neo4j_onto2ai_toolset.onto2schema.property_materializer import *
from neo4j_onto2ai_toolset.onto2schema.sparql_statement import query4dataprop
from neo4j_onto2ai_toolset.onto2schema.base_functions import get_rdf_data
from neo4j_onto2ai_toolset.onto2schema.rdf_statement import *
from neo4j_onto2ai_toolset.onto2ai_tool_config import *
from neo4j_onto2ai_toolset.onto2schema.prefixes import PREFIXES_CANON as prefixes
from rdflib.plugins.sparql import prepareQuery

# Use the application logger so messages follow the same handlers/formatters as the rest of the tool.
logger = logging.getLogger("onto2ai-toolset")

DCTERMS = Namespace("http://purl.org/dc/terms/")

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

    logger.info(f"Load ontology {uri_str}")

    imported_onto_set.add(uri_str)

    try:
        rdfdata = get_rdf_data(uri_str)
    except Exception as e:
        logger.warning(f"Failed to fetch RDF data for {uri_str}: {e}")
        return

    formats_to_try = [format] if format else [None, "application/rdf+xml", "xml", "turtle", "n3", "json-ld"]
    
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
        logger.warning(f"Failed to parse ontology {uri_str}: {last_err}")
        return

    # recurse imports (normalize to str)
    for _, _, imported_uri in graph.triples((None, OWL.imports, None)):
        load_ontology_with_imports(graph, str(imported_uri), format=format)

def discover_and_load_parts(graph: Graph, root_uri, format=None):
    """
    Loads an ontology and then discovers all components linked via dcterms:hasPart.
    This is useful for FIBO 'Domain' or 'Specification' ontologies.
    """
    logger.info(f"Starting discovery from {root_uri}")
    load_ontology_with_imports(graph, root_uri, format)
    
    # Discovery loop: keep finding new parts until no more are found
    new_parts_found = True
    while new_parts_found:
        new_parts_found = False
        parts = set()
        # Find all dcterms:hasPart targets in the current graph
        for _, _, part in graph.triples((None, DCTERMS.hasPart, None)):
            part_uri = str(part)
            if part_uri not in imported_onto_set:
                parts.add(part_uri)
        
        if parts:
            logger.info(f"Discovered {len(parts)} new parts to load")
            new_parts_found = True
            for part_uri in parts:
                load_ontology_with_imports(graph, part_uri, format)


def load_neo4j_db(onto_uri: str, format: str, discover: bool = False) -> None:
    # In-memory RDF graph for discovery & SPARQL
    discovery_graph = Graph()
    if discover:
        discover_and_load_parts(discovery_graph, onto_uri, format)
    else:
        load_ontology_with_imports(discovery_graph, onto_uri, format)
    
    # Now sync the discovered model to Neo4j
    neo4j_rdf_graph = Graph(store=Neo4jStore(config=config))
    for triple in discovery_graph:
        neo4j_rdf_graph.add(triple)
    neo4j_rdf_graph.close(True)

def load_neo4j_db_ext(sparQl, in_mem_graph,neo4j_graph):
    # Prepare the query
    query = prepareQuery(sparQl, initNs=dict(in_mem_graph.namespaces()))
    logger.info("RDF query prepared", extra={"op": "sparql_prepare", "query": sparQl})

    # Execute the query and retrieve results
    for row in in_mem_graph.query(query):
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
    # TOP SPEC
    FIBO_SPEC = "https://spec.edmcouncil.org/fibo/ontology/MetadataFIBO/FIBOSpecification"
    
    # DOMAINS
    FND_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/FND/MetadataFND/FNDDomain"
    BE_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/BE/MetadataBE/BEDomain"
    BP_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/BP/MetadataBP/BPDomain"
    FBC_DOMAIN = "https://spec.edmcouncil.org/fibo/ontology/FBC/MetadataFBC/FBCDomain"

    # --- USER SELECTION ---
    # Set discover=True to recursively find all modules/ontologies in a domain or spec
    selection = [FND_DOMAIN,BE_DOMAIN]
    discover_mode = True 
    # ----------------------

    rdf_format = "application/rdf+xml"

    reset_neo4j_db()
    for uri in selection:
        load_neo4j_db(uri, rdf_format, discover=discover_mode)
    
    materialize_properties(semanticdb, 'owl__ObjectProperty')
    materialize_properties(semanticdb, 'owl__DatatypeProperty')
    cleanup_duplicate_relationships(semanticdb)
