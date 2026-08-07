# Custodian Wealth Management Demo

This demo presents the Onto2AI Modeller workflow through a fictional global
custodian bank named Northstar Custody Bank. It does not represent or imply an
affiliation with any real financial institution.

The narration is AI-generated with the OpenAI `cedar` voice for demonstration
and review purposes.

The worked example starts from FIBO discovery, extracts a focused client and
custody subset into `stagingdb`, customizes the target model, reviews UML and
application schemas, validates the result, and prepares the fictional
`northstar-client-ontology` package for canonical RDF and release work.

The executable Harbor Ridge Family Office case is under `case/`. It includes
the exact source-selection decisions, the target-model acceptance criteria, a
domain-instance dataset, and a smoke-test harness. Start with
`case/README.md` when presenting the workflow in Modeller.

The review video is a Modeller UI walkthrough. Its durable UI captures are in
`assets/modeller/` and show Source Ontology search and preview, extraction
seeds, Target Ontology inspection, UML Diagram, Pydantic Models, Semantic
Interaction, and Native Query validation.

## Run the Case

Validate the case files without Neo4j:

```bash
.venv/bin/python demo/custodian_wealth/case/validate_case.py
```

Validate `stagingdb`, load the sample workflow into an isolated
`northstar-demo` database, and verify the client-to-payment trace:

```bash
set -a
source .env
set +a
.venv/bin/python demo/custodian_wealth/case/validate_case.py \
  --live-schema --live-data --reset-database
```

## Generate

Reuse the existing narration:

```bash
python3 demo/custodian_wealth/generate_custodian_wealth_video.py
```

Refresh OpenAI cedar narration and regenerate the video:

```bash
python3 demo/custodian_wealth/generate_custodian_wealth_video.py --refresh-audio
```

Render a silent review version without an API call:

```bash
python3 demo/custodian_wealth/generate_custodian_wealth_video.py --silent
```

## Outputs

- Editable deck: `demo/custodian_wealth/onto2ai-custodian-wealth-video-deck.pptx`
- Canonical manifest: `demo/video/custodian_wealth/custodian_wealth_demo.json`
- Narration: `demo/audio/onto2ai_custodian_wealth_cedar.mp3`
- Review video: `demo/video/review/onto2ai_custodian_wealth.mp4`
