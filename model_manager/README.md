# 🌌 Onto2AI Model Manager

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![GoJS](https://img.shields.io/badge/GoJS-FF9900?style=for-the-badge&logo=javascript&logoColor=white)](https://gojs.net/)

A premium, interactive web application designed to review, visualize, and enhance ontology schemas within a Neo4j staging environment. Powered by AI and interactive graph technology.

![Screenshot](../docs/model_manager_screenshot.png)

## ✨ Features

-   **🧠 Advanced AI Chat**: Context-aware assistance using GPT-5.2. Includes "Chat-to-Graph" functionality—ask about a class, and the graph automatically updates.
-   **🔍 Intelligent Query Workspace**: Execute Cypher queries with automatic visualization. Results are intelligently rendered as interactive graphs or sortable tables.
-   **🎨 Interactive Graph Visualization**: Powered by GoJS. Features custom styling for classes and datatypes, smooth animations, and automatic layout.
-   **🌓 Modern Dark UI**: Slick, resizable three-panel interface designed for deep focus.
-   **📋 Property Inspector**: Deep-dive into node and relationship metadata with a dedicated inspection panel.

## 🚀 Getting Started

### Requirements

-   **Python 3.10+**
-   **Neo4j** (with FIBO ontology or similar loaded into a `stagingdb`)
-   **OpenAI API Key** (for advanced chat features)

### Installation

```bash
# Clone the repository and navigate to the toolset root
cd neo4j-onto2ai-toolset

# Install dependencies
pip install fastapi uvicorn neo4j openai
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
GPT_MODEL_NAME=gpt-5.2
```

### Execution

Launch the backend server:

```bash
cd model_manager
python -m uvicorn main:app --host localhost --port 8180
```

Access the application at: **[http://localhost:8180](http://localhost:8180)**

## 🛠 API Overview

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/classes` | `GET` | Retrieve the list of all ontology classes. |
| `/api/class/{name}` | `GET` | Fetch detailed schema for a specific class. |
| `/api/chat` | `POST` | AI-assisted schema guidance and graph detection. |
| `/api/cypher` | `POST` | Execute and visualize read-only Cypher queries. |
| `/api/graph-data/{name}` | `GET` | Retrieve GoJS-formatted graph data for a class. |

## 📖 Usage Highlights

1.  **AI-Driven Exploration**: Navigate to the **Chat** tab. Ask: *"Show me the schema for a 'Person' class"*. The AI will explain the class and automatically render the graph in the center panel.
2.  **Custom Querying**: Use the **Query** tab to run complex Cypher. If your query returns nodes and relationships, they will be beautifully visualized automatically.
3.  **Visual Inspection**: Use the **Graph** panel to navigate connections. Clicking any element updates the **Properties** panel on the right with full metadata.

## 📂 Structure

```text
model_manager/
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
*Part of the Neo4j-Onto2AI Toolset.*
