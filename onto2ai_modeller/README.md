# Onto2AI Modeller

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![GoJS](https://img.shields.io/badge/GoJS-FF9900?style=for-the-badge&logo=javascript&logoColor=white)](https://gojs.net/)

A premium, interactive web application designed to review, visualize, and enhance ontology schemas within a Neo4j staging environment. Powered by AI and interactive graph technology.

## ✨ Features

-   **🧠 Extractive AI Chat**: Powered by the configured `LLM_MODEL_NAME`. Includes true "Chat-to-Graph" extraction—when the AI uses schema tools, the resulting structured data is captured and rendered with high fidelity.
-   **🎨 High-Fidelity Visualization**: Interactive graph powered by GoJS. Automatically visualizes both classes and datatype properties as separate nodes for a complete semantic view.
-   **🎨 Interactive Graph Visualization**: Powered by GoJS. Features custom styling for classes and datatypes, smooth animations, and automatic layout.
-   **🌓 Modern Dark UI**: Slick, resizable three-panel interface designed for deep focus.
-   **📋 Property Inspector**: Deep-dive into node and relationship metadata with a dedicated inspection panel.

## 🚀 Getting Started

### Requirements

-   **Python 3.12+**
-   **Neo4j** (with FIBO ontology or similar loaded into a `stagingdb`)
-   **OpenAI API Key** (for advanced chat features)

### Installation

```bash
# Navigate to the engineer root
cd onto2ai-engineer

# Install dependencies or let uv resolve them from the repository requirements
uv run --with-requirements requirements.txt python -m onto2ai_modeller.main --help
```

### Environment Configuration

Set the following variables in your environment or `.env` file:

```bash
# Neo4j connection details
NEO4J_MODEL_DB_URL=bolt://localhost:7687
NEO4J_MODEL_DB_USERNAME=neo4j
NEO4J_MODEL_DB_PASSWORD=your_password
NEO4J_STAGING_DB_NAME=stagingdb

# AI configuration
OPENAI_API_KEY=your_api_key
LLM_MODEL_NAME=gpt-5.4-mini
```

### Execution

Launch the backend server:

```bash
# Development mode with auto-reload for Python and UI asset changes
uv run --with-requirements requirements.txt \
  python -m onto2ai_modeller.main --reload --model gpt --host localhost --port 8180

# Installed console script
onto2ai-modeller --model gpt --port 8081

# Module form without reload
python -m onto2ai_modeller.main --model gpt --port 8180
```

Access the application at: **[http://localhost:8180](http://localhost:8180)**

## 🛠 API Overview

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/classes` | `GET` | Retrieve the list of all ontology classes. |
| `/api/class/{name}` | `GET` | Fetch detailed schema for a specific class. |
| `/api/chat` | `POST` | AI-assisted schema guidance and graph detection. |
| `/api/cypher` | `POST` | Execute and visualize Cypher queries. |
| `/api/graph-data/{name}` | `GET` | Retrieve GoJS-formatted graph data for a class. |

## 📖 Usage Highlights

1.  **AI-Driven Exploration**: Navigate to the **Chat** tab. Ask: *"Show me the schema for a 'Person' class"*. The AI will explain the class and automatically render the graph in the center panel.
2.  **Custom Querying**: Use the **Query** tab to run complex Cypher. If your query returns nodes and relationships, they will be beautifully visualized automatically.
3.  **Visual Inspection**: Use the **Graph** panel to navigate connections. Clicking any element updates the **Properties** panel on the right with full metadata.

## 📂 Structure

```text
onto2ai_modeller/
├── main.py              # FastAPI Application Entry
├── api/
│   ├── models.py        # Pydantic Response/Request Models
│   └── schemas.py       # API Endpoints & DB Logic
└── static/
    ├── index.html       # UI Foundation
    ├── css/styles.css   # Premium Dark Theme
    └── js/
        ├── app.js       # UI Coordination & AI Integration
        └── graph.js     # GoJS Visualization Logic
```

---
Part of Onto2AI Engineer.
