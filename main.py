import asyncio
import warnings
from neo4j_onto2ai_toolset.onto2ai_client import main as onto2ai_client_main

async def main():
    warnings.warn(
        "main.py is deprecated. Use package entrypoints instead: "
        "'onto2ai-client' or 'python -m neo4j_onto2ai_toolset.onto2ai_client'.",
        DeprecationWarning,
        stacklevel=2,
    )
    await onto2ai_client_main()

if __name__ == "__main__":
    asyncio.run(main())
