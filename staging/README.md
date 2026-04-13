# Staging Workspace

This directory is a transient local workspace for ontology review and enrichment.

It is not the permanent home for released artifacts.

Harness boundary for this workspace:

- ontology/schema validation belongs in `stagingdb`
- dataset-only smoke tests belong in `testdb`
- root `staging/` is temporary workspace, not canonical release source
- packaged domain outputs should live in their package directories

Permanent entitlement release artifacts live under:

- `onto2ai_entitlement/ontology/`
- `onto2ai_entitlement/staging/`

Use this directory only for temporary regeneration output while refining `stagingdb`.

The canonical packaged smoke test is:

```bash
python -m onto2ai_entitlement.staging.schema_to_data_flow_smoke_test
```

Dataset smoke-test rule:

- dataset test databases must not include ontology schema nodes such as `owl__Class`
- dataset test databases must not rely on ontology-only relationships such as `rdf__type` or `rdfs__subClassOf`
- validate schema artifacts separately, then load dataset-only sample instances for runtime smoke tests

Local parcel-slice workflow:

- schema validation in `stagingdb`: `python /Users/weizhang/github/neo4j-onto2ai-toolset/staging/stagingdb_schema_validation.py`
- dataset smoke test in `testdb`: `python /Users/weizhang/github/neo4j-onto2ai-toolset/staging/parcel_schema_smoke_test.py`
