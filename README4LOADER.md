## Ontology Loader (RDFLib → Neo4j → Onto2AI Schema)

This document describes the ontology loading pipeline implemented in  
`neo4j_onto2ai_toolset/onto2schema/onto_loader.py`.

The loader ingests OWL/RDF ontologies (including all `owl:imports`) into Neo4j using **RDFLib + rdflib-neo4j**, enriches the RDF graph with inferred datatype-property ranges, and then converts the RDF layer into the project’s **Neo4j Onto2Schema domain model**.

---

## High-level workflow

```
OWL / RDF URLs
      ↓
Recursive RDFLib loading (owl:imports)
      ↓
RDF triples streamed into Neo4j (rdflib-neo4j store)
      ↓
SPARQL inference for datatype properties
      ↓
RDF store close (flush batched writes)
      ↓
rdf_to_neo4j_graph(db)
      ↓
Neo4j Onto2Schema model
```

---

## What the loader does

1. Recursively loads an ontology and all its imports  
   - Uses RDFLib to parse RDF documents  
   - Follows `owl:imports` transitively  
   - Prevents infinite loops via an `already_loaded` URI set  

2. Streams RDF data into Neo4j  
   - Uses `rdflib-neo4j` as the RDF store backend  
   - Supports batched writes for performance  

3. Infers datatype property ranges  
   - Runs a SPARQL query (`query4dataprop`) over the in-memory RDF graph  
   - Adds inferred `(Class, DatatypeProperty, xsd:Type)` triples to Neo4j  

4. Converts RDF graph to Onto2Schema Neo4j model  
   - Materializes OWL classes, properties, and restrictions  
   - Normalizes URIs, labels, and annotations  
   - Prepares the graph for downstream reasoning and schema generation  

5. Optionally cleans the Neo4j database before loading  
   - Uses `clean_up_neo4j_graph(db)` (destructive)

---

## Prerequisites

- Python 3.10+
- Neo4j 5.x (local or Aura)
- Python packages:
  - rdflib
  - rdflib-neo4j
  - neo4j
  - neo4j-onto2ai-toolset

Install dependencies:

```bash
pip install -r requirements.txt
```

Install a local build of `rdflib-neo4j` if needed:

```bash
pip install /path/to/rdflib-neo4j/dist/rdflib-neo4j-1.0.tar.gz
```

---

## Configuration

### Neo4j model database

Configured via:
- `onto2ai_tool_config.py`
- `get_neo4j_model_config()`

Typical parameters:
- `NEO4J_MODEL_URL`
- `NEO4J_MODEL_USERNAME`
- `NEO4J_MODEL_PASSWORD`
- `NEO4J_MODEL_DB_NAME`

### RDF store configuration

The loader initializes an RDF store using:

```python
Neo4jStoreConfig(
    auth_data=auth_data,
    custom_prefixes=prefixes,
    handle_vocab_uri_strategy=HANDLE_VOCAB_URI_STRATEGY.SHORTEN,
    batching=True
)
```

⚠️ When `batching=True`, the store **must be explicitly closed** to flush writes.

---

## Running the loader

From the project root:

```bash
python neo4j_onto2ai_toolset/onto2schema/onto_loader.py
```

### Select ontology to load

Edit in `onto_loader.py`:

```python
file_path = "<ONTOLOGY_URI>"
format = "application/rdf+xml"
```

Supported formats include:
- `application/rdf+xml`
- `ttl`
- `nt`

---

## Logging and output

During execution, the loader logs:

- Neo4j configuration and connection details
- Each loaded ontology URI
- Inferred datatype-property triples
- Final triple count summary

Example:

```
Loading: https://spec.edmcouncil.org/fibo/ontology/...
subj: <ClassURI>, pred: <DatatypePropertyURI>, Type: xsd:string