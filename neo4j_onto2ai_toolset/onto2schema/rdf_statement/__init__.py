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

# , - is replaced with _ since - is operator
prefixes = {'owl': 'http://www.w3.org/2002/07/owl#',
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'xml': 'http://www.w3.org/XML/1998/namespace',
            'cmns_av': 'https://www.omg.org/spec/Commons/AnnotationVocabulary/',
            'cmns_cds': 'https://www.omg.org/spec/Commons/CodesAndCodeSets/',
            'cmns_cls': 'https://www.omg.org/spec/Commons/Classifiers/',
            'cmns_dsg': 'https://www.omg.org/spec/Commons/Designators/',
            'cmns_id': 'https://www.omg.org/spec/Commons/Identifiers/',
            'dcterms': 'http://purl.org/dc/terms/',
            'fibo_be_fct_fct': 'https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/',
            'fibo_be_le_fbo': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/FormalBusinessOrganizations/',
            'fibo_fnd_arr_cls': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/ClassificationSchemes/',
            'fibo_fnd_org_fm': 'https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/',
            'fibo_fnd_org_org': 'https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/',
            'fibo_fnd_pas_pas': 'https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/',
            'fibo_fnd_pty_pty': 'https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/',
            'fibo_fnd_pty_rl': 'https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Roles/',
            'fibo_fnd_rel_rel': 'https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/',
            'fibo_fnd_utl_av': 'https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/',
            'skos': 'http://www.w3.org/2004/02/skos/core#',
            'cmns_qtu': 'https://www.omg.org/spec/Commons/QuantitiesAndUnits/',
            'fibo_be_le_lp': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/',
            'fibo_fnd_aap_ppl': 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/',
            'fibo_fnd_acc_aeq': 'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/AccountingEquity/',
            'fibo_fnd_agr_ctr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/',
            'fibo_fnd_gao_obj': 'https://spec.edmcouncil.org/fibo/ontology/FND/GoalsAndObjectives/Objectives/',
            'fibo_fnd_plc_adr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/',
            'cmns_cxtdsg': 'https://www.omg.org/spec/Commons/ContextualDesignators/',
            'cmns_dt': 'https://www.omg.org/spec/Commons/DatesAndTimes/',
            'fibo_fnd_agr_agr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Agreements/',
            'fibo_fnd_law_jur': 'https://spec.edmcouncil.org/fibo/ontology/FND/Law/Jurisdiction/',
            'fibo_fnd_law_lcap': 'https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCapacity/',
            'fibo_fnd_arr_arr': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Arrangements/',
            'cmns_col': 'https://www.omg.org/spec/Commons/Collections/',
            'fibo_fnd_aap_agt': 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/',
            'lcc_cr': 'https://www.omg.org/spec/LCC/Countries/CountryRepresentation/',
            'fibo_fnd_dt_bd': 'https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/',
            'cmns_doc': 'https://www.omg.org/spec/Commons/Documents/',
            'fibo_fnd_acc_cur': 'https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/',
            'fibo_fnd_dt_oc': 'https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/',
            'fibo_fnd_plc_fac': 'https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/',
            'fibo_fnd_plc_loc': 'https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/',
            'cmns_txt': 'https://www.omg.org/spec/Commons/TextDatatype/',
            'fibo_fnd_oac_own': 'https://spec.edmcouncil.org/fibo/ontology/FND/OwnershipAndControl/Ownership/',
            'fibo_fnd_arr_doc': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/',
            'fibo_fnd_dt_fd': 'https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/FinancialDates/',
            'fibo_fnd_arr_id': 'https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/IdentifiersAndIndices/',
            'fibo_fnd_law_cor': 'https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCore/',
            'sm': 'http://www.omg.org/techprocess/ab/SpecificationMetadata/',
            'lcc_lr': 'https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/',
            'cmns_cxtid': 'https://www.omg.org/spec/Commons/ContextualIdentifiers/',
            'fibo_fnd_utl_alx': 'https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/Analytics/',
            'fibo_be_le_lei': 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/',
            'fibo_be_corp_corp' : 'https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/',
            'fibo_be_le_cb' : 'https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/',
            'fibo_be_ge_ge' : 'https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/',
            'fibo_fbc_pas_fpas': 'https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/',
            'fibo_fbc_dae_dbt':'https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Debt/',
            'fibo_fbc_fct_breg':'https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/BusinessRegistries/',
            'fibo_fbc_pas_caa':'https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/',
            'fibo_fbc_fbc_fi_fi':'https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/FinancialInstruments/',
            'cmns_loc':'https://www.omg.org/spec/Commons/Locations/',
            'cmns_regag':'https://www.omg.org/spec/Commons/RegulatoryAgencies/',
            }