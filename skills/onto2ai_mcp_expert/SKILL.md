---
name: "MCP Server Expert"
description: "Instructions for maintaining, running, and extending the Onto2AI MCP Server."
---
# MCP Server Expert (onto2ai_mcp)

You are an expert on the [onto2ai_mcp.py](file:///Users/weizhang/github/neo4j-onto2ai-toolset/neo4j_onto2ai_toolset/onto2ai_mcp.py) server. Use this skill to add new tools, troubleshoot connections, or change the server's execution mode.

## Developer Guide

### 1. Adding New Tools
Register new tools using the `@mcp.tool()` decorator.
- **Rules**: Every tool must be `async` and have clear docstrings with argument descriptions.
- **Type Hints**: Use `Union`, `List`, `Optional`, and `Dict` from `typing` for robust tool signatures.
- **Example**:
```python
@mcp.tool()
async def my_new_tool(param: str) -> str:
    """Description for my new tool."""
    return f"Processed {param}"
```

### 2. Execution Modes
The server supports two primary transports:
- **Stdio (Default)**: Best for direct integration with local agents. Run with `python neo4j_onto2ai_toolset/onto2ai_mcp.py`.
- **HTTP (SSE)**: Best for remote or shared access. Run with `python neo4j_onto2ai_toolset/onto2ai_mcp.py http [port]`.

### 3. Key Dependencies
- **FastMCP**: The core framework for tool registration.
- **Tool Config**: Resolves database connections and LLM settings via [onto2ai_tool_config.py](file:///Users/weizhang/github/neo4j-onto2ai-toolset/neo4j_onto2ai_toolset/onto2ai_tool_config.py).
- **Logger**: All events should be logged via the standard project `logger`.

### 4. Specialized Schema Tools
- **`get_ontology_schema_description`**: Generates a full textual/Markdown summary of a Neo4j database schema (Labels, Relationships, Properties, Metadata).
- **`generate_schema_code` (target_type='graph_schema')**: Invokes the schema description logic to produce a deployment-ready representation of the graph model.

## Maintenance & Debugging
- **JSON Outputs**: When returning complex data, prefer returning Pydantic models (like `DataModel`) or well-structured dictionaries.
- **Error Handling**: Wrap tool logic in `try/except` blocks and log errors before returning error messages to the client.
- **CamelCase Utility**: Use the internal `to_camel_case()` helper for normalizing Neo4j relationship types and property names to match project conventions.
