# Release Notes: v1.1.0

## Summary

`v1.1.0` is the MCP-aligned domain adaptation baseline for Onto2AI Toolset.

This milestone captures the current stable state before the Modeller UI is expanded into an industry-ontology adaptation studio. It preserves the existing package, MCP, loader, domain-packaging, and Modeller behavior as the release baseline for the next workflow increment.

## Highlights

- hardened ontology loading and local-only loader behavior
- aligned the Onto2AI MCP tool surface with Modeller browsing APIs
- added Modeller-style MCP tools for model classes, relationships, individuals, datatypes, hierarchy, and focus graphs
- aligned `get_materialized_schema` relationship scope with Modeller class detail behavior
- kept code/model extraction on an outgoing-only materialized schema path so generated artifacts remain directionally stable
- documented independent packaging for domain models as outputs of the toolset
- retained FIBO, entitlement, and parcel domain outputs as examples rather than core package contents

## Why This Milestone Matters

This release is the baseline for the next product direction:

1. start from a trusted industry ontology such as FIBO
2. discover and extract a relevant domain subset
3. review and tune that subset in Onto2AI Modeller
4. generate prototype application artifacts
5. finalize and publish the result as an enterprise ontology or domain pack

The next development milestone can now focus on Modeller UI and MCP-powered workflow enhancements without mixing those changes into the baseline release.

## Validation

Release verification should pass with:

```bash
python scripts/harness_verify_release.py
```

Focused regression coverage includes:

```bash
python -m unittest tests.test_onto2ai_loader
python -m unittest tests.test_onto2ai_mcp
```

## Package Version

- Package version: `1.1.0`
- Modeller API version: `1.1.0`
