# Designing and Publishing a Domain Package with Onto2AI

This demo is about how to use the Onto2AI toolset. Entitlement is the worked example, and the final proof is an independently consumable `onto2ai-entitlement` package.

Application teams often begin with code models, database constraints, and API contracts. Without a shared semantic source, those artifacts drift and every team rebuilds the same domain meaning differently.

The Onto2AI method starts with ontology. We define the domain concepts, relationships, restrictions, enumerations, and documentation in RDF. For entitlement, that includes users, policy groups, policies, row-filter rules, column-mask rules, and the protected data context.

RDF remains the source of truth. Onto2AI Modeller loads that ontology into the modelling workspace so the designer can inspect the ontology graph, review classes and relationships, and refine the model before generating implementation artifacts.

In Modeller, the same model can be reviewed through Ontology View, UML, and application code model views. These perspectives make inheritance, cardinality, required properties, and enumeration choices visible before they become application contracts.

Onto2AI MCP then turns ontology intent into aligned artifacts. For the entitlement example, it produces the full schema model, Neo4j query context, constraints, and a Pydantic application model. Pydantic is one supported target; the goal is any application code model.

The workflow is enforced through four Harness Modes. Ontology Mode validates RDF syntax, URI conventions, and package mirrors. Schema Mode checks generated artifacts and verifies the selected ontology in `stagingdb`.

Dataset Mode creates an isolated disposable database. It applies constraints, loads representative entitlement instances, validates required properties and application relationships, and proves that ontology-only nodes and edges did not leak into runtime data.

Release Mode runs the live gates, aligns package versions, builds the wheel and source distribution with `uv`, and inspects their contents. A release cannot pass by printing a checklist or skipping the package build.

The final `onto2ai-entitlement` package contains the ontology, generated schema artifacts, application code model, and reusable smoke test. Consumers receive the domain standard without depending on the Modeller workspace or copying the entire toolset.

Entitlement is only the example. The reusable Onto2AI workflow is: model meaning in RDF, inspect and refine it, generate aligned artifacts, test schema and runtime behavior, and publish an independent domain package.
