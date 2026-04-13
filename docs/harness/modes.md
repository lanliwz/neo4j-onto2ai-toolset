# Harness Modes

This repository uses a simple harness boundary so agentic work stays reliable across ontology authoring, schema generation, dataset validation, and release packaging.

Core idea:

- `Agent = Model + Harness`
- the harness here is the operating mode, file boundary, database boundary, validation rule, and release discipline around the model

These modes are intentionally strict. They reduce drift between RDF, Neo4j artifacts, sample data, and package outputs.

## Overview

The default operating modes are:

- `ontology mode`
- `schema mode`
- `dataset mode`
- `release mode`

Before starting substantial work, classify the task into one of these modes. If a task spans modes, complete them in this order:

1. ontology mode
2. schema mode
3. dataset mode
4. release mode

## Ontology Mode

Use ontology mode when changing ontology meaning.

Typical work:

- add or update ontology classes
- add or update object properties and datatype properties
- add or update restrictions, imports, axioms, or ontology documentation
- rename ontology concepts or URIs

Source of truth:

- RDF files under `resource/ontology/...`
- packaged ontology RDF files when a domain package is already the canonical release surface

Rules:

- update RDF first
- follow repo ontology URI and namespace conventions
- keep edits semantic, not application-data oriented
- align downstream Cypher artifacts after RDF changes
- validate RDF syntax with `xmllint --noout <rdf_file>`

Exit criteria:

- RDF is updated and valid
- ontology URI/path conventions still hold
- downstream schema artifacts are either updated or explicitly queued for schema mode

## Schema Mode

Use schema mode when converting ontology intent into implementation artifacts.

Typical work:

- update Neo4j ontology Cypher
- generate or update Neo4j query context
- generate or update Neo4j constraints
- generate or update Pydantic models
- validate schema coverage and topology

Primary database:

- `stagingdb`

Rules:

- schema artifacts must stay aligned to ontology intent
- schema artifacts do not replace RDF as source of truth
- perform ontology and schema validation in `stagingdb`
- keep query context, constraints, and models mutually consistent

Exit criteria:

- schema artifacts reflect the current ontology
- schema validation passes in `stagingdb`
- artifact drift between Cypher, query context, and Pydantic is resolved

## Dataset Mode

Use dataset mode when testing runtime-style data behavior.

Typical work:

- create smoke tests
- load sample instances
- verify enum/reference data
- verify constraints reject invalid runtime data
- validate application-oriented graph topology

Primary database:

- `testdb`

Rules:

- keep dataset databases instance-oriented
- do not load ontology nodes such as `owl__Class`, `owl__Ontology`, or `owl__Restriction`
- do not use ontology-only edges such as `rdf__type` or `rdfs__subClassOf`
- validate schema separately, then test runtime data behavior with sample instances

Exit criteria:

- smoke tests pass in `testdb`
- runtime graph contains no ontology schema nodes
- sample data exercises the major constraints and relationships

## Release Mode

Use release mode when preparing a package or release artifact.

Typical work:

- bump versions
- update milestone docs or release notes
- build distributions
- verify package contents
- confirm domain outputs are packaged from canonical package paths

Rules:

- run relevant validators before packaging
- keep version metadata and release docs aligned
- package only finalized deliverables
- do not release from transient root `staging/` output when a canonical package path exists

Exit criteria:

- version metadata is aligned
- package build succeeds
- release docs or milestone notes match the shipped scope

## Mode Boundaries

Use these boundaries to avoid mixed-responsibility work:

- `stagingdb` is for ontology/schema validation
- `testdb` is for dataset-only smoke testing
- root `staging/` is transient local workspace, not release source
- packaged domain outputs should live in their package directories

## Example Flow

For a domain ontology package:

1. update RDF in ontology mode
2. regenerate constraints, query context, and models in schema mode
3. run dataset smoke tests in dataset mode
4. package and document the release in release mode

This sequence is the default harness loop for ontology-driven work in this repository.
