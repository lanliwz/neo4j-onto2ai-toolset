---
name: "Enumeration Discovery"
description: "Instructions for identifying ontology enumeration classes and rendering them in generated application models."
---
# Enumeration Discovery Skill

Use these instructions to automatically identify which `owl__Class` nodes in the schema/model database, normally `stagingdb`, should be treated as enumerations in diagrams and generated application code models.

## Discovery Logic
An enumeration is defined as an `owl__Class` that has one or more `owl__NamedIndividual` members linked via `rdf__type`.

### Cypher Identification Pattern
Run this query to find active enums in the staging database:
```cypher
MATCH (c:owl__Class)<-[:rdf__type]-(i:owl__NamedIndividual)
WITH c, count(i) as memberCount, collect(i.rdfs__label)[0..5] as sampleMembers
WHERE memberCount > 0
RETURN c.rdfs__label as className, c.uri as uri, memberCount, sampleMembers
ORDER BY memberCount DESC
```

## Application Model Rendering
When an enum class is identified, generated application code models should render it as a native enumeration type when the target language supports one.

For Pydantic output, `generate_schema_code(target_type='pydantic')` renders it as a Python `Enum` automatically when `owl__NamedIndividual` members exist via `rdf__type`.

### Verification Pattern
After regeneration, confirm:
- the generated Pydantic artifact contains `from enum import Enum`
- Enum classes are present (for example, `class Currency(Enum):`)
- Member constants are present (for example, `US_DOLLAR`, `MARRIED_FILING_JOINTLY`)

## UML Visualization
In UML diagrams, ensure these classes use the `«enumeration»` stereotype.

- **Flattening Rule**: When a class has a relationship to an enumeration, render it as an **Attribute** inside the class box rather than an Association arrow, unless the enum itself has complex metadata that needs visualization.

## Maintenance
- **New Members**: When adding new individuals to the database, always ensure they are linked to the correct class via `rdf__type`.
- **Deduplication**: Periodically run deduplication queries to ensure that enumeration members are not duplicated across different URIs.
- **Schema vs Dataset Boundary**: `rdf__type` links are valid in `stagingdb` for schema/model enumeration discovery. Do not load ontology-only `rdf__type` links into dataset databases unless the task explicitly requires schema validation there.
- **Regeneration Workflow**: After enum changes, regenerate transient local review artifacts under `staging/`, then copy finalized artifacts into the relevant domain package staging folder before release.
