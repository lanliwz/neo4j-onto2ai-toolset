# FIBO Ontology Loader

The `onto2ai_loader.py` script is designed to load FIBO (Financial Industry Business Ontology) and other related ontologies into a Neo4j database using `rdflib` and `rdflib-neo4j`.

## Key Features

- **Recursive Part Discovery**: Supports loading complex specifications and domains by recursively discovering constituent parts using `dcterms:hasPart` relationships. This is essential for FIBO, which uses a hierarchical structure of domains and modules.
- **Domain-Based Loading**: Predefined constants for major FIBO domains (FND, BE, BP, FBC, SEC) allow for easy selection and comprehensive loading of specific functional areas.
- **Namespace Shortening**: Uses the `HANDLE_VOCAB_URI_STRATEGY.SHORTEN` strategy to produce clean, readable URIs in Neo4j. All namespaces are explicitly managed in `onto2schema/prefixes.py`.
- **Robust Import Handling**: Automatically handles `owl:imports` and provides fallbacks for various RDF formats (RDF/XML, Turtle, NT).
- **Post-Load Materialization**: Includes functions to materialize object and datatype properties from OWL restrictions into Neo4j relationships and properties.

## Usage

1.  **Configure Environment**: Ensure your Neo4j credentials and URI are set in `onto2ai_loader.py`.
2.  **Select Domains**: Update the `if __name__ == "__main__":` block in `onto2ai_loader.py` to select the domains you wish to load.
    ```python
    fibo_domains = [FND_DOMAIN, BE_DOMAIN, BP_DOMAIN]
    ```
3.  **Run Loader**:
    ```bash
    export PYTHONPATH=$PYTHONPATH:.
    python neo4j_onto2ai_toolset/onto2ai_loader.py
    ```

## Prefix Management

If you encounter a `ShortenStrictException`, it means a new namespace has been discovered that is not in the controlled list. Add the reported namespace to `neo4j_onto2ai_toolset/onto2schema/prefixes.py` to resolve the error.

## Core Functions

- `discover_and_load_parts(graph, root_uri)`: Recursively traverses `dcterms:hasPart`.
- `load_neo4j_db(onto_uri, format, discover=True)`: Loads the discovered or specified ontology into Neo4j.
- `reset_neo4j_db()`: Clears the Neo4j database and recreates the URI uniqueness constraint.