# Onto2AI Quickstart

## 1. Prerequisites
- Python 3.12+
- Running Neo4j instance
- Ontology source URIs/files accessible by loader
- API keys as needed for selected LLM provider

## 2. Install
```bash
pip install .
```

## 3. Configure Environment
```bash
export NEO4J_MODEL_DB_URL="bolt://localhost:7687"
export NEO4J_MODEL_DB_USERNAME="neo4j"
export NEO4J_MODEL_DB_PASSWORD="your_password"
export NEO4J_MODEL_DB_NAME="fibo"

export NEO4J_STAGING_DB_NAME="stagingdb"

# choose one default model
export LLM_MODEL_NAME="gpt-5.2"
# or
# export LLM_MODEL_NAME="gemini-3-flash-preview-001"

# provider keys
export OPENAI_API_KEY="your_openai_key"
# and/or
export GOOGLE_API_KEY="your_google_key"
```

Full variable contract: [configuration.md](./configuration.md)

## 4. Load Ontology
```bash
python -m neo4j_onto2ai_toolset.onto2ai_loader
```

Useful loader operations:
```bash
# list recent load runs
python -m neo4j_onto2ai_toolset.onto2ai_loader history --limit 10

# reload from a prior run's loaded ontology IRI set
python -m neo4j_onto2ai_toolset.onto2ai_loader reload --run-id <run_id> --source loaded

# offline/local-only reload (no internet fetch)
python -m neo4j_onto2ai_toolset.onto2ai_loader reload --run-id <run_id> --source loaded --local-files-only
```

## 5. Start MCP Server
```bash
onto2ai-mcp
```

HTTP mode:
```bash
onto2ai-mcp http 8082
```

## 6. Run Client
```bash
onto2ai-client
```

## 7. Start Modeller (Optional)
```bash
onto2ai-modeller --model gemini --host 0.0.0.0 --port 8180
# or
python -m onto2ai_modeller.main --model gemini --host 0.0.0.0 --port 8180
```
Open: `http://localhost:8180`

## 8. First Validation Checks
- Retrieve class schema via MCP: `get_materialized_schema`
- Extract full model view: `extract_data_model`
- Run staging copy: `staging_materialized_schema`
- Run staging consolidation: `consolidate_inheritance` or `consolidate_staging_db`

## 9. Regenerate Local Schema Artifacts (Recommended)
After enum/NamedIndividual or schema updates, regenerate local artifacts:
- transient local review artifacts may be regenerated under `staging/`
- finalized domain outputs should be published from their canonical package or release location, not from transient root `staging/`

## 10. Finalization Gate (Recommended)
Before distributing a toolset-driven ontology output:
1. Run harness preflight for the mode you are about to enter:
   - `python scripts/harness_preflight.py ontology`
   - `python scripts/harness_preflight.py schema`
   - `python scripts/harness_preflight.py dataset`
   - `python scripts/harness_preflight.py release`
   - or run the generic flow directly: `python scripts/harness_run.py verify`
2. Run generic ontology verification:
   - `python scripts/harness_verify_ontology.py`
3. Run generic mode-boundary verification:
   - `python scripts/harness_verify_mode_boundaries.py`
4. Run release verification:
   - `python scripts/harness_verify_release.py`
   - optional build check: `python scripts/harness_verify_release.py --build`
   - or full release flow: `python scripts/harness_run.py release`
5. Confirm generated artifacts are in sync and committed together.
6. Validate any domain-specific query or smoke-test scenarios in the appropriate downstream package or workspace.
