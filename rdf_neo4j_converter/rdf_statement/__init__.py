from rdflib.namespace import RDFS, OWL, SKOS, DC, RDF

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
            'fibo-be-le-lei': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/',
            'fibo-be-corp-corp' : 'https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/',
            'fibo-be-le-cb' : 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/',
            'fibo-be-ge-ge' : 'https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/'}