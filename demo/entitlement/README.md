# Onto2AI Entitlement Demo

This folder contains the standard, repeatable generation flow for the Onto2AI entitlement demo.

## Standard Flow

The demo follows the introduction demo pattern:

1. `entitlement-script.md` defines the durable story source.
2. `demo/video/entitlement/entitlement_demo.json` is the production source for slide content, narration text, timing, audio path, and video path.
3. `generate_entitlement_video.py` reads the manifest, rebuilds narration timing, and writes the derived narration text.
4. `render_entitlement_template_deck.mjs` renders the LinkedIn-style deck and slide frames through the presentation artifact tool.
5. `demo/audio/onto2ai_entitlement_cedar.mp3` provides OpenAI `cedar` narration when narration is refreshed.
6. `demo/video/review/onto2ai_entitlement_template.mp4` is the final review video.

## Durable Inputs

- `assets/onto2ai-qa-frontpage-4.png` - local copy of the LinkedIn article visual used as the cover/background style source.
- `entitlement-script.md` - full narration script and story source.
- `onto2ai-linkedin-presentation-template.pptx` - editable template based on the Onto2AI LinkedIn article visual style.
- `../video/entitlement/entitlement_demo.json` - production manifest for slide content, narration, timing, and outputs.

## Generated Deliverables

- `onto2ai-entitlement-template-video-deck.pptx` - populated editable deck used for video rendering.
- `../audio/onto2ai_entitlement_cedar.mp3` - OpenAI `cedar` narration, generated when `--refresh-audio` is used.
- `../video/entitlement/entitlement_demo.json` - single source of truth manifest for scenes, timing, slide content, audio, and output paths.
- `../video/entitlement/entitlement_narration.txt` - narration text derived from the manifest.
- `../video/review/onto2ai_entitlement_template.mp4` - final template-style entitlement video.

## Regenerate

Prerequisites:

- `ffmpeg` and `ffprobe`
- Node.js
- `uv`
- presentation artifact-tool setup from the installed presentations skill
- `OPENAI_API_KEY` only when refreshing narration with `--refresh-audio`

Reuse existing `cedar` audio after it has been generated:

```bash
python3 demo/entitlement/generate_entitlement_video.py
```

Render a no-network silent review video:

```bash
python3 demo/entitlement/generate_entitlement_video.py --silent
```

Refresh the OpenAI `cedar` narration and rebuild the video:

```bash
python3 demo/entitlement/generate_entitlement_video.py --refresh-audio
```

Use `--keep-work` only when debugging rendered frames or segment assembly.

If the presentation skill path changes, set `ONTO2AI_PRESENTATION_SKILL_DIR`.
If the speech CLI path changes, set `ONTO2AI_TTS_SCRIPT`.
