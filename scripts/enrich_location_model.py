import os
import sys

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger

def enrich_location_model():
    db = get_staging_db()
    
    location_class_uri = "https://www.omg.org/spec/Commons/Locations/Location"
    address_class_uri = "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/Address"
    
    # Individuals data
    locations = [
        {
            "uri": "https://model.onto2ai.com/resource/MainStreetOffice",
            "label": "Main Street Office",
            "lat": 51.5074,
            "long": -0.1278,
            "address": {
                "uri": "https://model.onto2ai.com/resource/Address-MainStreetOffice",
                "full": "123 Main St, London, UK",
                "city": "London",
                "zip": "SW1A 1AA"
            }
        },
        {
            "uri": "https://model.onto2ai.com/resource/BroadwayBranch",
            "label": "Broadway Branch",
            "lat": 40.7128,
            "long": -74.0060,
            "address": {
                "uri": "https://model.onto2ai.com/resource/Address-BroadwayBranch",
                "full": "456 Broadway, New York, NY, USA",
                "city": "New York",
                "zip": "10013"
            }
        },
        {
            "uri": "https://model.onto2ai.com/resource/DublinHub",
            "label": "Dublin Hub",
            "lat": 53.3498,
            "long": -6.2603,
            "address": {
                "uri": "https://model.onto2ai.com/resource/Address-DublinHub",
                "full": "789 O'Connell St, Dublin, Ireland",
                "city": "Dublin",
                "zip": "D01 VK06"
            }
        }
    ]
    
    try:
        # 1. Ensure Address class exists
        logger.info("Ensuring Address class exists...")
        db.execute_cypher("MERGE (c:owl__Class {uri: $uri}) SET c.rdfs__label = 'address'", {"uri": address_class_uri})
        
        # 2. Add properties to Location class metadata (for visualization/UI hits)
        logger.info("Updating location class metadata...")
        db.execute_cypher("""
            MATCH (c:owl__Class {uri: $uri})
            SET c.enrichment_status = 'enriched',
                c.added_properties = ['hasAddress', 'hasLatitude', 'hasLongitude']
        """, {"uri": location_class_uri})
        
        # 3. Create Individuals
        for loc in locations:
            logger.info(f"Creating location: {loc['label']}")
            
            addr = loc['address']
            
            # Create Location with flattened address properties
            db.execute_cypher("""
                MATCH (l_cls:owl__Class {uri: $l_cls_uri})
                MERGE (l:owl__NamedIndividual {uri: $uri})
                SET l.rdfs__label = $label,
                    l.hasLatitude = $lat,
                    l.hasLongitude = $long,
                    l.fullAddress = $full,
                    l.city = $city,
                    l.postalCode = $zip,
                    l:Location
                MERGE (l)-[:rdf__type]->(l_cls)
            """, {
                "l_cls_uri": location_class_uri,
                "uri": loc['uri'],
                "label": loc['label'],
                "lat": loc['lat'],
                "long": loc['long'],
                "full": addr['full'],
                "city": addr['city'],
                "zip": addr['zip']
            })
            
        logger.info("Enrichment complete.")
        
    finally:
        db.close()

if __name__ == "__main__":
    enrich_location_model()
