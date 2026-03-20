# Onto2AI Parcel Package

This package is the publishable parcel deliverable from Onto2AI Engineer.

It bundles the finalized parcel ontology together with the generated implementation artifacts used for Neo4j validation, query context, application modeling, and smoke testing.

## Contents

- `ontology/Parcel.rdf`
  - source RDF ontology for the finalized parcel domain
- `staging/pydantic_parcel_model.py`
  - generated Pydantic model aligned to the finalized parcel schema
- `staging/neo4j_query_context.md`
  - generated parcel schema description for query/context use
- `staging/neo4j_constraint.cypher`
  - generated Neo4j constraints for the finalized parcel schema
- `staging/parcel_schema_smoke_test.py`
  - dataset-oriented smoke test for the finalized parcel package

## Python Access

Use the exported paths from `onto2ai_parcel`:

```python
from onto2ai_parcel import (
    ONTOLOGY_PATH,
    STAGING_PYDANTIC_PATH,
    STAGING_QUERY_CONTEXT_PATH,
    STAGING_CONSTRAINT_PATH,
    SMOKE_TEST_PATH,
)
```

## Build

Build the package from the repository root:

```bash
python setup.py sdist bdist_wheel
```

Artifacts are written to `dist/`.

## Validation Flow

The intended finalization flow for this package is:

1. Validate the source ontology RDF.
2. Confirm the packaged parcel artifacts are in sync with the finalized staging/schema workflow.
3. Run the dataset smoke test against `testdb`.
4. Build the distribution.

Validation commands:

```bash
xmllint --noout ontology/Parcel.rdf
python staging/parcel_schema_smoke_test.py
```

Dataset rule:

- validate ontology and schema in `stagingdb`
- keep `testdb` dataset-oriented
- do not load ontology-only nodes such as `owl__Class` into the dataset database
- do not materialize ontology-only relationships such as `rdf__type` or `rdfs__subClassOf` in dataset smoke tests

## Current Domain Scope

The current parcel package covers:

- parcel
- address
- U.S. postal address
- country and country subdivision reference data
- geometry and polygon geometry
- GPS coordinates and boundary vertices
- GeoJSON features and feature collections
