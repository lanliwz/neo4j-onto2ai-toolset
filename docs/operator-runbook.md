# Onto2AI Operator Runbook

## Standard Startup
1. Export environment variables per [configuration.md](./configuration.md).
2. Verify Neo4j connectivity and target DB names.
3. Start MCP server: `onto2ai-mcp`.
4. Start client/UI as needed:
   - CLI: `onto2ai-client`
   - UI: `onto2ai-modeller --port 8180`

## Core Operating Flows

### Load/Reload Ontology
```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader
```
Use when baseline ontology content must be refreshed.

Related commands:
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
4. Run generic harness verification:
   - `python scripts/harness_verify_ontology.py`
   - `python scripts/harness_verify_mode_boundaries.py`
5. Run any domain-specific schema validation or dataset smoke tests in the downstream package or workspace that owns them
6. Finalize schema design only after the generic harness checks and any downstream domain checks pass

### Finalization Workflow
Use this gate before publishing a schema for downstream API/UI/data usage:
1. Review model quality in Onto2AI Modeller (ontology, UML, and class-model views).
2. Ensure artifacts are regenerated and in sync in the canonical package or release location.
3. Run release verification:
   - `python scripts/harness_verify_release.py`
   - optional build check: `python scripts/harness_verify_release.py --build`
4. Verify representative query or smoke-test scenarios pass in the downstream package or workspace that owns them.
5. Build and publish the relevant package or release artifact from its canonical location.
6. Proceed to distribution only when generic harness checks, downstream validation, and package build all pass.

## Smoke Checks
- MCP stdio startup succeeds.
- MCP HTTP startup on `8082` succeeds.
- Client connects and lists tools.
- At least one class query returns schema data.
- Staging tools execute against `NEO4J_STAGING_DB_NAME`.
- Enum members appear in schema description Section 5.
- Pydantic output includes `Enum` classes when `owl__NamedIndividual` members exist.

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
