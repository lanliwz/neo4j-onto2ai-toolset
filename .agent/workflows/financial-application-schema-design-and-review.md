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
### Iterative Design Loop (Repeat Steps 4-7 until finalized)

4. **Model Consolidation**
   Refine the model in the staging database:
   - **Inheritance Consolidation**: Use `consolidate_inheritance` for specific classes (e.g., `service provider`, `cardholder`) to flatten their hierarchy.
   - **Datatype Consolidation**: Use `consolidate_staging_db` to convert structural classes (like `address` or `open date`) into flat properties with technical XSD types.

5. **AI-Driven Schema Enhancement**
   Apply specific business logic or simplifications using the `enhance_schema` tool. Provide clear instructions for modifications (e.g., "Flatten the balance structure into a single decimal field").

6. **Structural Review & Validation**
   Verify the integrity of the design:
   - **Materialization Review**: Call `get_materialized_schema` on the staging database to inspect the final relationships.
   - **Graph Connectivity**: Use `read_neo4j_cypher` to run custom queries validating paths (e.g., between `Account` and `Payment`).
   - **SHACL Constraints**: Execute `generate_shacl_for_modelling` to create structural constraints that can be used for data validation.

7. **Architectural Visualization**
   Create visual documentation:
   - Generate Mermaid diagrams to represent the UML Class relationship.
   - Document key attributes and cardinalities.

*Review the visualization and validation results. If the model requires further refinement, return to Step 4. Proceed to Step 8 only when the stagingdb model is finalized.*
---

8. **Code Generation**
   Translate the validated schema into production code using `generate_schema_code`:
   - **Pydantic/SQLAlchemy**: For application backends.
   - **SQL DDL**: For relational databases.
   - **Cypher Scripts**: For graph database setup.

9. **Data Model Archival**
   Use the `extract_data_model` tool to generate a comprehensive JSON representation of the final schema for documentation, peer review, or integration into external tools.
