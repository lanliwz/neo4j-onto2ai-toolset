# Release Notes: v1.0.0

## Summary

`v1.0.0` is the first harness-compatible release of Onto2AI Toolset.

This release marks the shift from a collection of powerful scripts and workflows to a more controlled agent engineering system with explicit operating modes, feedforward checks, verification entrypoints, and lightweight audit logging.

## Highlights

- introduced explicit harness operating modes:
  - ontology mode
  - schema mode
  - dataset mode
  - release mode
- added repo-level harness guidance:
  - `AGENTS.md`
  - `docs/harness/modes.md`
  - `docs/harness/checklists.md`
- added generic harness entrypoints under `scripts/`:
  - `harness_preflight.py`
  - `harness_verify_ontology.py`
  - `harness_verify_mode_boundaries.py`
  - `harness_verify_release.py`
  - `harness_run.py`
- added lightweight JSONL audit logging for harness runs:
  - `log/harness_runs.jsonl`
- updated generic toolset docs to use the harness flow:
  - `README.md`
  - `docs/quickstart.md`
  - `docs/operator-runbook.md`

## Why This Is A Major Release

`v1.0.0` represents a major-version boundary because the repo now has an explicit operational contract for ontology work:

- work is classified by mode before changes begin
- ontology, schema, dataset, and release concerns are separated
- release verification is a first-class part of the workflow
- generic harness checks can be run through a single command

This is a meaningful maturity step for the toolset itself, not just an incremental package update.

## Generic Harness Commands

```bash
python scripts/harness_run.py verify
python scripts/harness_run.py release
python scripts/harness_verify_ontology.py
python scripts/harness_verify_mode_boundaries.py
python scripts/harness_verify_release.py --build
```

## Validation

The release flow for `v1.0.0` was verified with:

- ontology verification
- mode-boundary verification
- release verification
- build-backed release verification producing:
  - `dist/onto2ai_engineer-1.0.0-py3-none-any.whl`
  - `dist/onto2ai_engineer-1.0.0.tar.gz`

## Known Follow-Up

The build still emits pre-existing `setuptools` warnings around `onto2ai_modeller.static*` package discovery. The build succeeds, but that cleanup remains separate follow-up work.
