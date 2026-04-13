# Harness Checklists

This document makes the harness modes operational.

Use it as a preflight and exit checklist before doing substantial work in this repository. The goal is to catch mode violations early, keep ontology and implementation artifacts aligned, and reduce avoidable rework.

Related mode definitions:

- [modes.md](/Users/weizhang/github/neo4j-onto2ai-toolset/docs/harness/modes.md)
- [AGENTS.md](/Users/weizhang/github/neo4j-onto2ai-toolset/AGENTS.md)

## How To Use This Document

Before starting work:

1. classify the task into one primary mode
2. run the entry checks for that mode
3. keep work within the allowed file and database boundaries
4. run the required validators before finishing
5. confirm the exit criteria

Optional helper:

```bash
python scripts/harness_preflight.py <ontology|schema|dataset|release>
python scripts/harness_run.py verify
python scripts/harness_run.py release
```

Harness scripts also append lightweight JSONL run records to `log/harness_runs.jsonl`.

If a task spans multiple modes, complete them in this order:

1. ontology mode
2. schema mode
3. dataset mode
4. release mode

## Ontology Mode Checklist

Use ontology mode when changing ontology meaning, URI structure, or ontology documentation.

### Entry Checks

- confirm the task changes ontology meaning rather than only implementation artifacts
- identify the RDF source-of-truth file under `resource/ontology/...` or the canonical packaged ontology path
- confirm the ontology base URI, namespace, and file path follow repo conventions
- identify any downstream Cypher or documentation that will need alignment

### Allowed Files

- `resource/ontology/...`
- packaged ontology files such as `onto2ai_<domain>/ontology/...`
- matching ontology Cypher artifacts when alignment is required
- documentation that references the ontology path, URI, or semantics

### Allowed Databases

- none required for pure ontology editing
- `stagingdb` if ontology/schema validation is part of the task

### Required Validators

- `xmllint --noout <rdf_file>`
- cross-check ontology URI, namespace, and RDF header values
- verify downstream Cypher still matches ontology fragments and intent when applicable

### Exit Criteria

- RDF is the final source of truth for the change
- RDF syntax passes validation
- ontology URI/path references are consistent
- any affected downstream schema artifacts are updated or explicitly queued for schema mode

## Schema Mode Checklist

Use schema mode when converting ontology intent into implementation artifacts.

### Entry Checks

- confirm the ontology source is already updated
- identify which artifacts are in scope:
  - Neo4j Cypher
  - query context
  - constraints
  - Pydantic models
  - schema validation scripts
- identify the canonical schema package or workspace location
- confirm `stagingdb` is the target database for validation

### Allowed Files

- ontology-aligned Cypher files
- `neo4j_query_context.md`
- `neo4j_constraint.cypher`
- Pydantic model files
- schema validation scripts
- package-local staging artifacts such as `onto2ai_<domain>/staging/...`
- transient `staging/` files only when they are explicitly workspace-local and not release sources

### Allowed Databases

- `stagingdb`

### Required Validators

- schema validation against `stagingdb`
- cross-check query context, constraints, and Pydantic models for drift
- verify schema artifacts still reflect ontology intent and naming

### Exit Criteria

- schema artifacts are aligned to the ontology source
- validation passes in `stagingdb`
- query context, constraints, and models are mutually consistent
- no schema artifact is acting as a competing source of truth

## Dataset Mode Checklist

Use dataset mode for smoke tests, sample data, runtime behavior, and instance-oriented validation.

### Entry Checks

- confirm schema validation has already been completed separately
- identify the dataset smoke test or sample-data load path
- confirm `testdb` is the target runtime-style database
- confirm the test is instance-oriented, not ontology/schema-oriented

### Allowed Files

- smoke test scripts
- sample data loaders
- dataset-oriented Pydantic usage
- package-local staging test artifacts
- runtime validation helpers

### Allowed Databases

- `testdb`

### Required Validators

- smoke test execution in `testdb`
- checks that no ontology schema nodes are loaded into `testdb`
- checks that no ontology-only edges such as `rdf__type` or `rdfs__subClassOf` are used in `testdb`
- checks that constraints reject invalid runtime data where applicable

### Exit Criteria

- smoke tests pass in `testdb`
- runtime graph is dataset-only
- major entity, enumeration, and relationship paths are exercised
- ontology/schema validation remains separated from runtime data validation

## Release Mode Checklist

Use release mode for packaging, version updates, milestone notes, and distribution verification.

### Entry Checks

- confirm ontology, schema, and dataset validation are already complete for the scoped release
- identify the canonical package path for the deliverable
- identify the version files, milestone docs, or release notes that must stay aligned
- confirm the package is complete enough for release

### Allowed Files

- package metadata
- version markers
- milestone and release notes
- package-local artifacts
- build configuration files

### Allowed Databases

- none by default
- only use databases if a release check explicitly reruns validation

### Required Validators

- version consistency checks
- package build
- artifact presence checks in the built package
- verification that released artifacts come from canonical package paths, not transient root `staging/`

### Exit Criteria

- version metadata is aligned
- release notes or milestone notes match the shipped scope
- build succeeds
- released package contains only intended, finalized artifacts

## Fast Decision Guide

Use this quick guide when a task is ambiguous:

- if the change alters ontology meaning, start in ontology mode
- if the change alters constraints, query context, Cypher, or Pydantic artifacts, use schema mode
- if the change creates or validates sample/runtime data, use dataset mode
- if the change bumps versions, updates milestones, or builds artifacts, use release mode

When in doubt, choose the earliest applicable mode and move forward in order.
