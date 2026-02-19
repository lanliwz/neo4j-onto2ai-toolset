---
name: "Staging Database Expert"
description: "Specialized skill for managing, enriching, and consolidating the Neo4j staging database."
---
# Staging Database Expert Instructions

You are a master of the Staging Database (typically `stagingdb`). Use this skill to move data from the primary ontology to staging, enrich classes with properties, create custom classes, manage named individuals, and clean up/flatten the staging schema for production use.

## Core Operations

### Staging Data
Use `staging_materialized_schema` to copy classes and relationships to the staging database.
- **Goal**: Create a self-contained subset of the ontology.
- **Options**: Set `flatten_inheritance=True` if you want to copy ancestor relationships directly to the child classes during extraction.

### Enriching Classes from FIBO Ontology
Use `get_materialized_schema` to discover available properties for a class, then write them to staging with Cypher.

**Workflow:**
1. Query FIBO ontology: `get_materialized_schema(class_names=["person"])` to see all available relationships
2. Check what already exists in staging: `MATCH (c:owl__Class {rdfs__label: 'person'})-[r]->(t) RETURN type(r), t.rdfs__label`
3. Write enrichment via Cypher — create target class nodes with `MERGE` and relationships with `CREATE`

**Example — Enriching Person:**
```cypher
MATCH (person:owl__Class {rdfs__label: 'person'})
SET person.skos__definition = 'individual human being, with consciousness of self',
    person.uri = 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/Person'

MERGE (personName:owl__Class {uri: 'https://spec.edmcouncil.org/fibo/ontology/FND/AgentsAndPeople/People/PersonName'})
  ON CREATE SET personName.rdfs__label = 'person name',
               personName.skos__definition = 'designation by which someone is known in some context'

CREATE (person)-[:hasName {
  materialized: true,
  uri: 'https://www.omg.org/spec/Commons/Designators/hasName',
  skos__definition: 'is known by',
  cardinality: '0..*'
}]->(personName)
```

**Key rules for enrichment relationships:**
- Always set `materialized: true` on relationship properties
- Include `uri`, `skos__definition`, and `cardinality` on each relationship
- Use `MERGE` for target nodes (to avoid duplicates) and `CREATE` for relationships
- Standard cardinality values: `1`, `0..1`, `0..*`, `1..*`

### Creating Custom Classes
When FIBO doesn't have a class you need, create it in staging with a custom URI namespace.

**Example — Creating Tax Payer:**
```cypher
CREATE (tp:owl__Class {
  rdfs__label: 'tax payer',
  uri: 'https://example.org/ontology/TaxPayer',
  skos__definition: 'A person who is obligated to pay taxes and is identified by a tax identifier.'
})

// Inheritance
WITH tp
MATCH (person:owl__Class {rdfs__label: 'person'})
CREATE (tp)-[:rdfs__subClassOf {
  materialized: true,
  skos__definition: 'A tax payer is a person.'
}]->(person)

// Associations
WITH tp
MATCH (taxId:owl__Class {rdfs__label: 'tax identifier'})
CREATE (tp)-[:hasTaxId {
  materialized: true,
  uri: 'https://example.org/ontology/hasTaxId',
  skos__definition: 'The tax identifier assigned to a tax payer.',
  cardinality: '1..*'
}]->(taxId)
```

**Rules for custom classes:**
- Use `https://example.org/ontology/` as the URI namespace
- Use lowercase with spaces for `rdfs__label` (e.g., `'tax payer'`)
- Use PascalCase for the URI fragment (e.g., `TaxPayer`)
- Always include `skos__definition`
- Use `rdfs__subClassOf` for inheritance relationships

### Enriching with Datatype Properties (Inline)
For simple value-type properties, create `rdfs__Datatype` nodes directly instead of full classes.

**Example — Enriching Conventional Street Address as US Physical Address:**
```cypher
MATCH (addr:owl__Class {rdfs__label: 'conventional street address'})

MERGE (sa:rdfs__Datatype {uri: '...'})
  ON CREATE SET sa.rdfs__label = 'streetAddress', sa.xsd__type = 'xsd:string',
               sa.skos__definition = 'primary address number, street name, suffix'

MERGE (zip:rdfs__Datatype {uri: '...'})
  ON CREATE SET zip.rdfs__label = 'zipCode', zip.xsd__type = 'xsd:string',
               zip.skos__definition = 'US postal ZIP code'

MERGE (city:rdfs__Datatype {uri: '...'})
  ON CREATE SET city.rdfs__label = 'city', city.xsd__type = 'xsd:string'

MERGE (state:rdfs__Datatype {uri: '...'})
  ON CREATE SET state.rdfs__label = 'state', state.xsd__type = 'xsd:string'

CREATE (addr)-[:hasStreetAddress {materialized: true, cardinality: '1'}]->(sa)
CREATE (addr)-[:hasZipCode {materialized: true, cardinality: '1'}]->(zip)
CREATE (addr)-[:hasCity {materialized: true, cardinality: '1'}]->(city)
CREATE (addr)-[:hasState {materialized: true, cardinality: '1'}]->(state)
```

