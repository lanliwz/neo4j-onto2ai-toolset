# Onto2AI Operator Runbook

## Standard Startup
1. Export environment variables per [configuration.md](./configuration.md).
2. Verify Neo4j connectivity and target DB names.
3. Start MCP server: `onto2ai-mcp`.
4. Start client/UI as needed:
   - CLI: `onto2ai-client`
   - UI: `cd onto2ai_modeller && python main.py --port 8180`

## Core Operating Flows

### Load/Reload Ontology
```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader
```
Use when baseline ontology content must be refreshed.

### Schema Interrogation
Use MCP tools:
- `get_materialized_schema`
- `get_ontological_schema`
- `extract_data_model`

### Schema Enhancement
Use MCP tools:
- `enhance_schema`
- `generate_schema_code`
- `generate_shacl_for_modelling`

### Staging Operations
Use MCP tools:
- `staging_materialized_schema`
- `consolidate_inheritance`
- `consolidate_staging_db`
- `get_ontology_schema_description`

## Smoke Checks
- MCP stdio startup succeeds.
- MCP HTTP startup on `8082` succeeds.
- Client connects and lists tools.
- At least one class query returns schema data.
- Staging tools execute against `NEO4J_STAGING_DB_NAME`.

## Common Failures

### Missing DB credentials
Symptom: startup/connect errors.
Action: verify `NEO4J_MODEL_DB_*` variables.

### Model/provider mismatch
Symptom: model init failure.
Action: set `LLM_MODEL_NAME` to supported value and ensure matching API key.

### Namespace shortening errors during load
Symptom: `ShortenStrictException`.
Action: extend prefix map in `neo4j_onto2ai_toolset/onto2schema/prefixes.py`.

## Migration Notes
- Prefer package/module entrypoints only.
- Root `main.py` is deprecated and should not be used in new automation.
