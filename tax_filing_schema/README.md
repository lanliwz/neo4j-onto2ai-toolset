# Individual Tax Filing Schema (2025)

This directory contains the finalized ontological schema and production-ready code for the Individual Tax Filing system, designed for compatibility between Pydantic models and the Neo4j graph database.

## Directory Structure

```text
tax_filing_schema/
├── README.md           # This file
├── schema/
│   ├── constraints.cypher # Neo4j schema constraints (IS UNIQUE, IS NOT NULL)
│   └── description.md  # Human-readable graph topology & semantic definitions
├── code/
│   ├── models.py       # Pydantic domain models with ontological aliases
│   └── bridge.py       # Pydantic-Neo4j Bridge for automated CRUD operations
└── tests/
    └── verify_roundtrip.py # Round-trip verification script
```

## Key Features

### 1. 1:1 Parity (Pydantic <-> Neo4j)
The Pydantic models in `code/models.py` use the `Field(alias=...)` pattern to ensure that Python class attributes map exactly to Neo4j relationship types and property names (e.g., `taxableIncome` maps to `hasTaxableIncome`).

### 2. Automated Bridge
The `code/bridge.py` utility can recursively serialize Pydantic objects into Neo4j `MERGE` queries. This eliminates manual Cypher mapping for complex nested objects like tax forms.

### 3. Data Integrity
`schema/constraints.cypher` enforces existence constraints (IS NOT NULL) for mandatory properties as defined in the ontology, ensuring graph data matches the business requirements.

## How to Use

### Setup Database
Execute the Cypher statements in `schema/constraints.cypher` against your Neo4j instance to set up the necessary indexes and constraints.

### Loading Data
```python
from code.models import Form1040_2025
from code.bridge import PydanticNeo4jBridge

# Create your model instance
form = Form1040_2025(
    uri="https://example.org/filings/f1040_alice",
    taxYear=2025,
    ...
)

# Load to Neo4j
PydanticNeo4jBridge.load_model_to_neo4j(neo4j_db_driver, form)
```

### Verification
Run `python tests/verify_roundtrip.py` to ensure your environment is correctly configured for the serialization cycle.
