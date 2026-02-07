import os
import sys

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from neo4j_onto2ai_toolset.onto2ai_tool_config import get_staging_db

def verify_enrichment():
    db = get_staging_db()
    try:
        query = """
        MATCH (i:owl__NamedIndividual)-[:rdf__type]->(c:owl__Class)
        WHERE c.rdfs__label IN ['country', 'currency', 'occurrence kind', 'functional role', 'geographic region kind']
        RETURN i.rdfs__label AS label, c.rdfs__label AS class, labels(i) AS labels
        """
        results = db.execute_cypher(query)
        
        print(f"Found {len(results)} individuals:")
        for r in results:
            print(f"- {r['label']} (Class: {r['class']}, Labels: {r['labels']})")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_enrichment()
