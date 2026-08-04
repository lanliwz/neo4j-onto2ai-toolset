from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from onto2ai_entitlement.artifacts import (
    STAGING_CONSTRAINT_PATH,
    STAGING_MODEL_PATH,
    STAGING_PYDANTIC_PATH,
    STAGING_QUERY_CONTEXT_PATH,
)
from neo4j_onto2ai_toolset.onto2ai_mcp import (
    extract_data_model,
    generate_neo4j_schema_constraint,
    generate_neo4j_schema_description,
    generate_schema_code,
)


async def regenerate(database: str) -> None:
    data_model = await extract_data_model(database=database)
    pydantic_model = await generate_schema_code(
        target_type="pydantic",
        database=database,
    )
    query_context = await generate_neo4j_schema_description(database=database)
    constraints = await generate_neo4j_schema_constraint(database=database)

    STAGING_MODEL_PATH.write_text(
        data_model.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    STAGING_PYDANTIC_PATH.write_text(pydantic_model, encoding="utf-8")
    STAGING_QUERY_CONTEXT_PATH.write_text(query_context, encoding="utf-8")
    STAGING_CONSTRAINT_PATH.write_text(constraints, encoding="utf-8")

    print(f"Regenerated entitlement artifacts from {database}:")
    print(f"- {STAGING_MODEL_PATH}")
    print(f"- {STAGING_PYDANTIC_PATH}")
    print(f"- {STAGING_QUERY_CONTEXT_PATH}")
    print(f"- {STAGING_CONSTRAINT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate packaged entitlement artifacts from a schema database.",
    )
    parser.add_argument("--database", default="stagingdb")
    args = parser.parse_args()
    asyncio.run(regenerate(args.database))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
