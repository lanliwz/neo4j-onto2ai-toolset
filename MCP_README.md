# Neo4j Ontology MCP Server

This MCP server provides a powerful set of tools to interrogate, enhance, and materialize schemas from an OWL ontology loaded into Neo4j. It supports the **Model Context Protocol** (MCP), enabling seamless integration with AI agents.

## Features

### 1. Schema Exploration
- **`get_materialized_schema`**: Returns a simplified property-graph view of a class, including flattened inheritance and materialized relationships. Ideal for application developers.
- **`get_ontological_schema`**: Returns the raw, non-flattened ontological definitions (Restrictions, domain/range) for auditing or deep model analysis.

### 2. Schema Manager (AI-Powered)
- **`extract_data_model`**: Extracts a structured JSON `DataModel` from any ontology class.
- **`enhance_schema`**: Uses AI to modify a `DataModel` based on natural language instructions (e.g., "Add a middleName", "Make email unique").
- **`generate_schema_code`**: Generates production-ready code from a `DataModel` for:
  - **SQL**: Database DDL (Oracle compatible).
  - **Pydantic**: Python data validation classes.
  - **Neo4j**: Cypher constraints and indexes.

## Installation

```bash
pip install mcp
```

## Running the Server

Ensure your `PYTHONPATH` includes the project root and start the server:

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 neo4j_onto2ai_toolset/mcp_server.py
```

## Configuration

The server requires the following environment variables (configured via `.env` or exported):

- `NEO4J_MODEL_DB_URL`: Neo4j connection URL.
- `NEO4J_MODEL_DB_PASSWORD`: Neo4j password.
- `OPENAI_API_KEY`: Required for the LLM-powered enhancement and generation tools.

## Example Usage (via MCP Client)

1.  **Extract Base**: `extract_data_model(class_names='Person')`
2.  **Add Property**: `enhance_schema(model, 'Add a mandatory SSN to Person')`
3.  **Generate Code**: `generate_schema_code(target_type='pydantic', data_model=enhanced_model)`

## Dependencies

- `mcp`
- `pydantic`
- `langchain_openai`
- `neo4j`
