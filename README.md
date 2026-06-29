# Onto2AI Toolset

![Onto2AI Engineer Frontpage](./docs/assets/frontpage.svg)

Onto2AI Toolset is a generic toolkit for turning ontology knowledge into validated, implementation-ready application code models. It uses Neo4j, MCP, and AI-assisted workflows as supporting technologies for loading, exploring, extracting, shaping, and packaging ontology-driven schemas.

Current release: `v1.1.0`, the MCP-aligned domain adaptation baseline.

This repository is the toolset itself. Field-specific ontologies and models such as entitlement or parcel are examples of outputs that can be produced with the toolset, not the core product definition.

## Who This Toolset Is For
Onto2AI Toolset is for teams that need to turn ontology knowledge into usable application code models. It is useful when your source of truth is RDF/OWL, a public ontology such as FIBO, or a domain ontology you are designing, but your downstream users need concrete constraints, query context, generated code artifacts, smoke tests, and reviewable schema packages.

The main users are:
- ontology engineers who need to load, inspect, validate, and curate RDF/OWL content
- data modelers who need to convert ontology meaning into domain schema and application code contracts
- AI engineers who want an MCP-enabled ontology workbench for model extraction and schema assistance
- platform or application teams that want application code models packaged separately from the generic tooling

## How Users Can Use It
Users can work with Onto2AI Toolset in three complementary ways:

- **Workbench for ontology exploration**: load ontology files or known ontology presets into a graph-backed workbench, inspect classes and relationships, and use MCP tools or the client CLI to ask schema-oriented questions.
- **Modeller UI for review and refinement**: open the web UI to browse staged models, inspect schema graphs, run Cypher, and use the configured LLM provider to help refine model structure.
- **Packaging pipeline for application code models**: generate and validate RDF, Cypher constraints, query context, code-model artifacts, and smoke tests, then publish the resulting domain package independently from the core toolset.

A typical path is: install the toolset, configure the graph store and LLM credentials, load or stage an ontology, review it in the CLI/MCP server or Modeller UI, validate the generated artifacts, and package the finalized application code model for downstream use.

## Value Proposition
Onto2AI Toolset helps ontology engineers, data modelers, and AI engineers:
- load well-known ontologies into a graph-backed ontology workbench for inspection and reuse
- explore concepts, relationships, restrictions, rules, and axioms through MCP and graph tooling
- extract a focused subset of concepts from large ontologies such as FIBO and other standards
- use those subsets as building blocks for domain-specific or application-specific ontologies
- generate implementation artifacts such as database constraints, query context, and application code models
- keep ontology, schema, API, and runtime data aligned to a single semantic foundation

## Scope
This repository is scoped to ontology-centric workflows:
- ontology load and materialization
- ontology exploration and subset extraction
- MCP schema tooling and AI-assisted enhancement
- staging database enrichment and consolidation
- packaging finalized ontology deliverables
- Onto2AI Modeller web UI for review and operations

## Harness Modes
The toolset now starts from an explicit harness boundary so agentic work stays reliable instead of relying on prompts alone.

The four operating modes are:
- `ontology mode`: RDF-first ontology authoring with URI rules and `xmllint` validation
- `schema mode`: generate and validate Cypher, query context, and application code artifacts from ontology intent
- `dataset mode`: dataset-only smoke tests in `testdb` with no `owl__Class`, `rdf__type`, or `rdfs__subClassOf`
- `release mode`: package checks, versioning, milestone notes, and release discipline

See: [docs/harness/modes.md](./docs/harness/modes.md)
Checklist: [docs/harness/checklists.md](./docs/harness/checklists.md)
Preflight: `python scripts/harness_preflight.py <ontology|schema|dataset|release>`

## Typical Uses
This toolset is especially useful when you want to:
- inspect a large public ontology and understand its reusable conceptual structure
- extract a domain-relevant subset of concepts, properties, restrictions, and axioms
- build your own ontology on top of a trusted well-known ontology instead of starting from scratch
- generate implementation-ready schema artifacts from ontology-driven design
- let an AI engineer use MCP tools and graph-backed storage as an ontology workbench rather than treating an ontology as static RDF files

## Onto2AI Modeller
Onto2AI Modeller is the branded web studio for adapting industry ontologies into enterprise-ready target ontologies and application code models. It is a core part of Onto2AI Toolset and is designed for the workflow where a data or AI engineer starts from a trusted source ontology such as FIBO, extracts a focused subset, tunes it for an enterprise domain, validates it, prototypes generated artifacts, and prepares it for publication.

The Modeller UI is organized around four working surfaces:
- **Source Ontology**: search source ontologies such as FIBO, preview concept neighborhoods, collect extraction seeds, and stage selected domain subsets into the workspace. This surface is backed by the shared Onto2AI MCP server.
- **Target Ontology**: review the staged working copy as the ontology you are adapting and governing for your use case.
- **Semantic Interaction**: use the configured LLM provider to ask modelling questions, inspect schema decisions, and refine ontology structure with semantic context.
- **Native Query**: run direct Cypher queries for graph-native inspection and troubleshooting.

The center workspace uses **Ontology View** for source and target ontology graphs. UML Diagram and Pydantic Models are available for target ontology review and prototyping, but are disabled while working in Source Ontology because source discovery should stay focused on ontology graph context.

