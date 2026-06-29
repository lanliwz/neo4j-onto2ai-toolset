# Onto2AI MCP: Ontology Exploration and Modeling Tools

This project provides a **Model Context Protocol (MCP)** server and an AI-driven client designed to explore, interrogate, extract, enhance, and materialize schemas from an OWL ontology loaded into Neo4j.

The MCP workflow is meant to support a generic ontology-engineering process:
- load a well-known ontology into Neo4j
- inspect concepts, properties, restrictions, and axioms
- extract a useful subset for your use case
- refine that subset into your own ontology or implementation-ready schema

## Features

- **Materialized Schema Retrieval**: Flattened, production-ready views of ontology classes.
- **Data Model Extraction**: High-fidelity structured JSON extraction (classes, attributes, relationships).
- **Schema Artifact Generation**: Generate implementation artifacts from extracted ontology subsets.
- **SHACL Generation**: Modeling-ready SHACL files for ontology-driven data validation.
- **Multi-Model Support**: Seamlessly switch between **Gemini 3.5 Flash** and **GPT-5.2 (OpenAI)**.
- **Clean Agentic Workflow**: Modern LangChain integration using the `create_agent` factory.
- **Ontology Workbench for AI Engineers**: Lets AI engineers use Neo4j plus MCP as a workbench for exploring well-known ontologies and designing derived ontologies.

---

## Server Tool Semantics

### Schema Exploration
- `get_materialized_schema`: Returns a flattened, production-ready class view.
  - Formatting: two Markdown tables (Labels->URI and Relationships->URI).
- `get_ontological_schema`: Returns raw ontology logic (restrictions/domain/range).
  - Formatting: two Markdown tables (Labels->URI and Properties->URI).
- `extract_data_model`: Returns a structured model view suitable for subset extraction, implementation design, and downstream code generation.

### Schema Artifact Generation
- `generate_schema_code`: Generates SQL, Pydantic, or Neo4j outputs.
- `generate_shacl_for_modelling`: Generates modeling SHACL while preserving ontological URIs.

---

## Setup & Installation

### 1. Requirements

- Python 3.12+
- A running Neo4j instance with an OWL ontology loaded.
- (Optional) `langchain-google-genai` for Gemini support.
- MCP runtime:

```bash
pip install mcp
```

### 2. Environment Configuration

The system relies on system environment variables for security. Do **not** hardcode passwords in `.env` for production use.

#### Required Environment Variables

```bash
# Neo4j Settings
export NEO4J_MODEL_DB_URL="bolt://localhost:7687"
export NEO4J_MODEL_DB_USERNAME="neo4j"
export NEO4J_MODEL_DB_PASSWORD="your_neo4j_password"
export NEO4J_MODEL_DB_NAME="fibo"

# LLM Selection (choose one or both)
export GOOGLE_API_KEY="your_google_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Optional: Default LLM Model
export LLM_MODEL_NAME="gemini-3.5-flash" # or "gpt-5.2"
```

---

## Project Structure

- `neo4j_onto2ai_toolset/onto2ai_mcp.py`: The MCP server providing the ontology modeling tools.
- `neo4j_onto2ai_toolset/onto2ai_client.py`: The AI agent client that connects to the server and handles user queries.
- `neo4j_onto2ai_toolset/onto2ai_tool_config.py`: Central configuration manager.

---

## Usage

### Running the Onto2AI Client

The client serves as your primary interface. It automatically starts the MCP server as a subprocess and gives you an ontology workbench over the loaded Neo4j graph.

```bash
onto2ai-client
```

Alternative:
```bash
python -m neo4j_onto2ai_toolset.onto2ai_client
```

Upon startup, the client will:
1. Verify required Neo4j environment variables.
2. Initialize the selected LLM (Gemini with OpenAI fallback).
3. Connect to the MCP server.
4. List available tools.
5. Execute a test query (e.g., fetching the 'person' class schema).

In practice, a common workflow is:
1. load a well-known ontology into Neo4j
2. inspect a candidate class or domain slice with `get_ontological_schema`
3. extract a structured subset with `extract_data_model`
4. refine or simplify that subset through the staging/modeling workflow
5. generate implementation artifacts or a custom ontology-aligned schema

### Using Specific Models

To force the client to use a specific model without changing your environment globally:

**Using OpenAI:**
```bash
LLM_MODEL_NAME=gpt-5.2 python -m neo4j_onto2ai_toolset.onto2ai_client
```

**Using Gemini (requires GOOGLE_API_KEY):**
```bash
LLM_MODEL_NAME=gemini-3.5-flash python -m neo4j_onto2ai_toolset.onto2ai_client
```

### Running as an HTTP Server (SSE)

If you prefer to run the MCP server over HTTP (Server-Sent Events) instead of `stdio`:

