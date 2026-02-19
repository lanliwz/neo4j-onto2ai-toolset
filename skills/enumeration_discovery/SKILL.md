---
name: "Enumeration Discovery"
description: "Instructions for automatically identifying and modeling ontology classes as Python Enums based on stagingdb content."
---
# Enumeration Discovery Skill

Use these instructions to automatically identify which `owl__Class` nodes in the `stagingdb` should be treated as enumerations in diagrams and code generation.

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

## Pydantic Modeling
When an enum class is identified, `generate_schema_code(target_type='pydantic')` now renders it as a Python `Enum` automatically when `owl__NamedIndividual` members exist via `rdf__type`.

### Verification Pattern
After regeneration, confirm:
- `staging/schema_models.py` contains `from enum import Enum`
- Enum classes are present (for example, `class Currency(Enum):`)
- Member constants are present (for example, `US_DOLLAR`, `MARRIED_FILING_JOINTLY`)

## UML Visualization
In UML diagrams, ensure these classes use the `«enumeration»` stereotype.

- **Flattening Rule**: When a class has a relationship to an enumeration, render it as an **Attribute** inside the class box rather than an Association arrow, unless the enum itself has complex metadata that needs visualization.

## Maintenance
- **New Members**: When adding new individuals to the database, always ensure they are linked to the correct class via `rdf__type`.
- **Deduplication**: Periodically run deduplication queries to ensure that enumeration members are not duplicated across different URIs.
- **Regeneration Workflow**: After enum changes, regenerate:
  1. `staging/full_schema_data_model.json` via `extract_data_model`
  2. `staging/schema_models.py` via `generate_schema_code(target_type='pydantic')`
  3. `staging/schema_description.md` via `generate_neo4j_schema_description`
  4. `staging/stagingdb_constraints_mcp.cypher` via `generate_neo4j_schema_constraint`
