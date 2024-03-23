# pip install /Users/weizhang/github/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
from rdflib_neo4j import Neo4jStoreConfig, Neo4jStore, HANDLE_VOCAB_URI_STRATEGY
from rdflib import Graph
import os

from rdflib.namespace import RDF, RDFS, OWL, SKOS, DC, DCTERMS

# AnnotationProperty
# OWL.AnnotationProperty

# most popular annotation properties
POPULAR_ANNOTATION_PREDICATE = {
    RDFS.label,
    RDFS.comment,
    SKOS.definition,
    SKOS.prefLabel,
    SKOS.altLabel,
    SKOS.example,
    SKOS.note,
    SKOS.notation,
    SKOS.scopeNote,
    # part of a broader metadata standard often used in digital libraries and archives.
    DC.title,
    DC.description,
    OWL.versionInfo,
    OWL.deprecated}

CLASS_AXIOMS = {
    RDFS.subClassOf,
    OWL.equivalentClass,
    OWL.disjointWith,
    OWL.disjointUnionOf,
    OWL.intersectionOf,
    OWL.unionOf,

}
PROPERTY_AXIOMS = {
    OWL.FunctionalProperty,
    OWL.TransitiveProperty,
    OWL.SymmetricProperty,
    OWL.AsymmetricProperty,
    OWL.TransitiveProperty
}
INDIVIDUAL_AXIOMS = {
    OWL.NamedIndividual
}


# set the configuration to connect to your Aura DB
url = os.getenv("Neo4jFinDBUrl")
username = os.getenv("Neo4jFinDBUserName")
password = os.getenv("Neo4jFinDBPassword")
database = os.getenv("Neo4jFinDBName")

auth_data = {'uri': url,
             'database': "neo4j",
             'user': username,
             'pwd': password}
prefixes = {'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'xml': 'http://www.w3.org/XML/1998/namespace',
            'cmns-av': 'https://www.omg.org/spec/Commons/AnnotationVocabulary/',
            'cmns-cds': 'https://www.omg.org/spec/Commons/CodesAndCodeSets/',
            'cmns-cls': 'https://www.omg.org/spec/Commons/Classifiers/',
            'cmns-dsg': 'https://www.omg.org/spec/Commons/Designators/',
            'cmns-id': 'https://www.omg.org/spec/Commons/Identifiers/',
            'dcterms': 'http://purl.org/dc/terms/',
            'fibo-be-fct-fct': 'https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/',
            'fibo-be-le-fbo': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/FormalBusinessOrganizations/',
            'fibo-fnd-arr-cls': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/ClassificationSchemes/',
            'fibo-fnd-org-fm': 'https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/',
            'fibo-fnd-org-org': 'https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/',
            'fibo-fnd-pas-pas': 'https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/',
            'fibo-fnd-pty-pty': 'https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/',
            'fibo-fnd-pty-rl': 'https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Roles/',
            'fibo-fnd-rel-rel': 'https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/',
            'fibo-fnd-utl-av': 'https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/',
            'skos': 'http://www.w3.org/2004/02/skos/core#',
            'cmns-qtu': 'https://www.omg.org/spec/Commons/QuantitiesAndUnits/',
            'fibo-be-le-lp': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/',
            'fibo-fnd-aap-ppl': 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/',
            'fibo-fnd-acc-aeq': 'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/AccountingEquity/',
            'fibo-fnd-agr-ctr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/',
            'fibo-fnd-gao-obj': 'https://spec.edmcouncil.org/fibo/ontology/FND/GoalsAndObjectives/Objectives/',
            'fibo-fnd-plc-adr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/',
            'cmns-cxtdsg': 'https://www.omg.org/spec/Commons/ContextualDesignators/',
            'cmns-dt': 'https://www.omg.org/spec/Commons/DatesAndTimes/',
            'fibo-fnd-agr-agr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Agreements/',
            'fibo-fnd-law-jur': 'https://spec.edmcouncil.org/fibo/ontology/FND/Law/Jurisdiction/',
            'fibo-fnd-law-lcap': 'https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCapacity/',
            'fibo-fnd-arr-arr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Arrangements/',
            'cmns-col': 'https://www.omg.org/spec/Commons/Collections/',
            'fibo-fnd-aap-agt': 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/',
            'lcc-cr': 'https://www.omg.org/spec/LCC/Countries/CountryRepresentation/',
            'fibo-fnd-dt-bd': 'https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/',
            'cmns-doc': 'https://www.omg.org/spec/Commons/Documents/',
            'fibo-fnd-acc-cur': 'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/',
            'fibo-fnd-dt-oc': 'https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/',
            'fibo-fnd-plc-fac': 'https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/',
            'fibo-fnd-plc-loc': 'https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/',
            'cmns-txt': 'https://www.omg.org/spec/Commons/TextDatatype/',
            'fibo-fnd-oac-own': 'https://spec.edmcouncil.org/fibo/ontology/FND/OwnershipAndControl/Ownership/',
            'fibo-fnd-arr-doc': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/',
            'fibo-fnd-dt-fd': 'https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/FinancialDates/',
            'fibo-fnd-arr-id': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/IdentifiersAndIndices/',
            'fibo-fnd-law-cor': 'https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCore/',
            'sm': 'http://www.omg.org/techprocess/ab/SpecificationMetadata/',
            'lcc-lr': 'https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/',
            'cmns-cxtid': 'https://www.omg.org/spec/Commons/ContextualIdentifiers/',
            'fibo-fnd-utl-alx': 'https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/Analytics/',
            'fibo-be-le-lei': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/'}
# Define your custom mappings & store config
config = Neo4jStoreConfig(auth_data=auth_data,
                          custom_prefixes=prefixes,
                          handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.SHORTEN,
                          batching=True)
already_loaded = set()
def load_ontology(graph:Graph, uri, format):
    """
    Recursively load an ontology and all its imports into a graph.
    :param graph: An rdflib.Graph instance.
    :param uri: URI of the ontology to load.
    """
    if uri not in already_loaded:
        print(f"Loading: {uri}")
        graph.parse(uri,format=format)
        already_loaded.add(uri)

        # Find all import statements in the currently loaded ontology.
        for _, _, imported_uri in graph.triples((None, OWL.imports, None)):
            load_ontology(graph, imported_uri, format)

# file_path = 'https://github.com/jbarrasa/gc-2022/raw/main/search/onto/concept-scheme-skos.ttl'
# format="ttl"
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/FunctionalEntities.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/ClientsAndAccounts.rdf'
# file_path = '/Users/weizhang/Downloads/ontology-fibo-rdf/CodesAndCodeSets.rdf'
# file_path = 'https://www.omg.org/spec/Commons/Designators/'
# file_path =  'https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/'
file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LEIEntities/'
# file_path = 'https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/FormalBusinessOrganizations/'
# file_path ='https://spec.edmcouncil.org/fibo/ontology/master/latest/BE/LegalEntities/LegalPersons/'
format="application/rdf+xml"

# Create the RDF Graph, parse & ingest the data to Neo4j, and close the store(If the field batching is set to True in the Neo4jStoreConfig, remember to close the store to prevent the loss of any uncommitted records.)
neo4j_aura = Graph(store=Neo4jStore(config=config))
# Calling the parse method will implictly open the store
# neo4j_aura.parse(file_path, format=format)
g = Graph()
load_ontology(g,file_path,format)

for url in already_loaded:
    neo4j_aura.parse(url, format=format)

neo4j_aura.close(True)