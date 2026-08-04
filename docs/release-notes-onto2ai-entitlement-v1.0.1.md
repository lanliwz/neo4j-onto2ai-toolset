# Onto2AI Entitlement 1.0.1

Release date: 2026-08-04

## Summary

This patch release aligns the entitlement RDF ontology, materialized schema,
generated application model, Neo4j constraints, and dataset smoke workflow.

## Changes

- Added explicit object-property cardinalities for required and optional-single
  entitlement relationships.
- Marked scalar datatype properties as functional while preserving the intended
  multi-valued policy name and description fields.
- Consolidated the duplicate block-query enumeration members into one individual
  shared by deny and fallback behavior classes.
- Preserved canonical `rdf:type` URIs in extracted named-individual relationships.
- Preserved unique-identifier semantics through property materialization and
  generated ten Neo4j uniqueness constraints.
- Added deterministic entitlement artifact regeneration and regression coverage.
- Updated the schema-to-data smoke fixture for required object relationships.

## Validation

- RDF syntax and packaged/source ontology equality checks passed.
- All 18 repository unit tests passed.
- The entitlement data-flow smoke test validated all 22 model classes.
- The smoke test applied 20 Neo4j constraints: ten required-property constraints
  and ten uniqueness constraints.