**Common XSD types:**
- `xsd:string` — names, codes, identifiers, addresses
- `xsd:date` — dates (dateOfBirth, dateOfDeath)
- `xsd:integer` — whole numbers (age)
- `xsd:decimal` — monetary amounts
- `xsd:boolean` — true/false flags

### Creating Named Individuals
Create instances of classes using `owl__NamedIndividual` nodes with `rdf__type` links.

**Example — Creating United States of America:**
```cypher
MATCH (country:owl__Class {rdfs__label: 'country'})

CREATE (usa:owl__NamedIndividual {
  rdfs__label: 'United States of America',
  uri: 'https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/UnitedStatesOfAmerica',
  skos__definition: 'country in North America'
})
CREATE (usa)-[:rdf__type {materialized: true}]->(country)

// Link to a class that uses this individual
WITH usa
MATCH (addr:owl__Class {rdfs__label: 'conventional street address'})
CREATE (addr)-[:defaultCountry {materialized: true, cardinality: '1'}]->(usa)
```

If you need instance data attributes (for example, ISO codes), model them as relationships to `rdfs__Datatype` nodes instead of inline properties.

**Rules for named individuals:**
- Label: `owl__NamedIndividual`
- Must have `rdf__type` relationship to its class
- Keep only metadata properties on the node (`rdfs__label`, `uri`, `skos__definition`)
- Model all domain data attributes as relationships to `rdfs__Datatype` nodes
- Use official URIs (e.g., FIBO/LCC) when available

### Consolidating Inheritance
If data is already in staging but still has parent-child links, use `consolidate_inheritance`.
- **Purpose**: Flatten the hierarchy so each class is fully descriptive on its own.
- **When**: Use this after staging classes if you didn't use `flatten_inheritance` during the initial copy.

### Structural Consolidation (Class → Datatype)
Use `consolidate_staging_db` to convert complex classes into simpler datatypes.

**Example — Converting date classes to datatypes:**
```python
consolidate_staging_db(transformations=[
    {"old_label": "date of birth", "new_label": "dateOfBirth", "xsd_type": "xsd:date"},
    {"old_label": "date of death", "new_label": "dateOfDeath", "xsd_type": "xsd:date"},
    {"old_label": "person name",   "new_label": "personName",   "xsd_type": "xsd:string"},
    {"old_label": "age",           "new_label": "age",           "xsd_type": "xsd:integer"}
])
```

**When to consolidate:**
- Class acts purely as a value container (no outgoing relationships of its own)
- Class represents a simple scalar type (date, string, number)
- You want to simplify the UML diagram by reducing class boxes

### Enriching Location Classes
For location-type classes (place of birth, headquarters, etc.), use a mix of datatypes and class references.

**Example — Enriching Place of Birth:**
```cypher
MATCH (pob:owl__Class {rdfs__label: 'place of birth'})

MERGE (city:rdfs__Datatype {rdfs__label: 'city', xsd__type: 'xsd:string'})
MERGE (state:rdfs__Datatype {rdfs__label: 'stateOrProvince', xsd__type: 'xsd:string'})

MATCH (country:owl__Class {rdfs__label: 'country'})

CREATE (pob)-[:hasCity {materialized: true, cardinality: '0..1'}]->(city)
CREATE (pob)-[:hasStateOrProvince {materialized: true, cardinality: '0..1'}]->(state)
CREATE (pob)-[:hasCountry {materialized: true, cardinality: '1'}]->(country)
```

**Pattern**: Use datatypes for simple text fields (city, state names) and class references for complex objects (country with its own properties).

### Metadata Enrichment (AI-Driven)
For nodes (Classes) and relationships in `stagingdb` that are missing semantic documentation, use the LLM to generate `skos__definition` based on the context.

