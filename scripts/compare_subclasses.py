import os
import sys

# Add project root to sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from neo4j_onto2ai_toolset.onto2ai_tool_config import semanticdb, get_staging_db, neo4j_model, NEO4J_STAGING_DB_NAME
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger

def get_subclasses(db, name):
    query = """
    MATCH (c:owl__Class)-[:rdfs__subClassOf]->(p:owl__Class)
    RETURN c.uri AS child, p.uri AS parent, c.rdfs__label AS childLabel, p.rdfs__label AS parentLabel
    """
    logger.info(f"Fetching subclasses from {name}...")
    results = db.execute_cypher(query, name=f"get_subclasses_{name}")
    data = {(r['child'], r['parent']): (r['childLabel'], r['parentLabel']) for r in results}
    print(f"DEBUG: Found {len(data)} subClassOf links in {name}")
    return data

def get_all_staging_classes(db):
    query = "MATCH (c:owl__Class) RETURN c.uri AS uri"
    results = db.execute_cypher(query, name="get_all_staging_classes")
    return {r['uri'] for r in results}

def main():
    # 1. Get subclasses from main ontology DB
    main_subclasses = get_subclasses(semanticdb, "Main Ontology DB")
    
    # 2. Get subclasses and all class nodes from staging DB
    staging_db = get_staging_db()
    try:
        staging_subclasses = get_subclasses(staging_db, "Staging DB")
        staging_classes = get_all_staging_classes(staging_db)
    finally:
        staging_db.close()
    
    # 3. Compare and filter by existing classes
    missing = []
    for rel_key, labels in main_subclasses.items():
        child_uri, parent_uri = rel_key
        # Check if it's missing AND both classes exist in staging
        if rel_key not in staging_subclasses:
            if child_uri in staging_classes and parent_uri in staging_classes:
                missing.append({
                    "child": child_uri,
                    "parent": parent_uri,
                    "childLabel": labels[0],
                    "parentLabel": labels[1]
                })
    
    # 4. Report
    if not missing:
        print("\n✅ No missing subclass relationships found between existing classes in Staging DB.")
    else:
        print(f"\n❌ Found {len(missing)} missing subclass relationships among existing classes in Staging DB:\n")
        print("| Child Class | Parent Class | Child URI | Parent URI |")
        print("| :--- | :--- | :--- | :--- |")
        for m in sorted(missing, key=lambda x: str(x['childLabel'])):
            print(f"| {m['childLabel']} | {m['parentLabel']} | {m['child']} | {m['parent']} |")

if __name__ == "__main__":
    main()
