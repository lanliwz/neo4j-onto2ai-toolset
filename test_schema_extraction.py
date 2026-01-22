import asyncio
import json
from neo4j_onto2ai_toolset.onto2ai_mcp import get_materialized_schema

async def main():
    result = await get_materialized_schema("account")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
