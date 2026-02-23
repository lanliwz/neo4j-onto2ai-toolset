# Release Notes: v0.4.0 (M1 Onto2AI Toolset Only)

## Summary
This release finalizes milestone `M1-onto2ai-toolset-only` and completes the Onto2AI-only repository consolidation.

## Highlights
- Renamed prompt package:
  - `neo4j_onto2ai_toolset/langgraph_prompts` -> `neo4j_onto2ai_toolset/onto2ai_prompt`
- Renamed ontology core package:
  - `neo4j_onto2ai_toolset/onto2schema` -> `neo4j_onto2ai_toolset/onto2ai_core`
- Updated loader and docs to support persistent load history and offline reload:
  - history file at `log/ontology_load_history.json`
  - reload from prior run with `--source loaded --local-files-only`
- Standardized staging artifact names:
  - `staging/full_schema_model.json`
  - `staging/pydantic_schema_model.py`
  - `staging/neo4j_query_context.md`
  - `staging/neo4j_constraint.cypher`
  - `staging/schema_to_data_flow_smoke_test.py`

## Validation Performed
- Staging schema workflow smoke test passed:
  - `python staging/schema_to_data_flow_smoke_test.py --test-db test`
- Local-only ontology reload from latest history run passed:
  - `python -m neo4j_onto2ai_toolset.onto2ai_loader reload --run-id <latest> --source loaded --local-files-only`
- Packaging smoke passed:
  - `python -m build`
  - wheel install/import validation against built artifact

## Upgrade Notes
- Any imports using `neo4j_onto2ai_toolset.onto2schema` must be updated to `neo4j_onto2ai_toolset.onto2ai_core`.
- Any imports using `neo4j_onto2ai_toolset.langgraph_prompts` must be updated to `neo4j_onto2ai_toolset.onto2ai_prompt`.

## Version
- Package version: `0.4.0`
- Release date: `2026-02-23`
