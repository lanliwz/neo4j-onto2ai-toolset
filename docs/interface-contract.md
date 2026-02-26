# Onto2AI Engineer Interface Contract

This document defines stable runtime interfaces for the `onto2ai-engineer` milestone.

## Canonical Commands

### Client CLI
- `onto2ai-client`
- Equivalent module form: `python -m neo4j_onto2ai_toolset.onto2ai_client`

### MCP Server
- `onto2ai-mcp`
- HTTP mode: `onto2ai-mcp http 8082`
- Equivalent module form: `python -m neo4j_onto2ai_toolset.onto2ai_mcp [http <port>]`

### Loader
- Module form: `python -m neo4j_onto2ai_toolset.onto2ai_loader`

## Stable MCP Tool Surface
The following tools are part of the stabilized Onto2AI MCP surface:
- `get_materialized_schema`
- `get_ontological_schema`
- `extract_data_model`
- `generate_schema_code`
- `generate_shacl_for_modelling`
- `staging_materialized_schema`
- `consolidate_inheritance`
- `consolidate_staging_db`
- `generate_neo4j_schema_description`
- `generate_neo4j_schema_constraint`

## Deprecated Interfaces and Migration

- Deprecated: `python main.py`
  - Migration: `onto2ai-client` or `python -m neo4j_onto2ai_toolset.onto2ai_client`

- Removed as canonical: `neo4j-chatbot` console script
  - Migration: `onto2ai-client`

- Archived legacy chatbot modules
  - `neo4j_onto2ai_toolset/schema_chatbot/` and `neo4j_onto2ai_toolset/display_dataflow.py`
  - Archived under `archive/out_of_scope/2026-02-22/schema_chatbot/`

- Archived legacy local agent workflows
  - `.agent/workflows/*`
  - Archived under `archive/out_of_scope/2026-02-22/agent-workflows/`

- Deprecated path-based script calls for MCP/loader
  - Migration: use `onto2ai-mcp` or `python -m ...` module execution

## Compatibility Window
- Deprecated interfaces remain temporarily as compatibility shims where present.
- New automation and docs should use canonical commands only.
