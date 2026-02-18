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
export NEO4J_MODEL_DB_NAME="neo4j"

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

## 7. Start Model Manager (Optional)
```bash
cd model_manager
python main.py --model gemini --port 8180
```
Open: `http://localhost:8180`

## 8. First Validation Checks
- Retrieve class schema via MCP: `get_materialized_schema`
- Extract full model view: `extract_data_model`
- Run staging copy: `staging_materialized_schema`
- Run staging consolidation: `consolidate_inheritance` or `consolidate_staging_db`