**Class Enrichment Workflow:**
1. Identify missing class definitions: `MATCH (n:owl__Class) WHERE n.skos__definition IS NULL RETURN n.rdfs__label, n.uri`
2. Generate with AI: Provide the class label and URI to the LLM.
3. Update Staging: `MATCH (n:owl__Class {uri: $uri}) SET n.skos__definition = $definition`

**Relationship Enrichment Workflow:**
1. Identify missing rel definitions: `MATCH (n:owl__Class)-[r]->(m) WHERE r.skos__definition IS NULL RETURN n.rdfs__label, type(r), m.rdfs__label, r.uri`
2. Generate with AI: Provide the relationship URI and the source/target labels to the LLM.
3. Update Staging: Set the generated definition on the relationship property in `stagingdb`.

### Full Schema Documentation
Maintain a textual representation of the entire graph schema for easy reference and LLM context.

**Tool:** `generate_neo4j_schema_description(database='stagingdb')`
**Purpose**: Generates a structured Markdown/text description:
1. **Node Labels**: URI and semantic definition.
2. **Relationship Types**: URI, definition, source/target, and cardinality.
3. **Node Properties**: **Data Type** (XSD or semantic class) and **Mandatory** status (existence requirement).

**Standard**: Ensure the Markdown output includes dedicated columns for `Data Type` and `Mandatory` in the properties section.

**Enum Visibility Standard**:
- Ensure `owl__NamedIndividual` members and `rdf__type` links are represented in schema artifacts.
- Ensure the schema description includes an explicit enumeration members section for review.

### Data Schema Constraints (Archival)
To ensure data integrity, maintain a Cypher constraints file (for example, `staging/staging_schema_constraint.cypher`) that defines the physical constraints of the Neo4j database.

**Core Principles:**
1. **Separate Metadata**: Metadata properties like `uri`, `skos__definition`, and `rdfs__label` should NOT have constraints or persistent indexes in the archival script (keep them as comments only).
2. **Enforce Structural Schema**: Mandatory properties (cardinality starting with `1`) MUST have existence constraints (`IS NOT NULL`).
3. **Keep in Sync**: Generate or update the constraints file from current graph metadata as part of your release workflow (scripted or manual), and verify it against `stagingdb` before applying.
4. **Enum-Aware Notes**: Keep mandatory enum/class relationships documented as comments in the generated constraints output (while reserving physical `IS NOT NULL` constraints for datatype-backed node properties).

### Regeneration Workflow (After Enum or Relationship Updates)
After changing enum classes, named individuals, or mandatory relationships, regenerate in this order:
1. `extract_data_model(database='stagingdb')` -> `staging/full_schema_data_model.json`
2. `generate_schema_code(target_type='pydantic', database='stagingdb')` -> `staging/schema_models.py`
3. `generate_neo4j_schema_description(database='stagingdb')` -> `staging/schema_description.md`
4. `generate_neo4j_schema_constraint(database='stagingdb')` -> `staging/stagingdb_constraints_mcp.cypher`

### Domain Model Consistency (Pydantic)
To ensure the generated code is fully compatible with the graph, follow these Pydantic modeling standards:

**Key Patterns:**
1. **URI Identity**: All core classes should inherit from a `SemanticModel` base class that includes an optional `uri: str` field.
2. **Field Aliases**: Use `Field(alias="...")` to map Python field names to their ontological counterparts (the Neo4j relationship types or property names). This allows for clean Python code while maintaining strict graph parity.
   - Example: `taxableIncome: Optional[MonetaryAmount] = Field(alias="hasTaxableIncome", ...)`
3. **Automated Bridge**: Use the `PydanticNeo4jBridge` utility to automate the conversion between Pydantic objects and Neo4j `MERGE` queries. This utility leverages the aliases to identify the correct graph predicates.

**Why**: This 1:1 parity between the domain model and the graph schema enables type-safe, automated data ingestion and extraction without manual Cypher mapping.

### Effective Node Label Heuristic (Documentation Filtering)
When generating final documentation (like `staging_schema.md`), use instance counts and topological activity to distinguish between primary Entity Classes and metadata/flattened classes.

