# Onto2AI Operator Runbook

## Standard Startup
1. Export environment variables per [configuration.md](./configuration.md).
2. Verify Neo4j connectivity and target DB names.
3. Start MCP server: `onto2ai-mcp`.
4. Start client/UI as needed:
   - CLI: `onto2ai-client`
   - UI: `onto2ai-modeller --port 8180`
   - UI development with auto-reload: `uv run --with-requirements requirements.txt python -m onto2ai_modeller.main --reload --model gpt --port 8180`

## Core Operating Flows

### Load/Reload Ontology
```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader load --uri <ontology_iri> --no-reset
```
Use when baseline ontology content must be refreshed.

`load` resets the configured target database by default. Keep `--no-reset` for additive loading; use `--reset` only after confirming the target database and intentionally replacing its contents.

Related commands:
- Load default FIBO domain slice: `python -m neo4j_onto2ai_toolset.onto2ai_loader load --preset default-domains --no-reset`
- List history: `python -m neo4j_onto2ai_toolset.onto2ai_loader history --limit 10`
- Reload prior run: `python -m neo4j_onto2ai_toolset.onto2ai_loader reload --run-id <run_id> --source loaded`
- Reload local-only (no network fetch): `python -m neo4j_onto2ai_toolset.onto2ai_loader reload --run-id <run_id> --source loaded --local-files-only`

### Schema Interrogation
Use MCP tools:
- `get_materialized_schema`
- `get_ontological_schema`
- `extract_data_model`

### Schema Generation
Use MCP tools:
- `generate_schema_code`
- `generate_shacl_for_modelling`

### Staging Operations
Use MCP tools:
- `staging_materialized_schema`
- `consolidate_inheritance`
- `consolidate_staging_db`
- `generate_neo4j_schema_description`
- `generate_neo4j_schema_constraint`

### Artifact Regeneration Workflow
After ontology or schema changes:
1. Run preflight for the intended mode:
   - `python scripts/harness_preflight.py ontology`
   - `python scripts/harness_preflight.py schema`
   - `python scripts/harness_preflight.py dataset`
   - `python scripts/harness_preflight.py release`
2. Regenerate transient local review artifacts as needed under `staging/`
3. Keep finalized domain artifacts in their canonical package or release paths, not in transient root `staging/`
4. Run portable harness verification:
   - `python scripts/harness_run.py verify`
5. Before release, run live schema and isolated dataset validation for the selected domain:
   - `python scripts/harness_run.py verify --live --domain entitlement`
6. Build a release only through the enforced release flow:
   - `python scripts/harness_run.py release --domain entitlement --package entitlement`

### Finalization Workflow
Use this gate before publishing a schema for downstream API/UI/data usage:
1. Review model quality in Onto2AI Modeller (ontology, UML, and class-model views).
2. Ensure artifacts are regenerated and in sync in the canonical package or release location.
3. Run portable checks with `python scripts/harness_run.py verify`.
4. Run the matching live release gate, for example `python scripts/harness_run.py release --domain parcel --package parcel`.
5. Publish only the artifacts produced and inspected by that release gate.
6. Proceed to distribution only when generic harness checks, downstream validation, and package build all pass.

## Smoke Checks
- MCP stdio startup succeeds.
- MCP HTTP startup on `8082` succeeds.
- Client connects and lists tools.
- At least one class query returns schema data.
- Staging tools execute against `NEO4J_STAGING_DB_NAME`.
- Enum members appear in schema description Section 5.
- Generated application code model output includes enumeration classes when `owl__NamedIndividual` members exist. The current generated Python format uses Pydantic.

## Common Failures

### Missing DB credentials
Symptom: startup/connect errors.
Action: verify `NEO4J_MODEL_DB_*` variables.

### Model/provider mismatch
Symptom: model init failure.
Action: set `LLM_MODEL_NAME` to supported value and ensure matching API key.

### Namespace shortening errors during load
Symptom: `ShortenStrictException`.
Action: extend prefix map in `neo4j_onto2ai_toolset/onto2ai_core/prefixes.py`.

## Migration Notes
- Prefer package/module entrypoints only.
- Root `main.py` is deprecated and should not be used in new automation.
