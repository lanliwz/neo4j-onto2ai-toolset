# prefixes.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple


# -----------------------------
# 1) Canonical prefixes (PUBLIC CONTRACT)
#    - used for ALL generated keys
#    - do not rename existing keys (breaking change)
# -----------------------------
PREFIXES_CANON: Dict[str, str] = {
    # W3C / core
    "owl":  "http://www.w3.org/2002/07/owl#",
    "rdf":  "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":  "http://www.w3.org/2001/XMLSchema#",
    "xml":  "http://www.w3.org/XML/1998/namespace#",
    "sh":   "http://www.w3.org/ns/shacl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dct":  "http://purl.org/dc/terms/",

    # OMG Commons (short, unique)
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
    "c_org":  "https://www.omg.org/spec/Commons/Organizations/",
    "c_pty":  "https://www.omg.org/spec/Commons/Parties/",
    "c_fac":  "https://www.omg.org/spec/Commons/Facilities/",
    "c_agr":  "https://www.omg.org/spec/Commons/Agreements/",
    "c_ctr":  "https://www.omg.org/spec/Commons/Contracts/",
    "c_mod":  "https://www.omg.org/spec/Commons/AnnotationMetadata/",
    "c_rac":  "https://www.omg.org/spec/Commons/RolesAndCompositions/",
    "c_pmp":  "https://www.omg.org/spec/Commons/PartiesAndPeople/",
    "c_gov":  "https://www.omg.org/spec/Commons/Governance/",
    "c_idm":  "https://www.omg.org/spec/Commons/IdentifiersAndMetadata/",
    "c_pas":  "https://www.omg.org/spec/Commons/PartiesAndSituations/",
    "c_ra":   "https://www.omg.org/spec/Commons/RegistrationAuthorities/",
    "c_sf":   "https://www.omg.org/spec/Commons/SitesAndFacilities/",

    # OMG LCC
    "l":    "https://www.omg.org/spec/LCC/",
    "l_cr": "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/",
    "l_lr": "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/",

    # OMG Spec Metadata (kept)
    "sm": "http://www.omg.org/techprocess/ab/SpecificationMetadata/",

    # FIBO roots (optional but handy)
    "fibo": "https://spec.edmcouncil.org/fibo/ontology/",
    "be":   "https://spec.edmcouncil.org/fibo/ontology/BE/",
    "fnd":  "https://spec.edmcouncil.org/fibo/ontology/FND/",
    "fbc":  "https://spec.edmcouncil.org/fibo/ontology/FBC/",

    # --- BE leaf you use
    "be_fct_fct":  "https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/FunctionalEntities/",
    "be_le_fbo":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/FormalBusinessOrganizations/",
    "be_le_lp":    "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/",
    "be_le_lei":   "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LEIEntities/",
    "be_le_cb":    "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/",
    "be_corp_corp":"https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/",
    "be_ge_ge":    "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/",
    "be_ptr_ptr":   "https://spec.edmcouncil.org/fibo/ontology/BE/Partnerships/Partnerships/",
    "be_plc_plc":   "https://spec.edmcouncil.org/fibo/ontology/BE/PrivateLimitedCompanies/PrivateLimitedCompanies/",
    "be_oac_exec":  "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/Executives/",
    "be_oac_own":   "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/OwnershipParties/",
    "be_oac_cctl":  "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/CorporateControl/",
    "be_oac_cown":  "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/CorporateOwnership/",
    "be_oac_ctl":   "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/ControlParties/",
    "be_tr_tr":    "https://spec.edmcouncil.org/fibo/ontology/BE/Trusts/Trusts/",

    # --- FND leaf you use
    "fnd_arr_cls": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/ClassificationSchemes/",
    "fnd_org_fm":  "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/FormalOrganizations/",
    "fnd_org_org": "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/",
    "fnd_pas_pas": "https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/",
    "fnd_pty_pty": "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/",
    "fnd_pty_rl":  "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Roles/",
    "fnd_rel_rel": "https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/",
    "fnd_utl_av":  "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/",
    "fnd_aap_ppl": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/",
    "fnd_acc_aeq": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/AccountingEquity/",
    "fnd_agr_ctr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/",
    "fnd_gao_obj": "https://spec.edmcouncil.org/fibo/ontology/FND/GoalsAndObjectives/Objectives/",
    "fnd_plc_adr": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/",
    "fnd_agr_agr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Agreements/",
    "fnd_law_jur": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/Jurisdiction/",
    "fnd_law_lcp": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCapacity/",
    "fnd_aap_agt": "https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/Agents/",
    "fnd_dt_bd":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/BusinessDates/",
    "fnd_acc_4217": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/",
    "fnd_acc_cur": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/",
    "fnd_dt_oc":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/",
    "fnd_plc_fac": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/",
    "fnd_plc_loc": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/",
    "fnd_oac_own": "https://spec.edmcouncil.org/fibo/ontology/FND/OwnershipAndControl/Ownership/",
    "fnd_arr_doc": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/",
    "fnd_dt_fd":   "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/FinancialDates/",
    "fnd_arr_id":  "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/IdentifiersAndIndices/",
    "fnd_arr_rat": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Ratings/",
    "fnd_law_cor": "https://spec.edmcouncil.org/fibo/ontology/FND/Law/LegalCore/",
    "fnd_utl_alx": "https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/Analytics/",

    # --- FBC leaf you use
    "fbc_pas_fpas": "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/",
    "fbc_dae_dbt":  "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Debt/",
    "fbc_fct_breg": "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/BusinessRegistries/",
    "fbc_pas_caa":  "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/ClientsAndAccounts/",
    "fbc_fi_fi":    "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/FinancialInstruments/",
    "fbc_fi_stl":   "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/Settlement/",
    "fbc_fi_inst":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/InstrumentBase/",
    "fbc_fi_prc":   "https://spec.edmcouncil.org/fibo/ontology/FBC/FinancialInstruments/InstrumentPricing/",
    "fbc_fct_fse":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/FinancialServicesEntities/",
    "fbc_dae_eq":   "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Equities/",
    "be_fct_pub":   "https://spec.edmcouncil.org/fibo/ontology/BE/FunctionalEntities/Publishers/",
    "bp_bp_bp":    "https://spec.edmcouncil.org/fibo/ontology/BP/BusinessProcesses/BusinessProcesses/",
    "fbc_fct_mkt":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/Markets/",
    "fbc_fct_reg":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/RegulatoryAgencies/",
    "fbc_fct_bc":   "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/BusinessCenters/",
    "fbc_fct_ira":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/InternationalRegistriesAndAuthorities/",
    "fbc_fct_usreg":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USRegulatoryAgencies/",
    "fbc_fct_careg":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/CARegulatoryAgencies/",
    "fbc_fct_eureg":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/EuropeanEntities/EURegulatoryAgencies/",
    "fbc_fct_eufse":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/EuropeanEntities/EUFinancialServicesEntities/",
    "fbc_fct_usfse":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USFinancialServicesEntities/",
    "fbc_fct_cafse":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/CAFinancialServicesEntities/",
    "fbc_fct_nic":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USNationalInformationCenterControlledVocabularies/",
    "fbc_fct_mkti": "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/MarketsIndividuals/",
    "fbc_fct_bci":  "https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/BusinessCentersIndividuals/",
    "fbc_fct_usmkti":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USMarketsAndExchangesIndividuals/",
    "fbc_fct_usfsei":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USFinancialServicesEntitiesIndividuals/",
    "fbc_fct_eufsei":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/EuropeanEntities/EuropeanFinancialServicesEntitiesIndividuals/",
    "fbc_fct_usexi":"https://spec.edmcouncil.org/fibo/ontology/FBC/FunctionalEntities/NorthAmericanEntities/USExampleIndividuals/",
    "fbc_dae_rat":  "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/CreditRatings/",
    "fbc_dae_gty":  "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Guaranty/",
    "loan_loan_lo": "https://spec.edmcouncil.org/fibo/ontology/LOAN/LoansGeneral/Loans/",
    "loan_loan_ca": "https://spec.edmcouncil.org/fibo/ontology/LOAN/LoansSpecific/CardAccounts/",
    "loan_loan_con": "https://spec.edmcouncil.org/fibo/ontology/LOAN/LoansSpecific/ConsumerLoans/",
    "loan_loan_stud": "https://spec.edmcouncil.org/fibo/ontology/LOAN/LoansSpecific/StudentLoans/",
    "sec_dbt_ex":   "https://spec.edmcouncil.org/fibo/ontology/SEC/Debt/ExerciseConventions/",
    "sec_sec_bsk":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Securities/Baskets/",
    "sec_sec_iss":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Securities/SecuritiesIssuance/",
    "sec_sec_lst":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Securities/SecuritiesListings/",
    "sec_sec_cls":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Securities/SecuritiesClassification/",
    "sec_eq_eq":    "https://spec.edmcouncil.org/fibo/ontology/SEC/Equities/EquityInstruments/",
    "sec_dbt_dbt":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Debt/DebtInstruments/",
    "sec_dbt_bnd":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Debt/Bonds/",
    "sec_dbt_abs":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Debt/AssetBackedSecurities/",
    "sec_dbt_mbs":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Debt/MortgageBackedSecurities/",
    "sec_fnd_fnd":  "https://spec.edmcouncil.org/fibo/ontology/SEC/Funds/Funds/",
    "bp_iss_dbt":   "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/DebtIssuance/",
    "bp_iss_prc":   "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/IssuanceProcess/",
    "bp_iss_ipo":   "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/EquitiesIPOIssuance/",
    "bp_iss_mbs":   "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/MBSIssuance/",
    "bp_iss_muni":  "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/MuniIssuance/",
    "bp_iss_doc":   "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/IssuanceDocuments/",
    "bp_iss_ambs":  "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/AgencyMBSIssuance/",
    "bp_iss_pmbs":  "https://spec.edmcouncil.org/fibo/ontology/BP/SecuritiesIssuance/PrivateLabelMBSIssuance/",
    "bp_prc_fcp":   "https://spec.edmcouncil.org/fibo/ontology/BP/Process/FinancialContextAndProcess/",
    "bp_prc_mod":   "https://spec.edmcouncil.org/fibo/ontology/BP/Process/MetadataBPProcess/",
    "ind_ind_ind":  "https://spec.edmcouncil.org/fibo/ontology/IND/Indicators/Indicators/",
    "ind_ir_ir":    "https://spec.edmcouncil.org/fibo/ontology/IND/InterestRates/InterestRates/",
    "ind_fx_fx":    "https://spec.edmcouncil.org/fibo/ontology/IND/ForeignExchange/ForeignExchange/",
    "ind_ei_ei":    "https://spec.edmcouncil.org/fibo/ontology/IND/EconomicIndicators/EconomicIndicators/",
    "ind_mkt_bas":  "https://spec.edmcouncil.org/fibo/ontology/IND/MarketIndices/BasketIndices/",
    "der_drc_comm": "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/CommoditiesContracts/",
    "der_drc_curr": "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/CurrencyContracts/",
    "der_drc_der":  "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/DerivativesBasics/",
    "der_drc_opt":  "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/Options/",
    "der_drc_exo":  "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/ExoticOptions/",
    "der_drc_swp":  "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/Swaps/",
    "der_drc_ff":   "https://spec.edmcouncil.org/fibo/ontology/DER/DerivativesContracts/FuturesAndForwards/",
    "der_sbd_sbd":  "https://spec.edmcouncil.org/fibo/ontology/DER/SecurityBasedDerivatives/SecurityBasedDerivatives/",
}


