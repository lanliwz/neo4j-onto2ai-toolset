# Northstar Custodian Client Case

This is the executable worked case behind the Custodian Wealth Management demo.
Northstar Custody Bank and Harbor Ridge Family Office are fictional. The case
demonstrates the Onto2AI method; it is not a model for a real institution.

## Business Outcome

Northstar needs one governed application vocabulary for onboarding a wealth
management client, opening a custody account, holding an instrument, and
settling a cash movement. The team must reuse trusted FIBO meaning without
copying all of FIBO into the application model.

The completed case must answer one operational question:

> Can Northstar trace an approved client through its custody account and
> portfolio to a holding, settlement instruction, and completed cash movement?

## Case Files

- `case-definition.json` records the business requirements, exact FIBO seeds,
  customization decisions, and acceptance criteria.
- `northstar-client-scenario.json` is the instance-oriented test dataset.
- `validate_case.py` validates the files, the live target schema, and the sample
  data flow in an isolated Neo4j database.

## Demonstration Runbook

### 1. Discover in Source Ontology

1. Select **Source Ontology** in the left navigator.
2. Enter `account` in **Search source ontology...** and select the search icon.
3. Compare the ranked matches by type, definition, match reason, and score.
4. Select **Preview** on the exact `account` class.
5. Confirm Ontology View shows its relationship neighborhood and Properties
   shows the stable URI and definition.

Use `case-definition.json` to explain why each exact URI was selected. The
stable URI is the selection key; the display label alone is not sufficient.

### 2. Extract into Target Ontology

1. Search for `payment`, `party`, `currency`, and `financial instrument`.
2. Select **Add** for each exact class.
3. Review all five entries under **Extraction Seeds**.
4. Keep **flatten inheritance** enabled.
5. Select **Extract to Workspace**.
6. Confirm the completion message, then open **Target Ontology**.

The UI uses the shared Onto2AI MCP extraction service. The source FIBO database
remains unchanged; `stagingdb` becomes the governed working model.

### 3. Customize for Northstar

Introduce the application vocabulary listed under `target_model.classes`.
Focus the discussion on these decisions:

- `custody account` formally specializes FIBO `Account`.
- `cash movement` formally specializes FIBO `Payment`.
- Client, portfolio, holding, agreement, and onboarding are application-focused
  adaptations that retain source provenance without broad inherited fields.
- Settlement and lifecycle status concepts are local additions because the
  application needs explicit operational state.

### 4. Review Three Synchronized Views

1. In **Target Ontology**, enter `custodian client` in **Filter classes...**.
2. Select the class and confirm Ontology View and Properties synchronize.
3. Review its URI, definition, source provenance, properties, and incoming and
   outgoing relationships.
4. Filter for `custody account` and select **UML Diagram**.
5. Review attributes, FIBO Account inheritance, associations, and multiplicity.
6. Select **Pydantic Models** for the same class.
7. Review types, references, lists, required values, and uniqueness rules.

Use **Expand Design Window** when the graph needs more room. An awkward UML
association or generated field is treated as a modelling issue and corrected
in Target Ontology before regeneration.

### 5. Discuss and Validate in Modeller

Open **Semantic Interaction** and enter:

> Does this target model support onboarding Harbor Ridge, opening a USD custody
> account, and tracing settlement to a cash movement? Identify missing concepts
> or overly broad inherited fields.

Review the graph-grounded response and apply accepted changes in Target
Ontology. If the configured LLM is unavailable, continue with the deterministic
views and Native Query rather than treating chat as the source of truth.

Open **Native Query**, run the read-only validation query from the demo, and
confirm the Properties table returns `12` target classes and `34` custom
properties.

### 6. Test the Harbor Ridge Scenario

Run the file-only test:

```bash
.venv/bin/python demo/custodian_wealth/case/validate_case.py
```

Run the full schema and dataset smoke test:

```bash
set -a
source .env
set +a
.venv/bin/python demo/custodian_wealth/case/validate_case.py \
  --live-schema --live-data --reset-database
```

The live data test uses `northstar-demo`, not `stagingdb`. It loads only domain
instances and application relationships. Remove the disposable database with:

```bash
set -a
source .env
set +a
.venv/bin/python demo/custodian_wealth/case/validate_case.py --cleanup
```

### 7. Finalize and Publish

After review acceptance, use Ontology Mode to author canonical RDF first, align
Cypher and generated application artifacts in Schema Mode, repeat this smoke
test in Dataset Mode, then version and package the result in Release Mode.

The intended release artifact is `northstar-client-ontology`; the current
`stagingdb` model remains a prototype until those canonical package files are
created and validated.

## Acceptance Evidence

The case passes when:

- all required exact FIBO source URIs exist in `stagingdb`;
- all 12 Northstar target classes are documented;
- the 34 custom datatype/object properties carry complete metadata;
- custom resource URIs are unique;
- four controlled vocabularies have the expected members;
- generated application models expose the required fields and cardinalities;
- the isolated dataset contains no ontology schema labels or relationships;
- the client-to-cash-movement trace returns one complete path.
