# Onto2AI Entitlement Package

This package is the publishable entitlement deliverable from Onto2AI Engineer.

It bundles the source ontology together with the finalized staging artifacts used for implementation, validation, and review.

## Contents

- `ontology/Onto2AIEntitlement.rdf`
  - packaged copy of the source RDF ontology for the entitlement domain
- `../resource/ontology/www_onto2ai-toolset_com/ontology/entitlement/Onto2AIEntitlement.rdf`
  - URI-mirrored source RDF path used by repository-level ontology workflows
- `staging/full_schema_model.json`
  - extracted materialized schema model from `stagingdb`
- `staging/pydantic_schema_model.py`
  - generated application code model view of the staging schema; this package currently uses Pydantic as the generated model format
- `staging/neo4j_query_context.md`
  - generated schema description for review and LLM/query context
- `staging/neo4j_constraint.cypher`
  - generated Neo4j constraints for the finalized schema
- `staging/schema_to_data_flow_smoke_test.py`
  - end-to-end smoke test for the finalized schema

## Python Access

Use the exported paths from `onto2ai_entitlement`:

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

## Build

Build this domain package independently from its package directory:

```bash
cd onto2ai_entitlement
python -m build
```

Artifacts are written to `dist/`.

This build publishes only the entitlement domain package (`onto2ai-entitlement`).
It does not package the core Onto2AI toolset or other domain application models.

## Validation Flow

The intended finalization flow for this package is:

1. Update and validate the source ontology RDF.
2. Regenerate the staging artifacts from `stagingdb`.
3. Build the distribution.
4. Run the smoke test as the last step.
5. Publish the ontology package only after the smoke test passes.

Smoke test command:

```bash
python staging/schema_to_data_flow_smoke_test.py
```

Smoke test behavior:

- always recreates and uses `testdb`
- applies the generated Neo4j constraints
- loads representative entitlement sample data
- validates required properties and core relationships
- keeps the sample data in `testdb` by default for review

## Review Queries

Inspect retained smoke-test data:

```cypher
MATCH (n {sampleTag: 'schema_workflow'}) RETURN labels(n), n
```

Clean retained smoke-test data:

```cypher
MATCH (n {sampleTag: 'schema_workflow'}) DETACH DELETE n
```

## Current Domain Scope

The current entitlement package covers:

- `user`
- `policy group`
- `policy`
- `entitlement rule`
- `row filter rule`
- `column mask rule`
- `relational database`
- `jdbc connection profile`
- `schema`
- `table`
- `column`
- `user type`
- `rule priority`
- `filter action`
- `match mode`
- `comparison operator`
- `value source type`
- `deny behavior`
- `mask action`
- `masking method`
- `fallback behavior`
- `sensitivity classification`

## Release Expectation

Before publishing, confirm:

- URI-mirrored ontology RDF and packaged ontology RDF are current and identical
- staging artifacts are regenerated and in sync
- build succeeds
- smoke test passes on `testdb`
- smoke-test summary is reviewed
- the package is published from `onto2ai_entitlement/`
