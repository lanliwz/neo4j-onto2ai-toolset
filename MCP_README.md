# Neo4j Ontology MCP Server

This MCP server provides a powerful set of tools to interrogate, enhance, and materialize schemas from an OWL ontology loaded into Neo4j. It supports the **Model Context Protocol** (MCP), enabling seamless integration with AI agents.

## Features

### 1. Schema Exploration
- **`get_materialized_schema`**: Returns a flattened, production-ready view of a class.
    - **Formatting**: Rendered as two Markdown tables. Section 1 links **Labels** to URIs; Section 2 links **Relationships** to URIs.
- **`get_ontological_schema`**: Returns raw logic (Restrictions, domain/range).
    - **Formatting**: Rendered as two Markdown tables. Section 1 links **Labels** to URIs; Section 2 links **Properties** to URIs.

### 2. Schema Manager (AI-Powered)
- **`enhance_schema`**: Auto-extracts from ontology and modifies a `DataModel` via natural language (e.g., "Add middleName").
- **`generate_schema_code`**: Generates production-ready code (SQL, Pydantic, Neo4j).
- **`generate_shacl_for_modelling`**: Generates SHACL files using local shape namespaces and `4Modelling` naming conventions, while targeting official ontological URIs.
  - **SQL**: Database DDL (Oracle compatible).
  - **Pydantic**: Python data validation classes.
  - **Neo4j**: Cypher constraints and indexes.
  - *Pass `instructions` for on-the-fly AI enhancements.*

## Installation

```bash
pip install mcp
```

## Running the Server

Ensure your `PYTHONPATH` includes the project root and start the server:

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 neo4j_onto2ai_toolset/onto2ai_mcp.py
```

## Configuration

The server requires the following environment variables (configured via `.env` or exported):

- `NEO4J_MODEL_DB_URL`: Neo4j connection URL.
- `NEO4J_MODEL_DB_PASSWORD`: Neo4j password.
- `OPENAI_API_KEY`: Required for the LLM-powered enhancement and generation tools.

## Example Usage (via MCP Client)

1. **Browse**: `get_materialized_schema(class_names=['Account', 'Person'])`
2. **Transform**: `enhance_schema(class_names=['Person'], instructions='Add mandatory SSN')`
3. **Generate**: `generate_schema_code(class_names=['Payment'], target_type='sql', instructions='Add status enum')`

## Dependencies

- `mcp`
- `pydantic`
- `langchain_openai`
- `neo4j`
