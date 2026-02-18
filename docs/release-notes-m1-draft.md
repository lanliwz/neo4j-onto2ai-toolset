# Release Notes Draft: M1 Onto2AI Toolset Only

## Summary
This milestone narrows the repository to Onto2AI-only scope and standardizes runtime interfaces, configuration, and onboarding.

## Highlights
- Rebranded package identity to `onto2ai-toolset`.
- Standardized canonical CLIs:
  - `onto2ai-client`
  - `onto2ai-mcp`
- Converted root `main.py` to a deprecated compatibility shim.
- Archived out-of-scope modules under `archive/out_of_scope/2026-02-18/`.
- Unified configuration contract and documented it in `docs/configuration.md`.
- Stabilized interface contract in `docs/interface-contract.md`.
- Rewrote onboarding docs and added:
  - `docs/quickstart.md`
  - `docs/operator-runbook.md`

## Breaking/Behavioral Changes
- Canonical execution is now package/module entrypoint based.
- Legacy `neo4j-chatbot` script is replaced by `onto2ai-client`.
- Out-of-scope modules are no longer active at repository root.

## Migration Guidance
1. Replace `python main.py` with `onto2ai-client`.
2. Replace path-based MCP startup with `onto2ai-mcp` or `python -m neo4j_onto2ai_toolset.onto2ai_mcp`.
3. Set `LLM_MODEL_NAME` as primary model selector.
4. Keep `GPT_MODEL_NAME` only for temporary backward compatibility.

## Validation Status
- Completed:
  - Python syntax compile checks for core modules.
  - Import smoke checks for loader, client, and MCP modules.
  - Entrypoint presence checks for `cli_main()`.
- Pending (requires live runtime + credentials):
  - Full MCP stdio/http startup and tool round-trip.
  - End-to-end loader run against live Neo4j.
  - Full staging workflow execution against `stagingdb`.

## Release Checklist
- [ ] Run live runtime smoke checks in target environment.
- [ ] Finalize this document.
- [ ] Create tag: `v1.0.0-onto2ai-toolset`.
