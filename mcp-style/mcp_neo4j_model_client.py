import asyncio
import json
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from neo4j import GraphDatabase
from typing import Any

async def main():
    client = MultiServerMCPClient(
        {
            "mcp-neo4j-data-modeling": {
                "transport": "http",
                "url": "http://localhost:8100/mcp",
            }
        }
    )

    tools = await client.get_tools()

    def tool_by_name(name: str):
        for t in tools:
            if getattr(t, "name", None) == name:
                return t
        raise ValueError(f"Tool not found: {name}")

    def _extract_text(obj: Any) -> Any:
        # MCP tools often return a list of content blocks like [{'type':'text','text':'...'}]
        if isinstance(obj, list):
            parts = []
            for item in obj:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                else:
                    parts.append(str(item))
            return "".join(parts)
        return obj

    def _maybe_json_loads(val: Any) -> Any:
        if not isinstance(val, str):
            return val
        s = val.strip()
        if not s:
            return val
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                return json.loads(s)
            except Exception:
                return val
        return val

    def normalize_mcp_output(obj: Any) -> Any:
        return _maybe_json_loads(_extract_text(obj))

    def strip_code_fences(s: str) -> str:
        s2 = s.strip()
        if s2.startswith("```"):
            # Remove leading ```lang and trailing ```
            lines = s2.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return s2

    def _coerce_property(p: Any) -> dict:
        """Convert either a string property name or a partial dict into a full Property dict."""
        if isinstance(p, str):
            name = p
            p = {"name": name}
        if not isinstance(p, dict):
            p = {"name": str(p)}

        name = p.get("name") or p.get("property") or p.get("field") or ""
        if not name:
            name = "unknown"

        # Default type: STRING. You can improve heuristics later.
        p_type = p.get("type") or "STRING"

        return {
            "name": name,
            "type": p_type,
            "source": p.get("source"),
            "description": p.get("description"),
        }

    def coerce_datamodel_shape(dm: Any) -> dict:
        """Make the DataModel shape compatible with the MCP server's Pydantic models."""
        if not isinstance(dm, dict):
            raise ValueError(f"Data model must be a dict, got: {type(dm)}")

        dm = dict(dm)
        dm.setdefault("nodes", [])
        dm.setdefault("relationships", [])
        dm.setdefault("metadata", {})

        # Nodes
        fixed_nodes = []
        for n in dm.get("nodes", []) or []:
            if not isinstance(n, dict):
                continue
            n = dict(n)
            n.setdefault("description", None)
            n.setdefault("metadata", {})

            # key_property must be a dict with name/type/source/description
            kp = n.get("key_property") or n.get("keyProperty")
            if isinstance(kp, str):
                kp = {"name": kp}
            if not isinstance(kp, dict):
                # Fall back to common ids
                kp = {"name": "id"}
            kp_name = kp.get("name") or "id"
            kp_type = kp.get("type") or "STRING"
            n["key_property"] = {
                "name": kp_name,
                "type": kp_type,
                "source": kp.get("source"),
                "description": kp.get("description"),
            }

            props = n.get("properties") or []
            if isinstance(props, dict):
                # Some LLMs return {name: type}; convert to list[Property]
                props = [{"name": k, "type": v} for k, v in props.items()]
            n["properties"] = [_coerce_property(p) for p in (props or [])]

            # Ensure label exists
            if "label" not in n and "name" in n:
                n["label"] = n["name"]
            fixed_nodes.append(n)
        dm["nodes"] = fixed_nodes

        # Relationships
        fixed_rels = []
        for r in dm.get("relationships", []) or []:
            if not isinstance(r, dict):
                continue
            r = dict(r)
            r.setdefault("description", None)
            r.setdefault("metadata", {})

            # Normalize required fields
            if "start_node_label" not in r and "startNodeLabel" in r:
                r["start_node_label"] = r["startNodeLabel"]
            if "end_node_label" not in r and "endNodeLabel" in r:
                r["end_node_label"] = r["endNodeLabel"]

            props = r.get("properties") or []
            if isinstance(props, dict):
                props = [{"name": k, "type": v} for k, v in props.items()]
            r["properties"] = [_coerce_property(p) for p in (props or [])]

            fixed_rels.append(r)
        dm["relationships"] = fixed_rels

        return dm

    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5-nano"))

    # 1) Ask the LLM to design a data model (strict JSON only)
    prompt = (
        "Design a Neo4j Graph Data Model for a company selling AR glasses. "
        "Return ONLY valid JSON for a DataModel with keys: nodes, relationships, metadata (optional). "
        "Each node: label (PascalCase), key_property {name, type}, properties[] (camelCase names), description. "
        "Each relationship: type (SCREAMING_SNAKE_CASE), start_node_label, end_node_label, properties[] (optional), description. "
        "No markdown, no comments."
    )

    llm_msg = await llm.ainvoke(prompt)
    # langchain returns an AIMessage; content is the string
    raw_model_str = getattr(llm_msg, "content", str(llm_msg))
    raw_model_str = strip_code_fences(raw_model_str)
    data_model = json.loads(raw_model_str)
    data_model = coerce_datamodel_shape(data_model)

    print("\n=== Model Summary (pre-validation) ===")
    print(f"nodes={len(data_model.get('nodes', []))}, relationships={len(data_model.get('relationships', []))}")

    # 2) Validate model via MCP (ask for validated payload)
    validate_dm = tool_by_name("validate_data_model")
    validated_raw = await validate_dm.ainvoke({"data_model": data_model, "return_validated": True})
    validated_out = normalize_mcp_output(validated_raw)

    # validate_data_model may return True, a validated model, or a wrapper dict
    if isinstance(validated_out, dict) and "data_model" in validated_out:
        validated_model = validated_out["data_model"]
    else:
        validated_model = validated_out

    print("\n=== Validated Data Model ===")
    print(json.dumps(validated_model, indent=2))

    # 3) Generate constraint Cypher via MCP
    constraints_tool = tool_by_name("get_constraints_cypher_queries")
    constraints_raw = await constraints_tool.ainvoke({"data_model": validated_model})
    constraints_out = normalize_mcp_output(constraints_raw)

    # Support either list[str] or {'queries': [...]} or plain text
    if isinstance(constraints_out, dict) and "queries" in constraints_out:
        cypher_queries = constraints_out["queries"]
    elif isinstance(constraints_out, list):
        cypher_queries = constraints_out
    else:
        cypher_queries = [str(constraints_out)]

    print("\n=== Constraint Cypher Queries ===")
    for q in cypher_queries:
        print(q)

    # Set these env vars if your Neo4j is not local/default:
    #   NEO4J_URI=bolt://host:7687
    #   NEO4J_USER=neo4j
    #   NEO4J_PASSWORD=your_password
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = "neo4j"
    neo4j_password = os.getenv("NEO4J_PASSWORD", "neo4j")

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    try:
        with driver.session() as session:
            for q in cypher_queries:
                q = str(q).strip()
                if not q:
                    continue
                session.run(q)
        print("\n✅ Applied constraints/indexes to Neo4j successfully.")
        print(f"Neo4j: {neo4j_uri} (user={neo4j_user})")
    finally:
        driver.close()

    # Optional: export to Arrows JSON for visualization
    export_arrows = tool_by_name("export_to_arrows_json")
    arrows_raw = await export_arrows.ainvoke({"data_model": validated_model})
    arrows_out = normalize_mcp_output(arrows_raw)
    print("\n=== Arrows JSON ===")
    if isinstance(arrows_out, dict) and "result" in arrows_out:
        print(arrows_out["result"])
    else:
        print(arrows_out)

if __name__ == "__main__":
    asyncio.run(main())