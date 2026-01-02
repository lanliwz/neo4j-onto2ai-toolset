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
    # W3C / Core
    # -----------------------------
    "owl":    "http://www.w3.org/2002/07/owl#",
    "rdf":    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":    "http://www.w3.org/2001/XMLSchema#",
    "xml":    "http://www.w3.org/XML/1998/namespace#",
    "sh":     "http://www.w3.org/ns/shacl#",
    "skos":   "http://www.w3.org/2004/02/skos/core#",
    "dct":    "http://purl.org/dc/terms/",  # shorten dcterms -> dct (optional but common)

    # -----------------------------
    # OMG Commons (cmns_* -> c_*)
    # -----------------------------
    "c":      "https://www.omg.org/spec/Commons/",
    "c_av":   "https://www.omg.org/spec/Commons/AnnotationVocabulary/",
    "c_cds":  "https://www.omg.org/spec/Commons/CodesAndCodeSets/",
    "c_cls":  "https://www.omg.org/spec/Commons/Classifiers/",
    "c_col":  "https://www.omg.org/spec/Commons/Collections/",
    "c_cxd":  "https://www.omg.org/spec/Commons/ContextualDesignators/",
    "c_cxi":  "https://www.omg.org/spec/Commons/ContextualIdentifiers/",
    "c_doc":  "https://www.omg.org/spec/Commons/Documents/",
    "c_dsg":  "https://www.omg.org/spec/Commons/Designators/",
    "c_dt":   "https://www.omg.org/spec/Commons/DatesAndTimes/",
    "c_id":   "https://www.omg.org/spec/Commons/Identifiers/",
    "c_loc":  "https://www.omg.org/spec/Commons/Locations/",
    "c_qtu":  "https://www.omg.org/spec/Commons/QuantitiesAndUnits/",
    "c_reg":  "https://www.omg.org/spec/Commons/RegulatoryAgencies/",
    "c_txt":  "https://www.omg.org/spec/Commons/TextDatatype/",

    # -----------------------------
    # OMG LCC (lcc_* -> l_*)
    # -----------------------------
    "l":      "https://www.omg.org/spec/LCC/",
    "l_cr":   "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/",
    "l_lr":   "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/",

    # -----------------------------
    # OMG Spec Metadata (keep; already short)
    # -----------------------------
    "sm": "http://www.omg.org/techprocess/ab/SpecificationMetadata/",

    # -----------------------------
    # FIBO roots (optional but handy)
    # -----------------------------
    "fibo": "https://spec.edmcouncil.org/fibo/ontology/",
    "be":   "https://spec.edmcouncil.org/fibo/ontology/BE/",
    "fnd":  "https://spec.edmcouncil.org/fibo/ontology/FND/",
    "fbc":  "https://spec.edmcouncil.org/fibo/ontology/FBC/",

    # -----------------------------
    # FIBO BE leaf (fibo_be_* -> be_*)
    # -----------------------------
    "be_fct":     "https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/",
    "be_fct_fct": "https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/",

    "be_le":      "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/",
    "be_le_fbo":  "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/FormalBusinessOrganizations/",
    "be_le_lp":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/",
    "be_le_lei":  "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/",
    "be_le_cb":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/",

    "be_corp":       "https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/",
    "be_corp_corp":  "https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/",

    "be_ge":      "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/",
    "be_ge_ge":   "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/",

    # -----------------------------
    # FIBO FND leaf (fibo_fnd_* -> fnd_*)
    # -----------------------------
    "fnd_acc_aeq": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/AccountingEquity/",
    "fnd_acc_cur": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/",

    "fnd_aap_agt": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/",
    "fnd_aap_ppl": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/",

    "fnd_agr_agr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Agreements/",
    "fnd_agr_ctr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/",

    "fnd_arr_arr": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Arrangements/",
    "fnd_arr_cls": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/ClassificationSchemes/",
    "fnd_arr_doc": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/",
    "fnd_arr_id":  "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/IdentifiersAndIndices/",

    "fnd_dt_bd":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/",
    "fnd_dt_fd":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/FinancialDates/",
    "fnd_dt_oc":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/",

    "fnd_gao_obj": "https://spec.edmcouncil.org/fibo/ontology/FND/GoalsAndObjectives/Objectives/",

    "fnd_law_cor": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCore/",
    "fnd_law_jur": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/Jurisdiction/",
    "fnd_law_lcp": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCapacity/",

    "fnd_oac_own": "https://spec.edmcouncil.org/fibo/ontology/FND/OwnershipAndControl/Ownership/",

    "fnd_org_fm":  "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/",
    "fnd_org_org": "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/",

    "fnd_pas_pas": "https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/",

    "fnd_plc_adr": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/",
    "fnd_plc_fac": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/",
    "fnd_plc_loc": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/",

    "fnd_pty_pty": "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/",
    "fnd_pty_rl":  "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Roles/",

    "fnd_rel_rel": "https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/",

    "fnd_utl_av":  "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/",
    "fnd_utl_alx": "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/Analytics/",

    # -----------------------------
    # FIBO FBC leaf (fibo_fbc_* -> fbc_*)
    # -----------------------------
    "fbc_pas_fpas":   "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/",
    "fbc_dae_dbt":    "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Debt/",
    "fbc_fct_breg":   "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/BusinessRegistries/",
    "fbc_pas_caa":    "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/",
    "fbc_fi_fi":      "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/FinancialInstruments/",
}