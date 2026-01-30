# Onto2AI MCP: Ontology Modeling Tools

This project provides a powerful **Model Context Protocol (MCP)** server and an AI-driven client designed to interrogate, enhance, and materialize schemas from an OWL ontology loaded into Neo4j.

## Features

- **Materialized Schema Retrieval**: Flattened, production-ready views of ontology classes.
- **AI Enhancement**: On-the-fly schema refinement using GPT models.
- **SHACL Generation**: Modeling-ready SHACL files for ontology-driven data validation.
- **Multi-Model Support**: Seamlessly switch between **Gemini 2.0 Flash** and **GPT-5.2 (OpenAI)**.
- **Clean Agentic Workflow**: Modern LangChain integration using the `create_agent` factory.

---

## Setup & Installation

### 1. Requirements

- Python 3.12+
- A running Neo4j instance with an OWL ontology loaded.
- (Optional) `langchain-google-genai` for Gemini support.

### 2. Environment Configuration

The system relies on system environment variables for security. Do **not** hardcode passwords in `.env` for production use.

#### Required Environment Variables

```bash
# Neo4j Settings
export NEO4J_MODEL_DB_URL="bolt://localhost:7687"
export NEO4J_MODEL_DB_USERNAME="neo4j"
export NEO4J_MODEL_DB_PASSWORD="your_neo4j_password"
export NEO4J_MODEL_DB_NAME="neo4j"

# LLM Selection (choose one or both)
export GOOGLE_API_KEY="your_google_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# Optional: Default LLM Model
export LLM_MODEL_NAME="gemini-3-flash-preview" # or "gpt-5.2"
```

---

## Project Structure

- `neo4j_onto2ai_toolset/onto2ai_mcp.py`: The MCP server providing the oncology tools.
- `neo4j_onto2ai_toolset/onto2ai_client.py`: The AI agent client that connects to the server and handles user queries.
- `neo4j_onto2ai_toolset/onto2ai_tool_config.py`: Central configuration manager.

---

## Usage

### Running the Onto2AI Client

The client serves as your primary interface. It automatically starts the MCP server as a subprocess.

```bash
python neo4j_onto2ai_toolset/onto2ai_client.py
```

Upon startup, the client will:
1. Verify required Neo4j environment variables.
2. Initialize the selected LLM (Gemini with OpenAI fallback).
3. Connect to the MCP server.
4. List available tools.
5. Execute a test query (e.g., fetching the 'person' class schema).

### Using Specific Models

To force the client to use a specific model without changing your environment globally:

**Using OpenAI:**
```bash
LLM_MODEL_NAME=gpt-5.2 python neo4j_onto2ai_toolset/onto2ai_client.py
```

**Using Gemini (requires GOOGLE_API_KEY):**
```bash
LLM_MODEL_NAME=gemini-3-flash-preview python neo4j_onto2ai_toolset/onto2ai_client.py
```

### Running as an HTTP Server (SSE)

If you prefer to run the MCP server over HTTP (Server-Sent Events) instead of `stdio`:

```bash
# Start the server on port 8082
python neo4j_onto2ai_toolset/onto2ai_mcp.py http 8082
```

> [!NOTE]
> The default port is `8082`. When running in HTTP mode, clients (like Claude or your own custom integration) should point to `http://localhost:8082/sse`.

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
        "/Users/weizhang/github/neo4j-onto2ai-toolset/neo4j_onto2ai_toolset/onto2ai_mcp.py"
      ],
      "env": {
        "NEO4J_MODEL_DB_URL": "bolt://localhost:7687",
        "NEO4J_MODEL_DB_USERNAME": "neo4j",
        "NEO4J_MODEL_DB_PASSWORD": "your_password",
        "NEO4J_MODEL_DB_NAME": "neo4j",
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
| `get_materialized_schema` | Returns classes and relationships as Markdown tables. |
| `get_ontological_schema` | Returns the raw meta-model view of an ontology class. |
| `enhance_schema` | AI-driven schema enhancement based on custom instructions. |
| `generate_shacl_for_modelling` | Generates official SHACL files for class-based validation. |
| `generate_schema_code` | Generates SQL, Pydantic, or Neo4j code for ontology classes. |
| `staging_materialized_schema` | Copies materialized schema components to a staging database. |

---

## Troubleshooting

### ImportError or Connection Closed
If the client exits unexpectedly with an `ImportError` or `Connection closed`, ensure your Neo4j instance is reachable and your credentials are correct in the environment. The client includes `atexit` handlers to ensure Neo4j connections are closed gracefully.

### 404 Model Not Found (Gemini)
Gemini 3 models in AI Studio currently require the `-preview` suffix (e.g., `gemini-3-flash-preview`). The client defaults to this ID.
