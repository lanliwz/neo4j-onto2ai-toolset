# Onto2AI Modeller: Custodian Wealth Management

## Editorial Script

This demonstration uses a fictional institution, Northstar Custody Bank, to
show how Onto2AI Modeller helps a financial institution create an application
domain ontology without starting from a blank page.

Northstar is onboarding Harbor Ridge Family Office, another fictional entity,
to a custody and wealth-management platform. The demonstrable outcome is a
trace from the approved client through its USD custody account and portfolio to
a holding, settlement instruction, and completed cash movement. Teams use
different meanings for those concepts, so starting directly with application
classes would encode disagreement before the organization resolves it.

The modeller starts in Source Ontology. We search FIBO for account, payment,
party, financial instrument, and currency concepts. Search results are not
accepted merely because their labels look familiar. We inspect definitions,
stable URIs, properties, inheritance, and incoming and outgoing relationships.

Selected concepts become extraction seeds. Onto2AI MCP discovers the supporting
semantic neighborhood and copies the focused subset into `stagingdb`. FIBO
remains unchanged, while the extracted target becomes Northstar's governed
working model with source provenance retained.

The target ontology is customized for the application. Northstar introduces
Custodian Client, Custody Account, Custody Portfolio, Custody Holding, Cash
Movement, Settlement Instruction, Service Agreement, and Client Onboarding
Case. Definitions, relationship names, cardinalities, required properties,
enterprise identifiers, and four lifecycle vocabularies are refined.

Customization is reviewed through three synchronized views. Ontology View
checks meaning and provenance. UML checks class structure, association
multiplicity, and inheritance. Application Schema shows the fields, types,
collections, references, enumerations, and validation rules that application
teams will consume.

The review is iterative. Broad inherited client, portfolio, holding, agreement,
and onboarding fields expose a modelling issue. Northstar keeps exact source
provenance but treats those concepts as application-focused adaptations. It
retains formal FIBO inheritance only for Custody Account and Cash Movement,
where selected Account and Payment behavior is useful.

Semantic Interaction supports the design discussion. The team can ask which
FIBO concepts are unnecessary, what is missing for settlement, and whether the
target model supports custody and wealth workflows without importing unrelated
industry complexity.

The Harbor Ridge smoke test uses an isolated dataset database. It loads 21
application instances and 26 application relationships, with no ontology
schema nodes or ontology-only relationships. The test proves one complete path
from Harbor Ridge through custody account and settlement instruction to payment
reference `PAY-2026-000731`.

The accepted prototype is the handoff into Ontology and Release modes. After
canonical RDF authoring, schema alignment, package validation, and release gates
pass, the result will be the versioned `northstar-client-ontology` package with
provenance, application schemas, constraints, validation reports, sample data,
and release metadata.

The reusable method is the point of the demo: discover trusted industry
semantics, extract only what matters, customize through semantic and
implementation views, validate against the application, and publish the
finalized domain ontology.
