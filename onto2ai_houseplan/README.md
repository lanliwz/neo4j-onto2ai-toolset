# Onto2AI House Plan Package

This package is the publishable house plan deliverable from Onto2AI Engineer.

It bundles the source ontology together with the current staging constraint artifact and the GeoJSON parcel importer used to populate `stagingdb`.

## Contents

- `ontology/HousePlan.rdf`
  - source RDF ontology for the house plan, parcel, address, survey, and GeoJSON geometry domain
- `staging/neo4j_constraint.cypher`
  - Neo4j constraints aligned to the finalized house plan classes
- `importers/geojson_import.py`
  - importer for loading parcel GeoJSON into the house plan staging model

## Python Access

Use the exported paths from `onto2ai_houseplan`:

```python
from onto2ai_houseplan import (
    ONTOLOGY_PATH,
    STAGING_CONSTRAINT_PATH,
    GEOJSON_IMPORTER_PATH,
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
2. Reload `stagingdb` with the house plan ontology.
3. Optionally import parcel GeoJSON into `stagingdb`.
4. Build the distribution.

Validation commands:

```bash
xmllint --noout ontology/HousePlan.rdf
python scripts/validate_ontology.py ontology/HousePlan.rdf
```

## Current Domain Scope

The current house plan package covers:

- house plan and building levels
- spaces, rooms, walls, doors, windows, and fixtures
- dimensions and material specifications
- U.S. site addresses
- GPS coordinates and survey references
- parcels and parcel metadata
- GeoJSON feature collections, features, polygon geometry, and boundary vertices

## Release Expectation

Before publishing, confirm:

- ontology RDF is current
- staging constraints are in sync
- build succeeds
- any intended parcel GeoJSON import completes successfully