# -----------------------------
# 2) Alias prefixes (NOT used for generated keys)
#    - for authoring SPARQL/Turtle / user convenience
#    - safe to add, safe to rename (does not affect generated keys)
# -----------------------------
PREFIXES_ALIAS: Dict[str, str] = {
    # common alternates
    "dcterms": PREFIXES_CANON["dct"],

    # your old long forms (if you want to keep docs/queries compatible)
    "cmns_av": PREFIXES_CANON["c_av"],
    "cmns_cds": PREFIXES_CANON["c_cds"],
    "cmns_cls": PREFIXES_CANON["c_cls"],
    "cmns_col": PREFIXES_CANON["c_col"],
    "cmns_cxtdsg": PREFIXES_CANON["c_cxd"],
    "cmns_cxtid": PREFIXES_CANON["c_cxi"],
    "cmns_doc": PREFIXES_CANON["c_doc"],
    "cmns_dsg": PREFIXES_CANON["c_dsg"],
    "cmns_dt": PREFIXES_CANON["c_dt"],
    "cmns_id": PREFIXES_CANON["c_id"],
    "cmns_loc": PREFIXES_CANON["c_loc"],
    "cmns_qtu": PREFIXES_CANON["c_qtu"],
    "cmns_regag": PREFIXES_CANON["c_reg"],
    "cmns_txt": PREFIXES_CANON["c_txt"],

    "lcc_cr": PREFIXES_CANON["l_cr"],
    "lcc_lr": PREFIXES_CANON["l_lr"],

    # old fibo_* keys mapped to new canon (only if you previously used them)
    "fibo_be_fct_fct": PREFIXES_CANON["be_fct_fct"],
    "fibo_be_le_fbo":  PREFIXES_CANON["be_le_fbo"],
    "fibo_be_le_lp":   PREFIXES_CANON["be_le_lp"],
    "fibo_be_le_lei":  PREFIXES_CANON["be_le_lei"],
    "fibo_be_le_cb":   PREFIXES_CANON["be_le_cb"],
    "fibo_be_corp_corp": PREFIXES_CANON["be_corp_corp"],
    "fibo_be_ge_ge":     PREFIXES_CANON["be_ge_ge"],

    "fibo_fnd_arr_cls": PREFIXES_CANON["fnd_arr_cls"],
    "fibo_fnd_org_fm":  PREFIXES_CANON["fnd_org_fm"],
    "fibo_fnd_org_org": PREFIXES_CANON["fnd_org_org"],
    "fibo_fnd_pas_pas": PREFIXES_CANON["fnd_pas_pas"],
    "fibo_fnd_pty_pty": PREFIXES_CANON["fnd_pty_pty"],
    "fibo_fnd_pty_rl":  PREFIXES_CANON["fnd_pty_rl"],
    "fibo_fnd_rel_rel": PREFIXES_CANON["fnd_rel_rel"],
    "fibo_fnd_utl_av":  PREFIXES_CANON["fnd_utl_av"],
    "fibo_fnd_aap_ppl": PREFIXES_CANON["fnd_aap_ppl"],
    "fibo_fnd_acc_aeq": PREFIXES_CANON["fnd_acc_aeq"],
    "fibo_fnd_agr_ctr": PREFIXES_CANON["fnd_agr_ctr"],
    "fibo_fnd_gao_obj": PREFIXES_CANON["fnd_gao_obj"],
    "fibo_fnd_plc_adr": PREFIXES_CANON["fnd_plc_adr"],
    "fibo_fnd_agr_agr": PREFIXES_CANON["fnd_agr_agr"],
    "fibo_fnd_law_jur": PREFIXES_CANON["fnd_law_jur"],
    "fibo_fnd_law_lcap": PREFIXES_CANON["fnd_law_lcp"],
    "fibo_fnd_aap_agt": PREFIXES_CANON["fnd_aap_agt"],
    "fibo_fnd_dt_bd":   PREFIXES_CANON["fnd_dt_bd"],
    "fibo_fnd_acc_cur": PREFIXES_CANON["fnd_acc_cur"],
    "fibo_fnd_dt_oc":   PREFIXES_CANON["fnd_dt_oc"],
    "fibo_fnd_plc_fac": PREFIXES_CANON["fnd_plc_fac"],
    "fibo_fnd_plc_loc": PREFIXES_CANON["fnd_plc_loc"],
    "fibo_fnd_oac_own": PREFIXES_CANON["fnd_oac_own"],
    "fibo_fnd_arr_doc": PREFIXES_CANON["fnd_arr_doc"],
    "fibo_fnd_dt_fd":   PREFIXES_CANON["fnd_dt_fd"],
    "fibo_fnd_arr_id":  PREFIXES_CANON["fnd_arr_id"],
    "fibo_fnd_law_cor": PREFIXES_CANON["fnd_law_cor"],
    "fibo_fnd_utl_alx": PREFIXES_CANON["fnd_utl_alx"],

    "fibo_fbc_pas_fpas":   PREFIXES_CANON["fbc_pas_fpas"],
    "fibo_fbc_dae_dbt":    PREFIXES_CANON["fbc_dae_dbt"],
    "fibo_fbc_fct_breg":   PREFIXES_CANON["fbc_fct_breg"],
    "fibo_fbc_pas_caa":    PREFIXES_CANON["fbc_pas_caa"],
    "fibo_fbc_fbc_fi_fi":  PREFIXES_CANON["fbc_fi_fi"],
}


