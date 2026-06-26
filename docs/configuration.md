# Onto2AI Engineer Configuration Contract

This is the canonical environment-variable contract for Onto2AI Engineer runtime components.

## Canonical Variables

### Neo4j (required)
- `NEO4J_MODEL_DB_URL`
- `NEO4J_MODEL_DB_USERNAME`
- `NEO4J_MODEL_DB_PASSWORD`
- `NEO4J_MODEL_DB_NAME`

### Staging DB (optional)
- `NEO4J_STAGING_DB_NAME`
- Default: `stagingdb`

### LLM Selection
- `LLM_MODEL_NAME`
- Recommended values:
  - `gpt-5.4-mini`
  - `gpt-5.5`
  - `gemini-3-flash-preview-001`
- `ONTO2AI_MODELLER_CONFIG` (optional)
  - Path to a deployment-specific Modeller YAML config file.
  - Defaults to the packaged `onto2ai_modeller/config.yaml`.
  - The Modeller UI model dropdown is populated from `llm.available` in this file.

### API Keys
- `OPENAI_API_KEY` (required when using OpenAI models)
- `GOOGLE_API_KEY` (required when using Gemini models)

### App/UI
- `APP_THEME` (`dark` or `light`, optional)

## Compatibility Variables (Deprecated)
- `GPT_MODEL_NAME`: supported as a legacy alias during migration.
  - Internal OpenAI-only flows prefer `GPT_MODEL_NAME` if set.
  - If only `LLM_MODEL_NAME` is set and points to Gemini, OpenAI-only flows fall back to `gpt-5.2`.

## Component Behavior

### MCP / Loader / Core Engineer Runtime
- Resolve Neo4j from `NEO4J_MODEL_DB_*`.
- Use `NEO4J_STAGING_DB_NAME` for staging operations.

### Onto2AI Client
- Uses `LLM_MODEL_NAME` for model selection.
- Handles provider-specific fallback based on available keys.

### Modeller
- Uses the same `LLM_MODEL_NAME` contract and Neo4j variables.
- CLI shorthand `--model gpt` maps to `gpt-5.4-mini`.
- CLI shorthand `--model gemini` maps to `gemini-3-flash-preview-001`.
- Populates the UI model list from `llm.available` in `ONTO2AI_MODELLER_CONFIG`.

Example Modeller config:

```yaml
llm:
  default: gpt-5.4-mini
  available:
    - gpt-5.5
    - gpt-5.4-mini
    - gemini-3-flash-preview-001
```

## Migration Guidance
1. Set `LLM_MODEL_NAME` as the primary model selector.
2. Keep `GPT_MODEL_NAME` only for temporary compatibility.
3. Remove `GPT_MODEL_NAME` once all callers have migrated.
