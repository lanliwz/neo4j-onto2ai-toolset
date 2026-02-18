# Onto2AI Toolset

Onto2AI Toolset is a focused toolkit for loading ontologies into Neo4j, interrogating/enhancing schema via MCP tools, and operating a staging workflow for production-oriented model shaping.

## Scope
This repository is scoped to Onto2AI workflows only:
- ontology load and materialization
- MCP schema tooling and AI-assisted enhancement
- staging database enrichment/consolidation
- Onto2AI Modeller web UI for review and operations

## Primary Workflow
1. Configure environment variables (Neo4j + model/API keys).
2. Load ontology data into Neo4j.
3. Run MCP server/client for schema extraction and enhancement.
4. Stage and consolidate schema for implementation.
5. Review in Modeller UI.

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

### Modeller
```bash
cd onto2ai_modeller
python main.py --model gemini --port 8180
```

## Reference Docs
- Loader: [README4LOADER.md](./README4LOADER.md)
- MCP: [README4ONTO2AI_MCP.md](./README4ONTO2AI_MCP.md)
- MCP Server Notes: [MCP_README.md](./MCP_README.md)
- Config Contract: [docs/configuration.md](./docs/configuration.md)
- Interface Contract: [docs/interface-contract.md](./docs/interface-contract.md)
- Milestone Plan: [docs/milestones/onto2ai-toolset-only.md](./docs/milestones/onto2ai-toolset-only.md)

## Notes
- Root `main.py` is a compatibility shim and is deprecated.
- Canonical execution is package-first (`onto2ai-client`, `onto2ai-mcp`, `python -m ...`).
