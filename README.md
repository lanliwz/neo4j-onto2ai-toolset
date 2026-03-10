# Onto2AI Engineer

![Onto2AI Engineer Frontpage](./docs/assets/frontpage.svg)

Onto2AI Engineer is a focused toolkit for loading ontologies into Neo4j, interrogating/enhancing schema via MCP tools, and operating a staging workflow for production-oriented model shaping.

## Value Proposition
Onto2AI Engineer enables a model-once-serve-all approach for ontology-driven systems:
- Load well-known ontologies into a Neo4j ontology database.
- Materialize ontology semantics into graph structures that are operationally usable.
- Generate customized, industry-specialized schemas from those ontology foundations.
- Use generated schemas to create, load, and query Neo4j databases with LLM-assisted workflows.
- Keep API, UI, and data storage aligned to a single semantic model.

## Scope
This repository is scoped to Onto2AI workflows only:
- ontology load and materialization
- MCP schema tooling and AI-assisted enhancement
- staging database enrichment/consolidation
- Onto2AI Modeller web UI for review and operations

## Onto2AI Modeller
Onto2AI Modeller is an AI-assisted model-enrichment UI and a core part of Onto2AI Engineer. It helps users build industry-quality applications without requiring a full traditional team of product managers, architects, and engineers.

In the staging area, users can review and evolve models in ontology, UML, or object-oriented (class model) formats. You can inspect and refine classes, relationships, properties, and hierarchies, and use AI assistance to add or modify model elements.

Before publishing, users can generate sample data, run end-to-end application data flow tests, and validate model quality so the resulting model is ready for downstream distribution and implementation.

## Primary Workflow
1. Configure environment variables (Neo4j + model/API keys).
2. Load ontology data into Neo4j.
3. Run MCP server/client for schema extraction and enhancement.
4. Stage and consolidate schema for implementation.
5. Finalize schema design and review in Modeller UI.
6. Finalize `stagingdb` by running the dedicated packaged smoke test as the last step:
   - the smoke test always recreates and uses `testdb`
   - the smoke test keeps the sample data in `testdb` for review by default
   - `python -m onto2ai_entitlement.staging.schema_to_data_flow_smoke_test`
   - review the printed summary before distribution
7. Publish the ontology package:
   - build the distribution
   - publish the packaged entitlement ontology and finalized staging artifacts from `onto2ai_entitlement/`

## Quickstart
See: [docs/quickstart.md](./docs/quickstart.md)

## Operator Runbook
See: [docs/operator-runbook.md](./docs/operator-runbook.md)

## Core Commands

### Install
```bash
pip install .
```

### Client CLI
```bash
onto2ai-client
# or
python -m neo4j_onto2ai_toolset.onto2ai_client
```

### MCP Server
```bash
onto2ai-mcp
# HTTP mode
onto2ai-mcp http 8082
```

### Loader
```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader
```

### Packaging
```bash
# build source + wheel artifacts
python -m build

# artifacts output
ls -la dist/

# optional: install built wheel locally
python -m pip install --force-reinstall --no-deps dist/onto2ai_engineer-0.7.0-py3-none-any.whl
```

### Entitlement Package Contents
The distribution now includes a dedicated `onto2ai_entitlement` package that ships:
- the entitlement ontology RDF
- the finalized staging model JSON
- the generated Pydantic schema
- the generated Neo4j schema description
- the generated Neo4j constraint script
- the final smoke test script

After install, these artifacts are available from Python:

```python
from onto2ai_entitlement import (
    ONTOLOGY_PATH,
    STAGING_MODEL_PATH,
    STAGING_PYDANTIC_PATH,
    STAGING_QUERY_CONTEXT_PATH,
    STAGING_CONSTRAINT_PATH,
    SMOKE_TEST_PATH,
)
```

Root `staging/` is now treated as a transient local workspace only. Permanent entitlement artifacts live under `onto2ai_entitlement/`.

### Ontology Validation
```bash
python scripts/validate_ontology.py resource/ontology/www_onto2ai-toolset_com/ontology
```

### Modeller
```bash
onto2ai-modeller --model gemini --host localhost --port 8180
# or
python -m onto2ai_modeller.main --model gemini --host localhost --port 8180
```

### Demo Workflow
See: [demo/README4DEMO](./demo/README4DEMO)

## Reference Docs
- Loader: [README4LOADER.md](./README4LOADER.md)
- MCP: [README4ONTO2AI_MCP.md](./README4ONTO2AI_MCP.md)
- Config Contract: [docs/configuration.md](./docs/configuration.md)
- Interface Contract: [docs/interface-contract.md](./docs/interface-contract.md)
- Milestone Plan: [docs/milestones/onto2ai-engineer-only.md](./docs/milestones/onto2ai-engineer-only.md)
- Release Notes: [docs/release-notes-v0.4.0.md](./docs/release-notes-v0.4.0.md)
- Demo Guide: [demo/README4DEMO](./demo/README4DEMO)

## Notes
- Root `main.py` is a compatibility shim and is deprecated.
- Canonical execution is package-first (`onto2ai-client`, `onto2ai-mcp`, `python -m ...`).
