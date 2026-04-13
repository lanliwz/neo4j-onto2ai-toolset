# Ontology Loader

The `onto2ai_loader.py` module loads ontologies into Neo4j using `rdflib` and `rdflib-neo4j`, and records a persistent load history for replay and reload workflows.

Although it has strong support for FIBO and related standards, the loader is designed as a generic ontology-ingestion tool for anyone who wants to:
- load well-known ontologies into Neo4j
- inspect concepts, properties, axioms, and imports
- derive a smaller subset of reusable concepts from a large ontology
- use that subset as the foundation for a custom ontology or application schema

## Key Features

- **Recursive Part Discovery**: Supports loading complex specifications and domains by recursively discovering constituent parts using `dcterms:hasPart` relationships. This is especially useful for large, modular ontologies.
- **Domain-Based Loading**: Predefined presets for major FIBO domains (FND, BE, BP, FBC) and FIBO spec roots, while still supporting arbitrary ontology IRIs.
- **Namespace Shortening**: Uses the `HANDLE_VOCAB_URI_STRATEGY.SHORTEN` strategy to produce clean, readable URIs in Neo4j. All namespaces are explicitly managed in `onto2ai_core/prefixes.py`.
- **Robust Import Handling**: Automatically handles `owl:imports` and provides fallbacks for various RDF formats (RDF/XML, Turtle, NT).
- **Post-Load Materialization**: Includes functions to materialize object and datatype properties from OWL restrictions into Neo4j relationships and properties.
- **Load History Tracking**: Persists each run with:
  - loaded ontology IRI list,
  - destination Neo4j database/URI/user,
  - start/end timestamps and duration,
  - phase timings (reset/load/post-load),
  - replay metadata for `reload`.

## Usage

1. Configure environment variables (`NEO4J_MODEL_DB_URL`, `NEO4J_MODEL_DB_USERNAME`, `NEO4J_MODEL_DB_PASSWORD`, `NEO4J_MODEL_DB_NAME`).
2. Run loader commands:

```bash
# Default load (FND+BE+BP+FBC, discover enabled)
python -m neo4j_onto2ai_toolset.onto2ai_loader

# Explicit load command using a preset
python -m neo4j_onto2ai_toolset.onto2ai_loader load --preset fnd

# Load specific ontology IRI(s)
python -m neo4j_onto2ai_toolset.onto2ai_loader load \
  --uri https://spec.edmcouncil.org/fibo/ontology/FND/MetadataFND/FNDDomain

# Load any ontology IRI you want to inspect in Neo4j
python -m neo4j_onto2ai_toolset.onto2ai_loader load \
  --uri <ontology_iri>

# List recent load history
python -m neo4j_onto2ai_toolset.onto2ai_loader history --limit 10

# Show one run and all loaded ontology IRIs
python -m neo4j_onto2ai_toolset.onto2ai_loader history --run-id <run_id> --include-iris

# Reload a prior run from the saved loaded IRI list
python -m neo4j_onto2ai_toolset.onto2ai_loader reload --run-id <run_id> --source loaded

# Reload from local ontology files only (offline, no internet fetch)
python -m neo4j_onto2ai_toolset.onto2ai_loader reload \
  --run-id <run_id> --source loaded --local-files-only
```

Default history file:

```text
log/ontology_load_history.json
```

Override history path with:

```bash
--history-path <path>
```

or environment variable:

```bash
export ONTO2AI_LOADER_HISTORY_PATH=<path>
```

## Prefix Management

If you encounter a `ShortenStrictException`, it means a new namespace has been discovered that is not in the controlled list. Add the reported namespace to `neo4j_onto2ai_toolset/onto2ai_core/prefixes.py` to resolve the error.

## Why It Matters

For AI engineers and ontology engineers, the loader turns a large ontology into an explorable graph workspace. Once the ontology is loaded into Neo4j, you can:
- inspect its concept lattice and reusable modules
- trace object properties, datatype properties, restrictions, and subclass structure
- identify the subset you actually need
- use MCP tools and staging workflows to turn that subset into your own ontology package or implementation model

## Core Functions

- `discover_and_load_parts(graph, root_uri)`: Recursively traverses `dcterms:hasPart`.
- `load_neo4j_db(onto_uri, format, discover=True)`: Loads the discovered or specified ontology into Neo4j.
- `execute_loader_run(...)`: Runs load/reset/materialization and records history.
- `reset_neo4j_db()`: Clears the Neo4j database and recreates the URI uniqueness constraint.
