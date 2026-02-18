---
name: "FIBO Loading Expert"
description: "Instructions for loading the Financial Industry Business Ontology (FIBO) into Neo4j."
---
# FIBO Loading Expert Instructions

You are responsible for loading the FIBO ontology into the Neo4j environment. This involves configuring the loader script and executing the import process.

## Loading Process

### Configure the Loader
The core loading logic resides in `neo4j_onto2ai_toolset/onto2ai_loader.py`.
Before running, ensure the `if __name__ == "__main__":` block is configured with the desired domains:
- `FND_DOMAIN`: Foundations
- `BE_DOMAIN`: Business Entities
- `BP_DOMAIN`: Business Processes
- `FBC_DOMAIN`: Financial Business and Commerce

### Execute the Load
Run the loader script from the root of the workspace using the following command to ensure the package and prefixes are correctly resolved:

```bash
export PYTHONPATH=$PYTHONPATH:.
python neo4j_onto2ai_toolset/onto2ai_loader.py
```

### Post-Load Verification
After loading, the script automatically:
- Materializes OWL restrictions into Neo4j relationships and properties.
- Cleans up duplicate relationships.
- Resolves namespaces using the controlled list in `neo4j_onto2ai_toolset/onto2schema/prefixes.py`.

## Troubleshooting
- **ShortenStrictException**: If this occurs, a new namespace was found. Add it to `neo4j_onto2ai_toolset/onto2schema/prefixes.py`.
- **Database Reset**: The loader script calls `reset_neo4j_db()` by default. Warn the user if they have existing data they wish to keep.
