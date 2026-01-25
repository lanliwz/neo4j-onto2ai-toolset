# Onto2AI Model Manager

A web application to review and enhance ontology schemas in Neo4j staging database.

![Screenshot](../docs/model_manager_screenshot.png)

## Features

- **Three-Panel UI**: Search/Chat/Query (left), Graph visualization (center), Properties (right)
- **GoJS Graph Visualization**: Interactive display of classes and relationships
- **Search**: Filter classes by name
- **Chat**: AI-assisted schema guidance using GPT-4o
- **Query**: Execute Cypher queries directly
- **Property Inspector**: View details for selected nodes/relationships

## Requirements

- Python 3.10+
- Neo4j database with FIBO ontology loaded
- OpenAI API key (for chat feature)

## Installation

```bash
cd /Users/weizhang/github/neo4j-onto2ai-toolset
pip install fastapi uvicorn neo4j openai
```

## Environment Variables

```bash
# Neo4j connection
NEO4J_MODEL_DB_URL=bolt://localhost:7687
NEO4J_MODEL_DB_USERNAME=neo4j
NEO4J_MODEL_DB_PASSWORD=your_password
NEO4J_STAGING_DB_NAME=stagingdb

# OpenAI (for chat)
OPENAI_API_KEY=your_api_key
GPT_MODEL_NAME=gpt-4o
```

## Running

```bash
cd model_manager
../venv/bin/python -m uvicorn main:app --host localhost --port 8180
```

Open http://localhost:8080

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/classes` | GET | List all classes in stagingdb |
| `/api/class/{name}` | GET | Get class schema with relationships |
| `/api/graph-data/{name}` | GET | Get GoJS-formatted graph data |
| `/api/chat` | POST | AI chat for schema assistance |
| `/api/cypher` | POST | Execute read-only Cypher queries |

## Usage

1. **Search**: Type a class name (e.g., "person") in the search box
2. **Visualize**: Click a class to load its schema graph
3. **Inspect**: Click nodes/relationships to see properties
4. **Chat**: Switch to Chat tab for AI assistance
5. **Query**: Switch to Query tab to run Cypher

## Project Structure

```
model_manager/
├── main.py              # FastAPI app
├── api/
│   ├── __init__.py
│   ├── models.py        # Pydantic models
│   └── schemas.py       # API endpoints
└── static/
    ├── index.html       # Main page
    ├── css/styles.css   # Dark theme styles
    └── js/
        ├── app.js       # App logic
        └── graph.js     # GoJS visualization
```

## License

Same as parent project.
