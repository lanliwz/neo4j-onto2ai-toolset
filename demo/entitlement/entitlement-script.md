# Onto2AI Entitlement Demo Script

This demo shows how Onto2AI turns an entitlement ontology into a validated package for row-level filtering and column-level masking.

Entitlement rules often live in scattered implementation details: application code, SQL snippets, tickets, data catalog notes, and policy documents. That makes them hard to review, hard to validate, and risky for AI-assisted data access.

The goal is a governed entitlement model that can be inspected as ontology and consumed as implementation-ready artifacts.

The core entitlement model is intentionally direct. Users inherit policy through groups, and policies collect row filter and column mask rules.

The model also describes the protected data surface: relational database, JDBC connection profile, schema, table, column, and sensitivity classification.

For row-level access, row filter rules describe the target column, comparison semantics, match mode, value source type, deny behavior, and query rewrite guidance.

For column-level protection, column mask rules describe how protected values are revealed, redacted, tokenized, substituted, or nullified.

From the ontology, Onto2AI packages generated artifacts: schema JSON, query context, Neo4j constraints, and a Pydantic application model view. Pydantic is one output format; the goal is an aligned application code model.

Before publishing, the entitlement package runs a smoke test. It creates or reuses a safe generated Neo4j database, applies constraints, loads representative sample data, validates required properties, and checks all application topology relationships.

The result is an independent domain package. Teams consume the entitlement standard without copying the entire modelling workbench.

Onto2AI Entitlement models policy meaning once, generates aligned artifacts, validates them, and packages the result for delivery.