# -----------------------------
# 3) Deterministic matching + canonicalization
# -----------------------------
DEFAULT_PRIORITY: List[str] = [
    # W3C
    "rdf", "rdfs", "owl", "xsd", "skos", "xml", "sh", "dct",
    # OMG commons/lcc/meta
    "c", "l", "sm",
    # FIBO roots
    "fibo", "be", "fnd", "fbc",
]

def _rank(prefix: str) -> Tuple[int, int, str]:
    """
    Lower is better.
    1) group by known domains
    2) explicit priority list order
    3) lexical fallback
    """
    if prefix in DEFAULT_PRIORITY:
        return (0, DEFAULT_PRIORITY.index(prefix), prefix)

    if prefix.startswith("c_") or prefix.startswith("l_") or prefix == "sm":
        return (1, 10_000, prefix)

    if prefix.startswith(("be", "fnd", "fbc")):
        return (2, 10_000, prefix)

    return (3, 10_000, prefix)

@dataclass(frozen=True)
class QName:
    prefix: str
    local: str
    namespace: str

def _best_match(uri: str, prefix_map: Dict[str, str]) -> Optional[QName]:
    matches = [(pfx, ns) for pfx, ns in prefix_map.items() if uri.startswith(ns)]
    if not matches:
        return None

    # Longest namespace match
    max_len = max(len(ns) for _, ns in matches)
    cands = [(pfx, ns) for pfx, ns in matches if len(ns) == max_len]

    # Tie-break by rank then prefix
    cands.sort(key=lambda t: _rank(t[0]))
    pfx, ns = cands[0]
    return QName(prefix=pfx, local=uri[len(ns):], namespace=ns)

