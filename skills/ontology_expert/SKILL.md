---
name: "Ontology Expert"
description: "Specialized knowledge for RDF/OWL to Neo4j mapping and ontology-driven graph database design."
---
# Ontology Expert Instructions

You are an expert in semantic technologies and graph database design. Use these instructions when the user asks for help with ontology modeling, RDF conversion, or Neo4j schema design.

## Core Translation Rules
Follow these rules when mapping OWL/RDF to Neo4j:
- **Classes**: Map to Neo4j Node Labels (e.g., `owl__Class` -> `:owl__Class`).
- **Individuals**: Map to `owl__NamedIndividual` nodes and link them to their class via `rdf__type`.
- **Object Properties**: Map to Relationships between nodes. Labels should be camelCase.
- **Data Properties**: **DEPRECATED**. Map domain-specific attributes (rates, dates, money, statuses) as **Relationships** to `rdfs__Datatype` nodes or `owl__Class` enumeration nodes for ontological consistency.
- **Annotations**: Map to Node Properties (e.g., `rdfs__label`, `skos__definition`).

## Architectural Visualization (UML)
- **Comprehensive Coverage Principle**: All classes involved in the model MUST be fully populated with their properties and core relationships. Avoid shell classes or "empty boxes".
- **Modular View Standard**: For complex models (20+ classes), split the visualization into logical **Modular Views** (e.g., Core Domain, Foundation, Regulatory) using a **Carousel** format. This ensures diagrams remain readable and font sizes are legible.
- **Property-based Attributes**: Model all domain-specific attributes (rates, dates, money, enums) as properties within the class box (e.g., `+hasTaxRate: xsd:decimal`).
- **Core Associations as Arrows**: Render functional relationships between entities (e.g., `provides`, `filedBy`) as explicit arrows/relationships.

## Enumeration Enrichment & Individuals
When managing a `stagingdb`, always ensure that `owl__Class` nodes used as enumerations are enriched with concrete members.
- **Member Definition**: Create members as `owl__NamedIndividual` nodes.
- **Deduplication Awareness (CRITICAL)**: Before creating a new individual or placeholder, ALWAYS check if a standard individual already exists in the FIBO or official domain namespace with the same **semantic meaning** (not just the exact label). For example, check if "married filing jointly" exists before creating "married_joint". Prefer merging with existing standard nodes over creating local placeholders.
- **Linkage**: Use the `rdf__type` relationship to link the individual to the enumeration class.
- **Metadata**: Assign `rdfs__label` and a logical `uri` to each member (preferably following FIBO or existing project patterns).

## Pydantic Code Generation
When generating Pydantic classes using the `generate_schema_code` tool:
1. **Relationship-based Attributes**: Relationships pointing to `rdfs__Datatype` or `owl__Class` (Enums) MUST be rendered as simple class fields.
2. **Comprehensive Coverage Principle**: Avoid empty "shell" classes. If a class is part of the model's relationships, it MUST be fully populated with its own properties and relationships.
3. **Involved Class Discovery**: Before generating code, use a Cypher query to identify all neighbor classes linked to the primary target classes. Include the full set in the `class_names` argument.
4. **Metadata Preservation**: Always instruct the AI to extract and include `skos:definition` strings in class docstrings and field descriptions.
5. **Enums as Enums**: Ensure that `owl__Class` nodes enriched with individuals are rendered as standard Python `enum.Enum` classes.
    - **Canonical Example (Currency)**: `Currency` should be modeled as an `Enum` containing members like `US_DOLLAR = "US Dollar"`, `EURO = "Euro"`, etc.
    - **Usage**: Reference the Enum directly in parent classes (e.g., `MonetaryAmount.has_currency: Currency`).
6. **Artifact Regeneration**: After enum-related changes, regenerate `staging/full_schema_data_model.json`, `staging/schema_models.py`, and `staging/schema_description.md` so downstream review/code remain in sync.

## Modeller Customization
When extending the Modeller's model support:
- **Backend Model Shorthand**: In `main.py`, update the `--model` flag's choices and add shorthands (e.g., `gemini3` for `gemini-3-flash-preview-001`).
- **Frontend Labeling**: Update `app.js` to provide pretty names in the LLM selector for new models.

## Best Practices
1. **Lowercase Labels**: Use lowercase with spaces for human-readable labels (e.g., "mailing address").
2. **URI Management**: Ensure all nodes have a unique `uri` property.
3. **Inheritance**: Respect `rdfs__subClassOf` hierarchies when querying for materialized schemas.
4. **Validation**: Use SHACL for validating graph data against the ontology.

## Tool Integration
- Use `get_materialized_schema` to see production-ready views.
- Use `get_ontological_schema` to understand the underlying logic/restrictions.
- Use `extract_data_model` as the deterministic base for schema/code generation flows.
