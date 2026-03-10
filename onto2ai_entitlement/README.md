# Onto2AI Entitlement Package

This package is the publishable entitlement deliverable from Onto2AI Engineer.

It bundles the source ontology together with the finalized staging artifacts used for implementation, validation, and review.

## Contents

- `ontology/Onto2AIEntitlement.rdf`
  - source RDF ontology for the entitlement domain
- `staging/full_schema_model.json`
  - extracted materialized schema model from `stagingdb`
- `staging/pydantic_schema_model.py`
  - generated Pydantic model view of the staging schema
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

Build the package from the repository root:

```bash
python -m build --no-isolation
```

Artifacts are written to `dist/`.

## Validation Flow

The intended finalization flow for this package is:

1. Validate the source ontology RDF.
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
- `row filter rule`
- `column mask rule`
- `relational database`
- `jdbc connection profile`
- `schema`
- `table`
- `column`
- `user type`
- `rule priority`

## Release Expectation

Before publishing, confirm:

- ontology RDF is current
- staging artifacts are regenerated and in sync
- build succeeds
- smoke test passes on `testdb`
- smoke-test summary is reviewed
- the package is published from `onto2ai_entitlement/`