```bash
# Start the server on port 8082
python -m neo4j_onto2ai_toolset.onto2ai_mcp http 8082
```

> [!NOTE]
> The default port is `8082`. When running in HTTP mode, clients (like Claude or your own custom integration) should point to `http://localhost:8082/sse`.

### Running in Stdio Mode

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 -m neo4j_onto2ai_toolset.onto2ai_mcp
```

### Development Mode (with Auto-Reload)

For active development, use the `fastmcp dev` command. This automatically watches your files for changes, restarts the server, and provides a built-in **MCP Inspector** UI.

```bash
# Start the server with auto-reload and Inspector
export NEO4J_MODEL_DB_PASSWORD=your_password
fastmcp dev --server-port 8082 neo4j_onto2ai_toolset/onto2ai_mcp.py
```

- **Server (SSE)**: `http://localhost:8082/sse`
- **Inspector UI**: `http://localhost:3000` (by default)

---

## Configuring Antigravity / AI Desktop

To connect your AI agent (Antigravity, Claude Desktop, etc.) to this server, add the following to your MCP configuration file.

### Option 1: Stdio (Recommended for Local Use)
This mode starts the server automatically when the AI agent starts.

```json
{
  "mcpServers": {
    "onto2ai": {
      "command": "python",
      "args": [
        "/path/to/onto2ai-engineer/neo4j_onto2ai_toolset/onto2ai_mcp.py"
      ],
      "env": {
        "NEO4J_MODEL_DB_URL": "bolt://localhost:7687",
        "NEO4J_MODEL_DB_USERNAME": "neo4j",
        "NEO4J_MODEL_DB_PASSWORD": "your_password",
        "NEO4J_MODEL_DB_NAME": "fibo",
        "OPENAI_API_KEY": "your_key",
        "GOOGLE_API_KEY": "your_key"
      }
    }
  }
}
```

### Option 2: HTTP (SSE)
Use this if the server is already running independently on port 8082.

```json
{
  "mcpServers": {
    "onto2ai": {
      "url": "http://localhost:8082/sse"
    }
  }
}
```

---

## Available Modeling Tools

| Tool Name | Description |
|-----------|-------------|
| `list_model_classes` | Lists classes from the Modeller staging database. |
| `list_model_relationships` | Lists non-inheritance relationships from the Modeller staging database. |
| `list_model_individuals` | Lists named individuals grouped by their `rdf:type` class. |
| `list_model_datatypes` | Lists datatype nodes from the Modeller staging database. |
| `list_model_class_hierarchy` | Returns the `rdfs__subClassOf` hierarchy as a tree. |
| `get_model_focus_graph` | Returns focused graph rows for one class and its direct in/out relationships. |
| `search_ontology_concepts` | Searches source ontology labels, URIs, definitions, synonyms, examples, and notes for a business phrase. |
| `preview_concept_neighborhood` | Previews a source ontology class neighborhood before extracting it into a workspace. |
| `extract_domain_subset` | Extracts one or more source ontology classes into the Modeller staging workspace. |
| `get_materialized_schema` | Returns classes and relationships as Markdown tables. |
| `extract_data_model` | Returns high-fidelity structured JSON (Nodes/Properties/Rels) that is useful for subset extraction and custom ontology design. |
| `get_ontological_schema` | Returns the raw meta-model view of an ontology class. |
| `generate_shacl_for_modelling` | Generates official SHACL files for class-based validation. |
| `generate_schema_code` | Generates SQL, Pydantic, or Neo4j code for ontology classes. |
| `staging_materialized_schema` | Copies materialized schema components to a staging database. |
| `consolidate_inheritance` | Copies inherited relationships directly to staged classes. |
| `consolidate_staging_db` | Consolidates classes in stagingdb by converting them to datatypes. |
| `generate_neo4j_schema_description` | Generates a Markdown graph schema description from extracted model data. |
| `generate_neo4j_schema_constraint` | Generates deterministic Cypher constraints and relationship notes. |

Experimental tools currently registered but not part of the stable contract:

- `apply_data_model`
- `merge_semantic_individuals`

---

## Troubleshooting

### ImportError or Connection Closed
If the client exits unexpectedly with an `ImportError` or `Connection closed`, ensure your Neo4j instance is reachable and your credentials are correct in the environment. The client includes `atexit` handlers to ensure Neo4j connections are closed gracefully.

### 404 Model Not Found (Gemini)
If Gemini returns 404, confirm that `gemini-3.5-flash` is enabled for the configured `GOOGLE_API_KEY`.

## Example MCP Calls
1. Explore: `get_ontological_schema(class_name='Person')`
2. Extract: `extract_data_model(class_names=['Account', 'Person'])`
3. Stage: `staging_materialized_schema(class_names=['Person'], flatten_inheritance=True)`
4. Generate: `generate_schema_code(class_names=['Payment'], target_type='sql')`
