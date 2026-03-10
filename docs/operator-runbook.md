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
After enum, `owl__NamedIndividual`, `rdf__type`, or mandatory-relationship changes:
1. Regenerate transient local review artifacts as needed under `staging/`
2. Copy finalized entitlement artifacts into `onto2ai_entitlement/staging/`
3. Run end-to-end packaged schema test: `python -m onto2ai_entitlement.staging.schema_to_data_flow_smoke_test`
   - the script always recreates and uses `testdb`
   - it keeps the sample data in `testdb` for review by default
   - review the printed summary as the last step of finalization
4. Confirm the workflow scenario exists in the test graph:
   - person/taxpayer has residence/address
   - W-2 is issued by organization/employer and issued to person
   - Form 1040 is submitted by taxpayer to the IRS
5. Finalize schema design only after the schema workflow test passes and the summary is reviewed.
6. Publish the ontology package from `onto2ai_entitlement/`.

### Finalization Workflow
Use this gate before publishing a schema for downstream API/UI/data usage:
1. Review model quality in Onto2AI Modeller (ontology, UML, and class-model views).
2. Ensure artifacts are regenerated and in sync:
   - `onto2ai_entitlement/staging/full_schema_model.json`
   - `onto2ai_entitlement/staging/pydantic_schema_model.py`
   - `onto2ai_entitlement/staging/neo4j_query_context.md`
   - `onto2ai_entitlement/staging/neo4j_constraint.cypher`
3. Run the end-to-end smoke test:
   - `python -m onto2ai_entitlement.staging.schema_to_data_flow_smoke_test`
   - it always recreates and uses `testdb`
   - it keeps the sample data in `testdb` for review by default
4. Verify representative query scenarios pass against staging.
5. Build and publish the ontology package from `onto2ai_entitlement/`.
6. Proceed to distribution only when the smoke test, query checks, and package build pass.

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
