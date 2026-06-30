---
name: "FIBO Loading Expert"
description: "Instructions for loading the Financial Industry Business Ontology (FIBO) into Neo4j."
---
# FIBO Loading Expert Instructions

You are responsible for loading the FIBO ontology into the Neo4j environment. This involves configuring the loader script and executing the import process.

## Loading Process

### Configure the Loader
The core loading logic resides in `neo4j_onto2ai_toolset/onto2ai_loader.py`.

Use the package CLI instead of editing the `if __name__ == "__main__":` block. The loader now expects either an explicit ontology URI or a known preset.

Common commands:

```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader load --uri <ontology_iri>
python -m neo4j_onto2ai_toolset.onto2ai_loader load --preset default-domains
```

Use the default FIBO domain slice as the normal starting point for industry-ontology exploration. Expand domains only when the user needs a broader source landscape.

### Execute the Load
Run from the root of the workspace so package imports and prefixes are correctly resolved:

```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader load --preset default-domains
```

### Post-Load Verification
After loading, the script automatically:
- Materializes OWL restrictions into Neo4j relationships and properties.
- Cleans up duplicate relationships.
- Resolves namespaces using the controlled list in `neo4j_onto2ai_toolset/onto2ai_core/prefixes.py`.

## Troubleshooting
- **ShortenStrictException**: If this occurs, a new namespace was found. Add it to `neo4j_onto2ai_toolset/onto2ai_core/prefixes.py`.
- **Database Reset**: Confirm the target database before any reset or reload. Source ontology loading is destructive when reset flags are used.
- **Source vs Target**: FIBO is a source ontology. Use MCP/Modeller Source Ontology to search and extract a focused subset, then stage and curate the target ontology separately.
- **Post-load Check**: After loading, use `search_ontology_concepts` or `list_model_classes` against the loaded database to confirm expected concepts are present.
