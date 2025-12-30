import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

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
    resources = await client.get_resources()
    print("\n=== Available MCP Resources ===")
    for i, resource in enumerate(resources, start=1):
        # Each resource typically has attributes like uri, name, description, etc.
        print(f"{i}. Resource:")
        try:
            # Try to pretty-print its fields
            # If it's an MCP resource object, it might have attributes
            print(json.dumps(resource, indent=2))
        except Exception:
            # Fallback if resource isn’t JSON-serializable
            print(resource)
        print("-" * 40)






    print("\n=== Available MCP Tools ===")
    for i, t in enumerate(tools, start=1):
        name = getattr(t, "name", t.__class__.__name__)
        desc = getattr(t, "description", "") or ""
        args_schema = getattr(t, "args_schema", None)
        if args_schema is not None:
            try:
                schema_json = args_schema.model_json_schema()
            except Exception:
                schema_json = str(args_schema)
        else:
            schema_json = None

        print(f"{i}. {name}")
        if desc:
            print(f"   desc: {desc}")
        if schema_json:
            print(f"   args_schema: {schema_json}")
    print("=== End Tools ===\n")


    def tool_by_name(name: str):
        for t in tools:
            if getattr(t, "name", None) == name:
                return t
        raise ValueError(f"Tool not found: {name}")

    def _extract_text(obj):
        """MCP servers often return a list of content blocks like [{'type':'text','text':'...'}].
        This extracts and concatenates any 'text' fields."""
        if isinstance(obj, list):
            parts = []
            for item in obj:
                if isinstance(item, dict) and "text" in item:
                    parts.append(item["text"])
                else:
                    parts.append(str(item))
            return "".join(parts)
        return obj

    def _maybe_json_loads(s):
        if not isinstance(s, str):
            return s
        s2 = s.strip()
        if not s2:
            return s
        # Only attempt JSON parsing when it looks like JSON
        if (s2.startswith("{") and s2.endswith("}")) or (s2.startswith("[") and s2.endswith("]")):
            try:
                return json.loads(s2)
            except Exception:
                return s
        return s

    def normalize_mcp_output(obj):
        """Normalize MCP tool output to a Python dict/object when possible."""
        obj = _extract_text(obj)
        obj = _maybe_json_loads(obj)
        return obj

    def extract_data_model(example_out):
        """Pull the DataModel payload out of get_example_data_model output."""
        ex = normalize_mcp_output(example_out)
        if isinstance(ex, dict) and "data_model" in ex:
            return ex["data_model"], ex
        # Sometimes the tool may return the DataModel directly
        return ex, ex

    # End-to-end MCP tools demo (no agent): list examples -> load example -> validate -> export
    try:
        list_examples = tool_by_name("list_example_data_models")
        examples = await list_examples.ainvoke({})
        print("\n=== list_example_data_models ===")
        print(examples)

        example_name = "customer_360"
        get_example = tool_by_name("get_example_data_model")
        example_raw = await get_example.ainvoke({"example_name": example_name})
        example_out = normalize_mcp_output(example_raw)
        print(f"\n=== get_example_data_model: {example_name} ===")
        print(example_out)

        data_model, _full = extract_data_model(example_out)

        validate_dm = tool_by_name("validate_data_model")
        validated_raw = await validate_dm.ainvoke({"data_model": data_model, "return_validated": True})
        validated_out = normalize_mcp_output(validated_raw)

        # validate_data_model may return True, or the validated model, or a wrapper dict.
        if isinstance(validated_out, dict) and "data_model" in validated_out:
            validated_dm = validated_out["data_model"]
        else:
            validated_dm = validated_out

        print("\n=== validate_data_model (validated) ===")
        print(validated_dm)

        export_arrows = tool_by_name("export_to_arrows_json")
        arrows_raw = await export_arrows.ainvoke({"data_model": validated_dm})
        arrows_out = normalize_mcp_output(arrows_raw)
        print("\n=== export_to_arrows_json ===")
        print(arrows_out)

    except Exception as e:
        print("\n=== MCP tools demo failed ===")
        print(repr(e))
        print("Tip: if get_example_data_model returns a different shape, print(example_out) and adjust data_model extraction.")
        print("=== End MCP tools demo ===\n")




if __name__ == "__main__":
    asyncio.run(main())