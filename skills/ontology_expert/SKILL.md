---
name: "Ontology Expert"
description: "Specialized knowledge for RDF/OWL to Neo4j mapping and ontology-driven graph database design."
---
# Ontology Expert Instructions

You are an expert in semantic technologies and graph database design. Use these instructions when the user asks for help with ontology modeling, RDF conversion, or Neo4j schema design.

## Repository Operating Modes
Follow the repository harness boundary before making changes:
- **Ontology mode**: author or change RDF/OWL meaning. RDF is the source of truth. Validate with `xmllint --noout <rdf_file>`.
- **Schema mode**: generate or update Cypher constraints, query context, SHACL, Pydantic, or other application code models from ontology intent.
- **Dataset mode**: create or validate sample/runtime data. Use dataset databases such as `testdb`; do not load ontology schema nodes or ontology-only relationships into dataset databases.
- **Release mode**: package finalized artifacts from canonical package locations and keep version, notes, and metadata aligned.

## URI and File Convention
Unless a project explicitly overrides this convention:
- Base domain: `http://www.onto2ai-toolset.com/`
- Ontology base URI: `http://www.onto2ai-toolset.com/ontology/<domain>/<OntologyName>/`
- RDF header default namespace: `xmlns="http://www.onto2ai-toolset.com/ontology/<domain>/<OntologyName>/"`
- RDF header `xml:base`: same slash-terminated ontology base URI.
- RDF path: `resource/ontology/www_onto2ai-toolset_com/ontology/<domain>/<OntologyName>.rdf`
- Do not append `Ontology` to the file name or ontology URI name unless explicitly required.

For ontology changes, update RDF first, align Cypher/artifacts second, validate RDF syntax, then update docs if paths or names changed.

## Core Translation Rules
Follow these rules when mapping OWL/RDF to Neo4j:
- **Classes**: Map to Neo4j Node Labels (e.g., `owl__Class` -> `:owl__Class`).
- **Individuals**: Map to `owl__NamedIndividual` nodes and link them to their class via `rdf__type`.
- **Object Properties**: Map to relationships between nodes. Use lowerCamelCase predicate names for the relationship URI or graph edge, not noun labels. Prefer verb phrases such as `isSalesRepresentativeOf`, `hasClient`, or `linksToWealthManagementAccount`.
- **Data Properties**: **DEPRECATED**. Map domain-specific attributes (rates, dates, money, statuses) as **Relationships** to `rdfs__Datatype` nodes or `owl__Class` enumeration nodes for ontological consistency.
- **Annotations**: Map to Node Properties (e.g., `rdfs__label`, `skos__definition`).

## Architectural Visualization (UML)
- **Comprehensive Coverage Principle**: All classes involved in the model MUST be fully populated with their properties and core relationships. Avoid shell classes or "empty boxes".
- **Modular View Standard**: For complex models (20+ classes), split the visualization into logical **Modular Views** (e.g., Core Domain, Foundation, Regulatory) using a **Carousel** format. This ensures diagrams remain readable and font sizes are legible.
- **Property-based Attributes**: Model all domain-specific attributes (rates, dates, money, enums) as properties within the class box (e.g., `+hasTaxRate: xsd:decimal`).
- **Core Associations as Arrows**: Render functional relationships between entities (e.g., `provides`, `filedBy`) as explicit arrows/relationships.
- **Source vs Target UI Rule**: Source Ontology uses Ontology View only. UML Diagram and Pydantic Models are target-ontology review/prototyping views and should stay disabled for Source Ontology.

## Enumeration Enrichment & Individuals
When managing a `stagingdb`, always ensure that `owl__Class` nodes used as enumerations are enriched with concrete members.
- **Member Definition**: Create members as `owl__NamedIndividual` nodes.
- **Deduplication Awareness (CRITICAL)**: Before creating a new individual or placeholder, ALWAYS check if a standard individual already exists in the FIBO or official domain namespace with the same **semantic meaning** (not just the exact label). For example, check if "married filing jointly" exists before creating "married_joint". Prefer merging with existing standard nodes over creating local placeholders.
- **Linkage**: Use the `rdf__type` relationship to link the individual to the enumeration class.
- **Metadata**: Assign `rdfs__label` and a logical `uri` to each member (preferably following FIBO or existing project patterns).

## Application Code Model Generation
Pydantic is one supported output, not the goal of the toolset. When generating any application code model, keep the generated artifact aligned to ontology intent, relationship aliases, constraints, query context, and smoke tests.

When generating Pydantic classes using the `generate_schema_code` tool:
1. **Relationship-based Attributes**: Relationships pointing to `rdfs__Datatype` or `owl__Class` (Enums) MUST be rendered as simple class fields.
2. **Comprehensive Coverage Principle**: Avoid empty "shell" classes. If a class is part of the model's relationships, it MUST be fully populated with its own properties and relationships.
3. **Involved Class Discovery**: Before generating code, use a Cypher query to identify all neighbor classes linked to the primary target classes. Include the full set in the `class_names` argument.
4. **Metadata Preservation**: Always instruct the AI to extract and include `skos:definition` strings in class docstrings and field descriptions.
5. **Enums as Enums**: Ensure that `owl__Class` nodes enriched with individuals are rendered as standard Python `enum.Enum` classes.
    - **Canonical Example (Currency)**: `Currency` should be modeled as an `Enum` containing members like `US_DOLLAR = "US Dollar"`, `EURO = "Euro"`, etc.
    - **Usage**: Reference the Enum directly in parent classes (e.g., `MonetaryAmount.has_currency: Currency`).
6. **Artifact Regeneration**: After enum-related changes, regenerate transient local review artifacts under `staging/`, then copy finalized release artifacts into the relevant domain package staging folder (for example, `onto2ai_entitlement/staging/` or `onto2ai_parcel/staging/`) so downstream review/code remain in sync.

## Modeller Customization
When extending the Modeller's model support:
- **Config First**: Model lists and defaults should come from `onto2ai_modeller/config.yaml` so deployment can change them without code edits.
- **Backend Status**: Keep `/api/llm-status` and config parsing aligned with configured `available_models` and `default_model`.
- **Frontend Labeling**: Keep the LLM selector readable without hard-coding model availability.
- **LLM Errors**: Return meaningful user-facing errors for quota, missing key, unsupported model, and provider failures. `/api/chat` may return HTTP 200 even when the LLM call failed, so inspect the response body during troubleshooting.

## Best Practices
1. **Lowercase Labels**: Use lowercase with spaces for human-readable labels (e.g., "mailing address").
2. **URI Management**: Ensure all nodes have a unique `uri` property.
3. **Relationship Predicate Naming**: For object properties, the URI fragment should read as a directed predicate from domain to range. A good test is: `Domain predicate Range`, such as `Client isTrusteeOf Account`.
4. **Inheritance**: Respect `rdfs__subClassOf` hierarchies when querying for materialized schemas.
5. **Validation**: Use SHACL for validating graph data against the ontology.
6. **Identifier Display**: Treat URI values as identifiers. In UI surfaces, display them as text unless the user explicitly asks for external navigation.

## Tool Integration
- Use `get_materialized_schema` to see production-ready views.
- Use `get_ontological_schema` to understand the underlying logic/restrictions.
- Use `extract_data_model` as the deterministic base for schema/code generation flows.
- Use Source Ontology MCP tools (`search_ontology_concepts`, `preview_concept_neighborhood`, `extract_domain_subset`) for standards-first subset extraction.
