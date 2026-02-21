---
name: "MCP Server Expert"
description: "Instructions for maintaining, running, and extending the Onto2AI MCP Server."
---
# MCP Server Expert (onto2ai_mcp)

You are an expert on the `neo4j_onto2ai_toolset/onto2ai_mcp.py` server. Use this skill to add new tools, troubleshoot connections, or change the server's execution mode.

## Developer Guide

### Adding New Tools
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

### Execution Modes
The server supports two primary transports:
- **Stdio (Default)**: Best for direct integration with local agents. Run with `onto2ai-mcp` or `python -m neo4j_onto2ai_toolset.onto2ai_mcp`.
- **HTTP (SSE)**: Best for remote or shared access. Run with `onto2ai-mcp http [port]` or `python -m neo4j_onto2ai_toolset.onto2ai_mcp http [port]`.

### Key Dependencies
- **FastMCP**: The core framework for tool registration.
- **Tool Config**: Resolves database connections and LLM settings via `neo4j_onto2ai_toolset/onto2ai_tool_config.py`.
- **Logger**: All events should be logged via the standard project `logger`.

### Specialized Schema Tools

#### `generate_schema_code` (target_type='pydantic')
- Deterministically emits Python `Enum` classes when `owl__NamedIndividual` members are linked via `rdf__type`.
- **Inheritance-aware**: `rdfs__subClassOf` relationships in the DataModel drive proper Python class inheritance.
  - Child classes extend their parent Pydantic class (e.g., `class TaxPayer(Person):`) instead of `BaseModel`.
  - Inherited fields are **omitted** from child class bodies to avoid redefinition.
  - Classes are **topologically sorted** so parents always appear before children in the generated file.
- **Key internal functions**: `_generate_pydantic_strict`, `_topo_sort`, `_inherited_aliases`.

#### `generate_neo4j_schema_description`
Generates a structured Markdown summary with five sections:
1. **Node Labels** — subclass nodes shown with **multi-label notation** (e.g., `TaxPayer:Person`, `Form1040_2025:IndividualTaxReturn`).
2. **Relationship Types** — `rdfs__subClassOf` is **excluded** (inheritance is encoded via multi-label instead).
3. **Node Properties** — **deduplicated** by `(label, property, type, mandatory)`; subclass label column uses multi-label.
4. **Graph Topology** — node patterns use multi-label notation; `rdfs__subClassOf` edges are omitted.
5. **Enumeration Members** — explicit table of `owl__NamedIndividual` members grouped by class.

#### Other Tools
- **`generate_schema_code` (target_type='graph_schema')**: Invokes the schema description logic for a deployment-ready representation.
- **`generate_neo4j_schema_constraint`**: Emits datatype `IS NOT NULL` constraints and enum-aware mandatory relationship comments.

## Maintenance & Debugging
- **JSON Outputs**: When returning complex data, prefer returning Pydantic models (like `DataModel`) or well-structured dictionaries.
- **Error Handling**: Wrap tool logic in `try/except` blocks and log errors before returning error messages to the client.
- **CamelCase Utility**: Use the internal `to_camel_case()` helper for normalizing Neo4j relationship types and property names.
- **Server Restart Required**: After editing `onto2ai_mcp.py`, the MCP server process must be restarted for changes to take effect.
