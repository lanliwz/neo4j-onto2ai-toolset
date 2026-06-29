# Onto2AI Parcel Package

This package is the publishable parcel deliverable from Onto2AI Engineer.

It bundles the finalized parcel ontology together with the generated implementation artifacts used for validation, query context, application code modeling, and smoke testing.

The RDF ontology is the source of truth for the package. It includes the parcel application profile, required-field/cardinality restrictions, direct reuse of FIBO real-property/address concepts, and direct reuse of LCC country and U.S. subdivision reference data.

High-confidence duplicate imported classes are canonicalized to OMG Commons concepts in the parcel profile through `owl:equivalentClass` bridges. This includes the LCC/FIBO location overlaps plus exact or near-exact FIBO/Commons and LCC/Commons duplicates such as business center, county, municipality, membership, organization identification scheme, code set, and country subdivision. Downstream review can reason from one canonical foundation while still preserving source ontology provenance.

## Contents

- `ontology/Parcel.rdf`
  - source RDF ontology for the finalized parcel domain
- `staging/pydantic_parcel_model.py`
  - generated application code model aligned to the finalized parcel schema; this package currently uses Pydantic as the generated model format and includes the full parcel attribute surface from the RDF
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

Build this domain package independently from its package directory:

```bash
cd onto2ai_parcel
python -m build
```

Artifacts are written to `dist/`.

This build publishes only the parcel domain package (`onto2ai-parcel`).
It does not package the core Onto2AI toolset or other domain application models.

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
- source parcel identifiers, district/section/block/lot fields, municipality, postal, land-use, status, date, and acreage attributes
- U.S. postal address
- FIBO physical address alignment without a duplicate local address wrapper
- Commons alignment with equivalent-class bridges for high-confidence imported LCC/FIBO duplicates
- LCC country and country subdivision reference data, represented as `hasCountry` and `hasSubdivision` relationships in the graph contract
- geometry and polygon geometry
- GPS coordinates and boundary vertices
- GeoJSON features and feature collections
