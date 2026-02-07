---
name: "Staging Database Expert"
description: "Specialized skill for managing, enriching, and consolidating the Neo4j staging database."
---
# Staging Database Expert Instructions

You are a master of the Staging Database (typically `stagingdb`). Use this skill to move data from the primary ontology to staging and to clean up/flatten the staging schema for production use.

## Core Operations

### 1. Staging Data
Use `staging_materialized_schema` to copy classes and relationships to the staging database.
- **Goal**: Create a self-contained subset of the ontology.
- **Options**: Set `flatten_inheritance=True` if you want to copy ancestor relationships directly to the child classes during extraction.

### 2. Consolidating Inheritance
If data is already in staging but still has parent-child links, use `consolidate_inheritance`.
- **Purpose**: Flatten the hierarchy so each class is fully descriptive on its own.
- **When**: Use this after staging classes if you didn't use `flatten_inheritance` during the initial copy.

### 3. Structural Consolidation
Use `consolidate_staging_db` to convert complex classes into simpler datatypes.
- **Workflow**: Identify classes that act purely as values (e.g., "card verification code") and transform them into `rdfs__Datatype` nodes.
- **Benefit**: This simplifies the final application schema and removes unnecessary node overhead.
- **Cleanup**: This tool automatically performs de-duplication of URIs, labels, and relationships.

## Best Practices
- **Isolation**: Always work on `stagingdb` to avoid polluting the main ontology.
- **Consistency**: Use camelCase for relationship types and lowercase with spaces for class labels.
- **Integrity**: Verify the results using standard Neo4j schema tools after each major transformation.
