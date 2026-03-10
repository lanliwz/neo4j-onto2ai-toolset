# Staging Workspace

This directory is a transient local workspace for ontology review and enrichment.

It is not the permanent home for released artifacts.

Permanent entitlement release artifacts live under:

- `onto2ai_entitlement/ontology/`
- `onto2ai_entitlement/staging/`

Use this directory only for temporary regeneration output while refining `stagingdb`.

The canonical packaged smoke test is:

```bash
python -m onto2ai_entitlement.staging.schema_to_data_flow_smoke_test
```
