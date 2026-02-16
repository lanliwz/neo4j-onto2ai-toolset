---
description: cleanup and validate staging database for payment system
---

1. **Identify and Remove Noise**
   Execute a Cypher query to detach and delete unrelated ontology classes (Regulatory, Metadata, Auxiliary structural nodes) and their instances from `stagingdb`.

2. **Flatten Hierarchy by Removing Generic Parents**
   Identify classes that only contain metadata (e.g., `agent`, `document`, `identifier`) and are extended by other classes. Re-parent their subclasses directly to the parent class and delete the generic node.
   
3. **Consolidate Inherited Relationships**
   Use the `consolidate_inheritance` tool for core classes like `service provider` to flatten parent relationships directly onto the class in `stagingdb`.

4. **Consolidate Structural Entities into Datatypes**
   Convert structural classes (e.g., `address`, `open date`, `close date`) into flat datatypes using the `consolidate_staging_db` tool with appropriate technical XSD types.

5. **Validate Materialized Schema**
   Retrieve the `get_materialized_schema` for core payment classes (`credit card account`, `cardholder`, `payment`, `merchant`, `economic transaction`) and verify all core connections and properties are present.

6. **Deduplicate Named Individuals**
   Identify `owl__NamedIndividual` nodes with duplicate `rdfs__label` strings across local (`onto2ai`) and official (`fibo`) namespaces. Use `apoc.refactor.mergeNodes` to consolidate them into the official FIBO version.

7. **Enrich Metadata Definitions**
   Identify nodes (Classes) and Relationships missing `skos__definition` in `stagingdb`. Use AI (LLM) to generate semantic descriptions based on URI, labels, and topology context to ensure a high-quality, documented schema.

8. **Generate Full Schema Representation**
   Use the `get_ontology_schema_description` tool to produce a comprehensive Markdown documentation (`staging_schema.md`).
   - **Requirement**: Documentation must include `Data Type` and `Mandatory` status (cardinality) for all node properties.

9. **Archive Schema Constraints**
   Generate a `staging_schema_contraint.cypher` file (e.g., via `generate_archival_cypher.py`) to preserve physical schema constraints. 
   - **Rule**: Separate metadata (definitions/URIs as comments) from data schema (existence constraints for mandatory properties).

10. **Verify Domain Model Parity**
    Finalize the validation by ensuring the generated Pydantic models are perfectly synchronized with the graph.
    - **Step**: Use the `PydanticNeo4jBridge` utility to run a round-trip test (Save Object -> Extract Object -> Assert Equality).
    - **Goal**: Confirm that the ontological aliases in the code correctly map to the database relationships.
