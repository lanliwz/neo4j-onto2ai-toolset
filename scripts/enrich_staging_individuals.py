import os
import sys

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger

def enrich_individuals():
    db = get_staging_db()
    
    countries = [
        {"uri": "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/UnitedStatesOfAmerica", "label": "United States of America (the)"},
        {"uri": "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/UnitedKingdomOfGreatBritainAndNorthernIreland", "label": "United Kingdom of Great Britain and Northern Ireland (the)"},
        {"uri": "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/Canada", "label": "Canada (le)"},
        {"uri": "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/Ireland", "label": "Ireland"}
    ]
    
    currencies = [
        {"uri": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/USDollar", "label": "US Dollar"},
        {"uri": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/Euro", "label": "Euro"},
        {"uri": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/PoundSterling", "label": "Pound Sterling"},
        {"uri": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/ISO4217-CurrencyCodes/CanadianDollar", "label": "Canadian Dollar"}
    ]
    
    occurrence_kinds = [
        {"uri": "https://model.onto2ai.com/resource/AuthorizationEvent", "label": "Authorization Event"},
        {"uri": "https://model.onto2ai.com/resource/SettlementEvent", "label": "Settlement Event"},
        {"uri": "https://model.onto2ai.com/resource/RefundEvent", "label": "Refund Event"},
        {"uri": "https://model.onto2ai.com/resource/ChargebackEvent", "label": "Chargeback Event"},
        {"uri": "https://model.onto2ai.com/resource/CardVerificationEvent", "label": "Card Verification Event"}
    ]

    functional_roles = [
        {"uri": "https://model.onto2ai.com/resource/MerchantRole", "label": "Merchant"},
        {"uri": "https://model.onto2ai.com/resource/IssuerRole", "label": "Issuer"},
        {"uri": "https://model.onto2ai.com/resource/AcquirerRole", "label": "Acquirer"},
        {"uri": "https://model.onto2ai.com/resource/CardholderRole", "label": "Cardholder"},
        {"uri": "https://model.onto2ai.com/resource/ServiceProviderRole", "label": "Service Provider"}
    ]

    region_kinds = [
        {"uri": "https://model.onto2ai.com/resource/CountryRegionKind", "label": "Country"},
        {"uri": "https://model.onto2ai.com/resource/CountrySubdivisionRegionKind", "label": "Country Subdivision"},
        {"uri": "https://model.onto2ai.com/resource/GeopoliticalEntityRegionKind", "label": "Geopolitical Entity"}
    ]
    
    country_class_uri = "https://www.omg.org/spec/Commons/Locations/Country"
    currency_class_uri = "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/Currency"
    occurrence_kind_class_uri = "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/OccurrenceKind"
    functional_role_class_uri = "https://www.omg.org/spec/Commons/RolesAndCompositions/FunctionalRole"
    region_kind_class_uri = "https://www.omg.org/spec/Commons/Locations/GeographicRegionKind"
    
    try:
        # 1. Ensure classes exist (safety)
        db.execute_cypher("MERGE (c:owl__Class {uri: $uri}) SET c.rdfs__label = 'country'", {"uri": country_class_uri})
        db.execute_cypher("MERGE (c:owl__Class {uri: $uri}) SET c.rdfs__label = 'currency'", {"uri": currency_class_uri})
        db.execute_cypher("MERGE (c:owl__Class {uri: $uri}) SET c.rdfs__label = 'occurrence kind'", {"uri": occurrence_kind_class_uri})
        db.execute_cypher("MERGE (c:owl__Class {uri: $uri}) SET c.rdfs__label = 'functional role'", {"uri": functional_role_class_uri})
        db.execute_cypher("MERGE (c:owl__Class {uri: $uri}) SET c.rdfs__label = 'geographic region kind'", {"uri": region_kind_class_uri})
        
        # 2. Create Countries
        for c in countries:
            logger.info(f"Creating country individual: {c['label']}")
            query = """
            MATCH (cls:owl__Class {uri: $cls_uri})
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i:Country
            MERGE (i)-[:rdf__type]->(cls)
            """
            db.execute_cypher(query, {
                "uri": c["uri"], 
                "label": c["label"], 
                "cls_uri": country_class_uri
            })
            
        # 3. Create Currencies
        for c in currencies:
            logger.info(f"Creating currency individual: {c['label']}")
            query = """
            MATCH (cls:owl__Class {uri: $cls_uri})
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i:Currency
            MERGE (i)-[:rdf__type]->(cls)
            """
            db.execute_cypher(query, {
                "uri": c["uri"], 
                "label": c["label"], 
                "cls_uri": currency_class_uri
            })

        # 4. Create Occurrence Kinds
        for ok in occurrence_kinds:
            logger.info(f"Creating occurrence kind individual: {ok['label']}")
            query = """
            MATCH (cls:owl__Class {uri: $cls_uri})
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i:OccurrenceKind
            MERGE (i)-[:rdf__type]->(cls)
            """
            db.execute_cypher(query, {
                "uri": ok["uri"], 
                "label": ok["label"], 
                "cls_uri": occurrence_kind_class_uri
            })

        # 5. Create Functional Roles
        for fr in functional_roles:
            logger.info(f"Creating functional role individual: {fr['label']}")
            query = """
            MATCH (cls:owl__Class {uri: $cls_uri})
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i:FunctionalRole
            MERGE (i)-[:rdf__type]->(cls)
            """
            db.execute_cypher(query, {
                "uri": fr["uri"], 
                "label": fr["label"], 
                "cls_uri": functional_role_class_uri
            })

        # 6. Create Geographic Region Kinds
        for rk in region_kinds:
            logger.info(f"Creating region kind individual: {rk['label']}")
            query = """
            MATCH (cls:owl__Class {uri: $cls_uri})
            MERGE (i:owl__NamedIndividual {uri: $uri})
            SET i.rdfs__label = $label,
                i:GeographicRegionKind
            MERGE (i)-[:rdf__type]->(cls)
            """
            db.execute_cypher(query, {
                "uri": rk["uri"], 
                "label": rk["label"], 
                "cls_uri": region_kind_class_uri
            })
            
        logger.info("Enrichment complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    enrich_individuals()
