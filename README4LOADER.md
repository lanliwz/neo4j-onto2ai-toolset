# FIBO Ontology Loader

The `onto2ai_loader.py` module loads FIBO and related ontologies into Neo4j using `rdflib` and `rdflib-neo4j`, and now records a persistent load history for replay/reload workflows.

## Key Features

- **Recursive Part Discovery**: Supports loading complex specifications and domains by recursively discovering constituent parts using `dcterms:hasPart` relationships. This is essential for FIBO, which uses a hierarchical structure of domains and modules.
- **Domain-Based Loading**: Predefined presets for major FIBO domains (FND, BE, BP, FBC) and FIBO spec roots.
- **Namespace Shortening**: Uses the `HANDLE_VOCAB_URI_STRATEGY.SHORTEN` strategy to produce clean, readable URIs in Neo4j. All namespaces are explicitly managed in `onto2schema/prefixes.py`.
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

If you encounter a `ShortenStrictException`, it means a new namespace has been discovered that is not in the controlled list. Add the reported namespace to `neo4j_onto2ai_toolset/onto2schema/prefixes.py` to resolve the error.

## Core Functions

- `discover_and_load_parts(graph, root_uri)`: Recursively traverses `dcterms:hasPart`.
- `load_neo4j_db(onto_uri, format, discover=True)`: Loads the discovered or specified ontology into Neo4j.
- `execute_loader_run(...)`: Runs load/reset/materialization and records history.
- `reset_neo4j_db()`: Clears the Neo4j database and recreates the URI uniqueness constraint.
