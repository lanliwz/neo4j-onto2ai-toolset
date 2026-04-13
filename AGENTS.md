# AGENTS.md

## Global Ontology Convention (Mandatory)

When creating or updating ontology files in any project, use the following standard unless the project explicitly overrides it:

- Base domain: `http://www.onto2ai-toolset.com/`
- Ontology base URI: `http://www.onto2ai-toolset.com/ontology/<domain>/<OntologyName>/`
- Ontology naming rule:
  - do not append `Ontology` to the ontology file name or ontology URI name unless a project explicitly requires it
  - prefer concise names such as `Parcel.rdf` with base URI `http://www.onto2ai-toolset.com/ontology/parcel/Parcel/`
- RDF namespace for ontology headers:
  - `xmlns="http://www.onto2ai-toolset.com/ontology/<domain>/<OntologyName>/"`
- RDF header must include:
  - default `xmlns` set to the slash-terminated ontology URI above
  - `xml:base` set to the same slash-terminated ontology base URI above
- Save RDF file using URI-mirrored path:
  - `resource/ontology/www_onto2ai-toolset_com/ontology/<domain>/<OntologyName>.rdf`

## Global Ontology Workflow (Mandatory)

For any ontology change:

1. Update RDF first as the source of truth.
2. Cross-check and update Cypher ontology artifacts to match the RDF URI base, class/property fragments, and semantics.
3. Validate RDF syntax before finishing:
   - `xmllint --noout <rdf_file>`
4. If ontology path or name changed, update project documentation references.

## Dataset Test Rule (Mandatory)

For any dataset-oriented smoke test or sample-data load:

1. Do not load ontology schema nodes such as `owl__Class`, `owl__Ontology`, `owl__Restriction`, or similar ontology-only nodes into the dataset database.
2. Do not use ontology-only relationships such as `rdf__type` or `rdfs__subClassOf` in the dataset database unless the task explicitly requires schema validation in a schema/model database.
3. Keep dataset databases instance-oriented: domain/entity labels, reference/enumeration data, constraints, and application relationships only.
4. If schema validation is needed, validate schema artifacts separately from dataset contents.

## Harness Operating Modes (Mandatory)

Use these four operating modes as the default harness boundary for this repository.

### Ontology Mode

Use ontology mode when the task is about authoring or changing ontology meaning.

Required rules:

1. Treat RDF as the source of truth and update RDF first.
2. Follow the global ontology URI, namespace, and file-path conventions in this file.
3. Keep edits ontology-oriented: classes, properties, restrictions, axioms, imports, and documentation.
4. Validate ontology syntax before finishing:
   - `xmllint --noout <rdf_file>`
5. If ontology semantics changed, align downstream Cypher and documentation references before finishing.

### Schema Mode

Use schema mode when the task is about turning ontology content into implementation artifacts.

Required rules:

1. Generate or update schema artifacts from ontology intent, not as an unrelated parallel design.
2. Keep Cypher constraints, Neo4j query context, Pydantic models, and similar artifacts aligned to the ontology source.
3. Perform schema validation in the schema/model database, normally `stagingdb`.
4. Do not treat schema artifacts as the ontology source of truth.

### Dataset Mode

Use dataset mode when the task is about sample data, smoke tests, or runtime-style validation.

Required rules:

1. Use dataset-oriented databases such as `testdb`, not the schema/model database, unless the task explicitly requires schema validation.
2. Keep dataset databases free of ontology schema nodes such as `owl__Class`, `owl__Ontology`, and `owl__Restriction`.
3. Do not use ontology-only relationships such as `rdf__type` or `rdfs__subClassOf` in dataset databases unless the task explicitly requires schema validation in a schema/model database.
4. Test constraints, enumerations, and application relationships with instance-oriented sample data only.

### Release Mode

Use release mode when the task is about packaging, versioning, release notes, or milestone management.

Required rules:

1. Run the relevant validation steps before packaging or release updates.
2. Keep version numbers, milestone notes, and package metadata aligned.
3. Package finalized artifacts from their canonical package locations, not from transient local staging output.
4. Do not include incomplete or experimental domain packages in release artifacts.