The Source Ontology workflow calls Onto2AI MCP over Server-Sent Events. By default the UI calls `http://127.0.0.1:8082/sse`; set `ONTO2AI_MCP_URL` when the MCP server runs elsewhere. Start the MCP server before using source search, preview, or extraction:

```bash
python -m neo4j_onto2ai_toolset.onto2ai_mcp http 8082
```

Before publishing, users can generate sample data, run end-to-end application data flow tests, and validate model quality so the resulting ontology package and application code model are ready for downstream distribution and implementation.

## Primary Workflow
1. Configure environment variables for the graph store, staging database, and model/API keys.
2. Load a well-known ontology or your own ontology data into the ontology workbench.
3. Start Onto2AI MCP in HTTP mode so Modeller can reuse the same ontology tools as agents and CLI workflows.
4. Use Modeller Source Ontology to search source concepts, preview neighborhoods, and collect extraction seeds.
5. Extract a source subset into the Target Ontology workspace.
6. Review, rename, simplify, and extend the target ontology for your enterprise or application domain.
7. Prototype implementation artifacts such as graph schema, Pydantic models, SHACL, and Cypher constraints.
8. Validate the implementation workflow with smoke tests and schema checks when applicable.
9. Publish the resulting ontology package and application code artifacts.

Example outcome:
- use the toolset to derive a field-specific package such as an entitlement application model package or a parcel application model package
- validate that package with domain-specific constraints, query context, and smoke tests
- distribute that package separately from the generic toolset

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
python -m neo4j_onto2ai_toolset.onto2ai_loader load --uri <ontology_iri>

# or load a known preset, such as the default FIBO domain slice
python -m neo4j_onto2ai_toolset.onto2ai_loader load --preset default-domains
```

The loader requires an explicit ontology URI or preset. You can use it to bring well-known ontologies into the graph-backed workbench, inspect them, and prepare them for subset extraction and downstream ontology design.

### Packaging
Build the core toolset from the repository root:

```bash
python -m build

ls -la dist/

python -m pip install --force-reinstall --no-deps dist/onto2ai_engineer-1.1.0-py3-none-any.whl
```

Build domain packages independently from their package directories:

```bash
cd onto2ai_entitlement
python -m build

cd ../onto2ai_parcel
python -m build
```

The root build publishes only `onto2ai-engineer`. Domain builds publish their own wheels, such as `onto2ai-entitlement` and `onto2ai-parcel`, without bundling the core toolset or other domain packages.

### Example Outputs
Using the toolset, you can produce field-specific deliverables such as:
- a customized ontology RDF
- a generated database constraint script
- a generated query context
- a generated application code model, such as a Pydantic model
- a domain-specific smoke test

Examples created with this toolset have included entitlement-oriented and parcel-oriented ontology packages. Those are domain outputs built by using the toolset, not the generic definition of the toolset itself, and they are not part of the generic install surface.

### Ontology Validation
```bash
python scripts/validate_ontology.py resource/ontology/www_onto2ai-toolset_com/ontology
```

### Harness Verification
```bash
python scripts/harness_run.py verify
python scripts/harness_run.py release
python scripts/harness_preflight.py ontology
python scripts/harness_verify_ontology.py
python scripts/harness_verify_mode_boundaries.py
python scripts/harness_verify_release.py
```

### Modeller
```bash
# Start the shared MCP server used by Source Ontology search and extraction
python -m neo4j_onto2ai_toolset.onto2ai_mcp http 8082

# Development mode with auto-reload for Python and UI asset changes
uv run --with-requirements requirements.txt \
  python -m onto2ai_modeller.main --reload --model gpt --host localhost --port 8180

# Installed console script
onto2ai-modeller --model gpt --host localhost --port 8180
```
Open: `http://localhost:8180`

### Demo Workflow
See: [demo/README4DEMO](./demo/README4DEMO)

## Reference Docs
- Loader: [README4LOADER.md](./README4LOADER.md)
- MCP: [README4ONTO2AI_MCP.md](./README4ONTO2AI_MCP.md)
- Harness Modes: [docs/harness/modes.md](./docs/harness/modes.md)
- Harness Checklists: [docs/harness/checklists.md](./docs/harness/checklists.md)
- Config Contract: [docs/configuration.md](./docs/configuration.md)
- Interface Contract: [docs/interface-contract.md](./docs/interface-contract.md)
- Milestone Plan: [docs/milestones/onto2ai-engineer-only.md](./docs/milestones/onto2ai-engineer-only.md)
- Release Notes: [docs/release-notes-v1.1.0.md](./docs/release-notes-v1.1.0.md)
- Release Notes: [docs/release-notes-v1.0.0.md](./docs/release-notes-v1.0.0.md)
- Release Notes: [docs/release-notes-v0.4.0.md](./docs/release-notes-v0.4.0.md)
- Demo Guide: [demo/README4DEMO](./demo/README4DEMO)

## Notes
- Root `main.py` is a compatibility shim and is deprecated.
- Canonical execution is package-first (`onto2ai-client`, `onto2ai-mcp`, `python -m ...`).
- Root `staging/` should be treated as a transient local workspace; finalized domain outputs should be packaged separately from the generic toolset.