**Filtering Logic (Effective Label Calculation):**
1.  **Direct Instances**: Any label with `count > 0` in the database is considered an effective Entity Class.
2.  **Topological Activity**: Labels with outgoing relationships are considered structural classes and should be included.
3.  **Domain Baseline**: Core entities (e.g., `Person`, `Employer`, `Account`, `Form1010`) are always kept regardless of instances.
4.  **Leaf Node Rule (Exclusion)**: Labels with zero instances AND no outgoing relationships should be treated as **Datatypes** or **Enums**, even if they appear in the graph topology. They should be excluded from the main "Node Labels (Classes)" table but described in the "Graph Topology" and "Node Properties" sections.
5.  **Pydantic Enum Filter**: Explicitly exclude any class that is implemented as a Pydantic `Enum` (identified by `enumValues` or `xsd_type` in metadata) from the Classes table.

**Why**: This ensures the documentation matches the actual implemented model (where many ontological classes are flattened into properties) rather than listing every technical label used in the graph.

### ⚠️ CRITICAL: No Inline Properties on Named Individuals
**NEVER store data attributes as inline properties on `owl__NamedIndividual` nodes.** All attributes must be modeled as relationships to `rdfs__Datatype` nodes.

❌ **WRONG** — inline properties:
```cypher
CREATE (w2:owl__NamedIndividual {
  rdfs__label: 'W-2',
  box1_wages: 'decimal',      // WRONG: inline property
  box2_taxWithheld: 'decimal'  // WRONG: inline property
})
```

✅ **CORRECT** — relationships to datatypes:
```cypher
CREATE (w2:owl__NamedIndividual {
  rdfs__label: 'W-2',
  uri: '...',
  skos__definition: '...'
})

MERGE (wages:rdfs__Datatype {rdfs__label: 'wagesTipsOtherComp'})
  ON CREATE SET wages.xsd__type = 'xsd:decimal',
               wages.skos__definition = 'Box 1: Total wages, tips, and other compensation'

CREATE (w2)-[:hasWagesTipsOtherComp {materialized: true, cardinality: '1'}]->(wages)
```

**Why**: Named individuals should only have metadata properties (`rdfs__label`, `uri`, `skos__definition`). All domain attributes must be expressed as graph relationships so they appear correctly in UML/Pydantic visualizations and can be properly queried.

### ⚠️ CRITICAL: Promote Schema Types to Classes, Not Named Individuals
**When a concept represents a type/template (e.g., a form type, document type), model it as `owl__Class` with `rdfs__subClassOf`, NOT as `owl__NamedIndividual` with `rdf__type`.**

Use `owl__NamedIndividual` ONLY for true singleton instances (e.g., "United States of America", "US Dollar").

❌ **WRONG** — form type as named individual:
```cypher
CREATE (f:owl__NamedIndividual {rdfs__label: 'Form 1040'})
CREATE (f)-[:rdf__type]->(report)  // WRONG: rdf__type implies instance
```

✅ **CORRECT** — form type as class:
```cypher
CREATE (f:owl__Class {rdfs__label: 'Form 1040', uri: '...', skos__definition: '...'})
CREATE (f)-[:rdfs__subClassOf {materialized: true}]->(report)  // Subclass hierarchy
```

**To convert existing named individuals to classes:**
```cypher
MATCH (f:owl__NamedIndividual {rdfs__label: 'Form 1040'})
REMOVE f:owl__NamedIndividual
SET f:owl__Class
WITH f
MATCH (f)-[oldType:rdf__type]->(c)
DELETE oldType
WITH DISTINCT f
MATCH (parent:owl__Class {rdfs__label: 'report'})
MERGE (f)-[:rdfs__subClassOf {materialized: true}]->(parent)
```

**When to use which:**
| Concept | Node Type | Relationship |
|---|---|---|
| W-2 form, Form 1040, Form 1120 | `owl__Class` | `rdfs__subClassOf → report` |
| United States of America | `owl__NamedIndividual` | `rdf__type → country` |
| US Dollar, Euro | `owl__NamedIndividual` | `rdf__type → currency` |

## Best Practices
- **Isolation**: Always work on `stagingdb` to avoid polluting the main ontology.
- **Consistency**: Use camelCase for relationship types and lowercase with spaces for class labels.
- **Integrity**: Verify results after each enrichment: `MATCH (c {rdfs__label: '...'})-[r]->(t) RETURN type(r), t.rdfs__label`
- **Reuse nodes**: Always `MERGE` target nodes by URI to avoid duplicates (e.g., `country`, `city` datatypes).
- **FIBO first**: Check the FIBO ontology for existing definitions before creating custom classes.
- **Deduplication**: The `consolidate_staging_db` tool automatically de-duplicates URIs, labels, and relationships.
- **Consolidation cleanup**: `consolidate_staging_db` automatically deletes named individuals linked via `rdf__type` when converting a class to a datatype.
