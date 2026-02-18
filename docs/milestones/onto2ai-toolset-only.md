# Milestone: Onto2AI Toolset Only

- Milestone ID: `M1-onto2ai-toolset-only`
- Date started: `2026-02-18`
- Owner: `weizhang`
- Status: `In Progress`

## Objective
Consolidate this repository into a single-purpose `onto2ai-toolset` project, with aligned naming, structure, runtime configuration, interfaces, and documentation.

## Definition of Done
- Project identity is consistently `onto2ai-toolset` in docs, package metadata, and runtime UX.
- Scope is explicit: only Onto2AI-relevant modules remain active.
- Core workflows run end-to-end (loader, MCP, staging enrichment, schema generation).
- Release artifacts include migration notes for any breaking changes.

## Execution Checklist

### Phase 1: Scope and Boundaries
- [x] Create milestone and kickoff plan.
- [x] Run repository inventory for top-level modules and operational files.
- [x] Finalize include/exclude scope with project owner.
- [x] Document approved scope matrix in this file.

### Phase 2: Naming Consolidation
- [x] Standardize project naming to `onto2ai-toolset` in docs and metadata.
- [x] Normalize CLI/help text and log identity.
- [x] Define backward-compatibility aliases (if any) and deprecation notice.

### Phase 3: Repository Cleanup
- [x] Remove/archive out-of-scope modules and generated artifacts from tracked paths.
- [x] Keep `skills/` aligned with Onto2AI-only workflows.
- [x] Ensure top-level tree is minimal and purpose-driven.

### Phase 4: Runtime and Config Unification
- [x] Define one canonical config contract for DB, model, and environment vars.
- [x] Remove duplicate config flows.
- [x] Verify MCP, loader, and staging workflows use the same config surfaces.

### Phase 5: Interface Stabilization
- [x] Freeze canonical CLI + MCP interfaces.
- [x] Mark removed/renamed interfaces with migration guidance.

### Phase 6: Docs and Onboarding
- [x] Rewrite top-level docs around one Onto2AI workflow.
- [x] Add a fast-path quickstart and operator runbook.

### Phase 7: Validation and Release
- [ ] Execute smoke suite (loader, MCP stdio/http, staging, schema generation).
- [ ] Publish release notes + version tag for milestone completion.

## Phase 1 Working Draft (Proposed Scope)

### Proposed In-Scope (keep)
- `neo4j_onto2ai_toolset/`
- `model_manager/`
- `skills/`
- `staging/`
- `scripts/` (only scripts that support Onto2AI workflows)
- `README.md`, `README4LOADER.md`, `README4ONTO2AI_MCP.md`, `MCP_README.md`
- Packaging/runtime: `setup.py`, `requirements.txt`, `Pipfile`, `main.py`

### Proposed Out-of-Scope (review for remove/archive)
- `chatbots/`
- `tax62_chatbot/`
- `ai_tools/` (except scripts directly required by Onto2AI)
- `ai_graph_flow/`
- `vector_stores/`
- `agents/` (if unrelated to Onto2AI runtime)
- Generated/runtime clutter: `__pycache__/`, `*.log`, `.DS_Store`, `test_output.log`

## Open Decisions (Owner Confirmation Needed)
1. `chatbots/` and `tax62_chatbot/` should be archived out of this repository. ✅
2. `ai_tools/` and `vector_stores/` should be split to another repo. ✅
3. Route usage through package modules only (`package-only`). ✅

## Approved Scope Matrix

### Keep In This Repository
- `neo4j_onto2ai_toolset/`
- `model_manager/`
- `skills/`
- `staging/`
- `scripts/` (Onto2AI-only scripts)
- `README.md`, `README4LOADER.md`, `README4ONTO2AI_MCP.md`, `MCP_README.md`
- Packaging/runtime metadata: `setup.py`, `requirements.txt`, `Pipfile`

### Remove or Archive From This Repository
- `chatbots/` (archive out)
- `tax62_chatbot/` (archive out)
- `ai_tools/` (split to separate repo)
- `vector_stores/` (split to separate repo)
- `ai_graph_flow/` (out of scope unless explicitly required by Onto2AI)
- `agents/` (out of scope unless explicitly required by Onto2AI)

### Entrypoint Policy
- Canonical usage is package-only.
- `main.py` should be deprecated and removed (or converted to a thin compatibility shim during migration).

## Current Progress Notes
- Initial scope audit completed from repository root.
- Scope decisions approved and matrix finalized.
- Phase 2 completed:
  - package metadata renamed to `onto2ai-toolset` in `setup.py`
  - package CLI entrypoint set to `onto2ai-client`
  - root `main.py` converted to deprecated compatibility shim
  - docs updated to package module execution style (`python -m ...`)
- Phase 3 progress:
  - created safe archive area: `archive/out_of_scope/2026-02-18/`
  - moved out-of-scope modules into archive: `agents/`, `ai_graph_flow/`, `ai_tools/`, `chatbots/`, `tax62_chatbot/`, `vector_stores/`
  - added archive restore instructions in `archive/out_of_scope/2026-02-18/README.md`
  - cleaned generated runtime artifacts: `__pycache__/`, `.DS_Store`, `*.log`, `test_output.log`
  - validated Onto2AI-only `skills/` set is intact
- Phase 4 completed:
  - added canonical config contract: `docs/configuration.md`
  - unified model-manager defaults to `LLM_MODEL_NAME` with `GPT_MODEL_NAME` fallback
  - aligned shorthand models in `model_manager/main.py` to `gpt-5.2` and `gemini-3-flash-preview-001`
  - updated core LLM resolution in `neo4j_onto2ai_toolset/onto2ai_tool_config.py` with compatibility handling
- Phase 5 completed:
  - added stable interface specification: `docs/interface-contract.md`
  - added `onto2ai-mcp` console entrypoint in `setup.py`
  - added MCP server `cli_main()` entrypoint in `neo4j_onto2ai_toolset/onto2ai_mcp.py`
  - linked interface contract from `README.md`
- Phase 6 completed:
  - rewrote top-level onboarding in `README.md` to a workflow-first structure
  - added `docs/quickstart.md`
  - added `docs/operator-runbook.md`
  - aligned model manager doc defaults in `model_manager/README.md`
- Phase 7 progress:
  - completed static smoke validation (compile + import + entrypoint checks)
  - executed live `onto2ai-client` startup; MCP tool discovery succeeded
  - live AI round-trip blocked by external DNS/network resolution to Gemini/LangSmith endpoints
  - drafted release notes in `docs/release-notes-m1-draft.md`
  - pending live runtime smoke checks requiring active DB/credentials
- Next action: run live smoke checks and finalize release tag.
