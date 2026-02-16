---
description: financial application schema design and review
---

1. **Domain Analysis & Class Identification**
   Identify the core financial entities required for the application (e.g., `account`, `transaction`, `party`). Use the `get_neo4j_schema` tool on the FIBO ontology to explore relevant classes in the financial domain.

2. **Ontological Extraction**
   Use the `get_ontological_schema` tool to retrieve the raw ontological definitions and FIBO mappings for the identified classes. This provides insight into the underlying logic and constraints.

3. **Staging for Development**
   Extract the materialized schema and copy it to the staging database using the `staging_materialized_schema` tool. 
   - *Tip*: Set `flatten_inheritance=True` to automatically copy parent relationships if you want a self-contained model from the start.

---
### Iterative Design Loop (Repeat Steps 4-10 until finalized)

4. **Model Consolidation**
   Refine the model in the staging database:
   - **Inheritance Consolidation**: Use `consolidate_inheritance` for specific classes (e.g., `service provider`, `cardholder`) to flatten their hierarchy.
   - **Datatype Consolidation**: Use `consolidate_staging_db` to convert structural classes (like `address` or `open date`) into flat properties with technical XSD types.

5. **Schema Refinement**
   Prune and specialize the model for the target domain:
   - **Domain Specialization**: Rename generic classes to domain-specific ones (e.g., `conventional street address` -> `US street address`).
   - **Type Promotion (CRITICAL)**: Promote template-like `owl__NamedIndividual` nodes (e.g., specific tax forms or document types) to `owl__Class` nodes with `rdfs__subClassOf` links.
   - **Relationship Streamlining**: Remove redundant or instance-specific relationships (e.g., `defaultCountry`) from the class node to keep the schema decoupled from specific data instances.

6. **AI-Driven Schema Enhancement**
   Apply specific business logic or simplifications using the `enhance_schema` tool. 
   - **Ontological Consistency Standard**: All domain-specific attributes (rates, dates, money, statuses) MUST be modeled as **Relationships** to `rdfs__Datatype` nodes or `owl__Class` enumeration nodes. Avoid literal properties on class nodes.

7. **Enumeration Enrichment & Deduplication**
   Identify all `owl__Class` nodes used as enumerations (e.g., `filing status`, `report status`).
   - **Action**: Create `owl__NamedIndividual` members for these enums in `stagingdb`.
   - **Validation**: Ensure members are linked to the parent class via `rdf__type`.
   - **Semantic Deduplication (CRITICAL)**: Use the `merge_semantic_individuals` tool to consolidate any local placeholders (e.g., `married_joint`) with official FIBO standard individuals (e.g., `married filing jointly`) to prevent schema fragmentation.
   - **Metadata Enrichment (Global)**: Ensure all core Classes and Relationships have a populated `skos__definition`. Use AI-driven enrichment scripts (`enrich_class_definitions.py`, `enrich_rel_definitions.py`) to generate and apply missing descriptions.

8. **Structural Review & Validation**
   Verify the integrity of the design:
   - **Materialization Review**: Call `get_materialized_schema` on the staging database to inspect the final relationships.
   - **Graph Connectivity**: Use `read_neo4j_cypher` to run custom queries validating paths (e.g., between `Account` and `Payment`).
   - **SHACL Constraints**: Execute `generate_shacl_for_modelling` to create structural constraints that can be used for data validation.

9. **Architectural Visualization**
   Create visual documentation:
   - Generate Mermaid diagrams to represent the Class relationships.
   - **Comprehensive Coverage Principle**: Ensure all classes in the diagram are fully populated with their properties and core relationships.
   - **Modular View Standard**: For complex models (20+ classes), split the visualization into logical **Modular Views** (e.g., Core Domain, Foundation, Regulatory) using a **Carousel** format to maintain readability and font size.
   - **Rendering Rules**:
     - Render **Datatype and Enumeration relationships** (e.g., `hasTaxRate`, `hasStatus`) as **Properties** within the class boxes.
     - Render **Core Functional relationships** (e.g., `provides`, `filedBy`) as explicit **Arrows**.
   - Document key attributes and cardinalities.

10. **Designer Acceptance (User-in-the-Loop)**
   Share the visualization, validation results, and description of changes with the user.
   - **Action**: Use `notify_user` with `PathsToReview` including the UML diagram and walkthrough.
   - **Wait**: Do not proceed until the designer/user provides approval or requests further changes.

*Review the visualization and validation results. If the model requires further refinement, return to Step 4. Proceed to Step 11 only after receiving Designer Acceptance.*
---

11. **Code Generation**
    Translate the validated schema into production code using `generate_schema_code`:
    - **Comprehensive Coverage Principle**: 
      - Always include **all involved classes** (those linked via relationships) in the generation request to ensure no "shell" classes are produced.
      - Use Cypher queries to identify neighbor classes before calling the generation tool.
    - **Pydantic Bridge Standard (CRITICAL)**:
      - All core classes MUST inherit from a `SemanticModel` base class (including an optional `uri` field).
      - Use `Field(alias="...")` for all attributes and relationships to map Python field names to their ontological counterparts (Neo4j relationship types/properties). This enables automated compatibility with the `PydanticNeo4jBridge`.
      - Explicitly request `skos:definition` for every class to populate **Docstrings** and **Field Descriptions**.
    - **Output Types**:
      - **Pydantic/SQLAlchemy**: For application backends.
      - **SQL DDL**: For relational databases.
      - **Graph Schema Description**: Generate a detailed Markdown summary (`staging_schema.md`) using `get_ontology_schema_description`.
        - **Standard**: Must include `Data Type` and `Mandatory` status for all node properties.

12. **Data Model Archival & Documentation**
    Use the `extract_data_model` tool to generate a comprehensive JSON representation of the final schema.
    - **Physical Schema**: Generate `staging_schema_contraint.cypher` to enforce data integrity (existence constraints for mandatory properties) while keeping semantic metadata (labels, definitions, URIs) as comments.
    - **Documentation (Standard)**: Use `get_ontology_schema_description` to provide a human-readable Markdown summary (`staging_schema.md`).
        - **Alignment Heuristic (CRITICAL)**: Filter the "Node Labels (Classes)" table to only include **Effective Node Labels**. Use instance counts (`count > 0`), topological activity (outgoing relationships), and Pydantic Enum filtering to ensure the documented classes match the production Pydantic implementation.
        - **Metadata**: Must include `Data Type` and `Mandatory` status for all node properties.

13. **Integration & Round-Trip Validation**
    Perform a final validation gate before production deployment.
    - **Action**: Use the `PydanticNeo4jBridge` utility to save a complex instance of the domain model to `stagingdb` and extract it back.
    - **Validation**: Assert that the round-trip preserves all attributes, relationships, and metadata perfectly.
    - **Success Criteria**: 1:1 parity between the application code and the graph database schema.
