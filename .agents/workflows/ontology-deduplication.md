---
description: How to refine and deduplicate an OWL Ontology
---

# Ontology Refinement and Deduplication Workflow

This workflow describes the process of refining and deduplicating object properties in an RDF ontology file.

1. **Cross-Check Labels and Definitions**
Before deduplication, manually or programmatically scan the ontology to identify meaningless, ambiguous, or inconsistent labels and definitions. Ensure:
- Acronyms are properly expanded (e.g., `HO` -> `Head Office`, `Tpty` -> `Triparty` or `Third Party`).
- OCR artifacts are corrected (e.g., `Prud` -> `Provider`).
- Generic definitions are replaced with specific, formal financial definitions.
- All object properties comply with the FIBO Ontology Conventions specified in `skills/fibo_ontology_conventions/SKILL.md`.

2. **Verify the Python script is available**
Ensure that the reusable script `scripts/deduplicate_ontology.py` is present in the workspace.

3. **Run the deduplication script**
Specify the file path to the RDF file you wish to deduplicate.
// turbo
```bash
python3 scripts/deduplicate_ontology.py resource/ontology/www_onto2ai-toolset_com/ontology/bank/AssetManagement.rdf
```

4. **Verify the changes**
Review the ontology file to ensure the duplicated properties were removed successfully and all labels remaining are clean and consistent.
