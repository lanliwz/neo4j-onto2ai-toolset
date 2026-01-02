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
prefixes = {
    # -----------------------------
    # W3C / IETF (core standards)
    # -----------------------------
    "owl":    "http://www.w3.org/2002/07/owl#",
    "rdf":    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":    "http://www.w3.org/2001/XMLSchema#",
    "xml":    "http://www.w3.org/XML/1998/namespace#",
    "sh":     "http://www.w3.org/ns/shacl#",
    "skos":   "http://www.w3.org/2004/02/skos/core#",
    "dcterms":"http://purl.org/dc/terms/",

    # -----------------------------
    # OMG Commons (domain + modules)
    # -----------------------------
    "cmns":        "https://www.omg.org/spec/Commons/",

    "cmns_av":     "https://www.omg.org/spec/Commons/AnnotationVocabulary/",
    "cmns_cds":    "https://www.omg.org/spec/Commons/CodesAndCodeSets/",
    "cmns_cls":    "https://www.omg.org/spec/Commons/Classifiers/",
    "cmns_col":    "https://www.omg.org/spec/Commons/Collections/",
    "cmns_cxtdsg": "https://www.omg.org/spec/Commons/ContextualDesignators/",
    "cmns_cxtid":  "https://www.omg.org/spec/Commons/ContextualIdentifiers/",
    "cmns_doc":    "https://www.omg.org/spec/Commons/Documents/",
    "cmns_dsg":    "https://www.omg.org/spec/Commons/Designators/",
    "cmns_dt":     "https://www.omg.org/spec/Commons/DatesAndTimes/",
    "cmns_id":     "https://www.omg.org/spec/Commons/Identifiers/",
    "cmns_loc":    "https://www.omg.org/spec/Commons/Locations/",
    "cmns_qtu":    "https://www.omg.org/spec/Commons/QuantitiesAndUnits/",
    "cmns_regag":  "https://www.omg.org/spec/Commons/RegulatoryAgencies/",
    "cmns_txt":    "https://www.omg.org/spec/Commons/TextDatatype/",

    # -----------------------------
    # OMG LCC (domain + modules)
    # -----------------------------
    "lcc":    "https://www.omg.org/spec/LCC/",
    "lcc_cr": "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/",
    "lcc_lr": "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/",

    # -----------------------------
    # OMG Specification Metadata (kept as-is)
    # -----------------------------
    "sm": "http://www.omg.org/techprocess/ab/SpecificationMetadata/",

    # -----------------------------
    # FIBO (domain + families + modules)
    # -----------------------------
    "fibo":     "https://spec.edmcouncil.org/fibo/ontology/",

    # families
    "fibo_be":  "https://spec.edmcouncil.org/fibo/ontology/BE/",
    "fibo_fnd": "https://spec.edmcouncil.org/fibo/ontology/FND/",
    "fibo_fbc": "https://spec.edmcouncil.org/fibo/ontology/FBC/",

    # --- BE modules (LegalEntities / Corporations / GovernmentEntities / FunctionalEntities)
    "fibo_be_le":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/",
    "fibo_be_corp": "https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/",
    "fibo_be_ge":   "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/",
    "fibo_be_fct":  "https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/",

    # --- FND modules
    "fibo_fnd_acc": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/",
    "fibo_fnd_aap": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/",
    "fibo_fnd_agr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/",
    "fibo_fnd_arr": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/",
    "fibo_fnd_dt":  "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/",
    "fibo_fnd_gao": "https://spec.edmcouncil.org/fibo/ontology/FND/GoalsAndObjectives/",
    "fibo_fnd_law": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/",
    "fibo_fnd_oac": "https://spec.edmcouncil.org/fibo/ontology/FND/OwnershipAndControl/",
    "fibo_fnd_org": "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/",
    "fibo_fnd_pas": "https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/",
    "fibo_fnd_plc": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/",
    "fibo_fnd_pty": "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/",
    "fibo_fnd_rel": "https://spec.edmcouncil.org/fibo/ontology/FND/Relations/",
    "fibo_fnd_utl": "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/",

    # --- FBC modules
    "fibo_fbc_dae": "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/",
    "fibo_fbc_fct": "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/",
    "fibo_fbc_fi":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/",
    "fibo_fbc_pas": "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/",

    # -----------------------------
    # Leaf namespaces you already use (keep for precision)
    # -----------------------------
    # BE leaf
    "fibo_be_fct_fct":  "https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/",
    "fibo_be_le_fbo":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/FormalBusinessOrganizations/",
    "fibo_be_le_lp":    "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/",
    "fibo_be_le_lei":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/",
    "fibo_be_le_cb":    "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/",
    "fibo_be_corp_corp":"https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/",
    "fibo_be_ge_ge":    "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/",

    # FND leaf
    "fibo_fnd_acc_aeq": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/AccountingEquity/",
    "fibo_fnd_acc_cur": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/",
    "fibo_fnd_aap_agt": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/",
    "fibo_fnd_aap_ppl": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/",
    "fibo_fnd_agr_agr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Agreements/",
    "fibo_fnd_agr_ctr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/",
    "fibo_fnd_arr_arr": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Arrangements/",
    "fibo_fnd_arr_cls": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/ClassificationSchemes/",
    "fibo_fnd_arr_doc": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/",
    "fibo_fnd_arr_id":  "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/IdentifiersAndIndices/",
    "fibo_fnd_dt_bd":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/",
    "fibo_fnd_dt_fd":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/FinancialDates/",
    "fibo_fnd_dt_oc":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/",
    "fibo_fnd_gao_obj": "https://spec.edmcouncil.org/fibo/ontology/FND/GoalsAndObjectives/Objectives/",
    "fibo_fnd_law_cor": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCore/",
    "fibo_fnd_law_jur": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/Jurisdiction/",
    "fibo_fnd_law_lcap":"https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCapacity/",
    "fibo_fnd_oac_own": "https://spec.edmcouncil.org/fibo/ontology/FND/OwnershipAndControl/Ownership/",
    "fibo_fnd_org_fm":  "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/",
    "fibo_fnd_org_org": "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/",
    "fibo_fnd_pas_pas": "https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/",
    "fibo_fnd_plc_adr": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/",
    "fibo_fnd_plc_fac": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/",
    "fibo_fnd_plc_loc": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/",
    "fibo_fnd_pty_pty": "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/",
    "fibo_fnd_pty_rl":  "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Roles/",
    "fibo_fnd_rel_rel": "https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/",
    "fibo_fnd_utl_av":  "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/",
    "fibo_fnd_utl_alx": "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/Analytics/",

    # FBC leaf
    "fibo_fbc_dae_dbt":     "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Debt/",
    "fibo_fbc_fct_breg":    "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/BusinessRegistries/",
    "fibo_fbc_pas_fpas":    "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/",
    "fibo_fbc_pas_caa":     "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/",
    "fibo_fbc_fbc_fi_fi":   "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/FinancialInstruments/",
}