---
description: cleanup and validate staging database for payment system
---

1. **Identify and Remove Noise**
   Execute a Cypher query to detach and delete unrelated ontology classes (Regulatory, Metadata, Auxiliary structural nodes) and their instances from `stagingdb`.
   
2. **Consolidate Inherited Relationships**
   Use the `consolidate_inheritance` tool for core classes like `service provider` to flatten parent relationships directly onto the class in `stagingdb`.

3. **Consolidate Structural Entities into Datatypes**
   Convert structural classes (e.g., `address`, `open date`, `close date`) into flat datatypes using the `consolidate_staging_db` tool with appropriate technical XSD types.

4. **Validate Materialized Schema**
   Retrieve the `get_materialized_schema` for core payment classes (`credit card account`, `cardholder`, `payment`, `merchant`, `economic transaction`) and verify all core connections and properties are present.

5. **Generate Architectural Documentation**
   Optionally generate a UML Class Diagram or SHACL shapes using the specialized tools to document the final validated state.