def uri_to_qname(uri: str, *, allow_alias: bool = True) -> Optional[QName]:
    """
    Resolve URI to QName.
    If allow_alias=True, we try CANON+ALIAS maps for matching,
    but always return a CANON prefix when possible.
    """
    # 1) match against combined maps for maximum recall
    combined = dict(PREFIXES_CANON)
    if allow_alias:
        combined.update(PREFIXES_ALIAS)

    q = _best_match(uri, combined)
    if not q:
        return None

    # 2) canonicalize: map namespace -> canonical prefix (deterministic)
    canon_prefix = namespace_to_canon_prefix(q.namespace)
    if canon_prefix:
        return QName(prefix=canon_prefix, local=q.local, namespace=q.namespace)

    # 3) if no canonical prefix uses that exact namespace, return matched prefix
    return q

def namespace_to_canon_prefix(namespace: str) -> Optional[str]:
    """
    Given an exact namespace IRI, return the canonical prefix key.
    If multiple canonical keys point to same namespace, tie-break deterministically.
    """
    candidates = [pfx for pfx, ns in PREFIXES_CANON.items() if ns == namespace]
    if not candidates:
        return None
    candidates.sort(key=_rank)
    return candidates[0]


# -----------------------------
# 4) Operational name generation (Neo4j)
# -----------------------------
def uri_to_neo4j_key(uri: str, *, allow_alias: bool = True) -> Optional[str]:
    """
    Always uses CANON prefix keys (your namespace contract).
    Returns 'prefix__local'.
    """
    q = uri_to_qname(uri, allow_alias=allow_alias)
    if not q:
        return None
    return f"{q.prefix}__{q.local}"