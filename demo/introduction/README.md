# Onto2AI Introduction Demo

This folder contains the standard, repeatable generation flow for the Onto2AI Toolset introduction demo.

## Standard Flow

The demo is generated from durable inputs and writes transient render work to the system temp directory:

1. `introduction-script.md` is a long-form editorial reference; accepted changes must be synchronized into the manifest.
2. `demo/video/introduction/introduction_demo.json` is the production source for slide content, narration text, timing, audio path, and video path.
3. `generate_introduction_video.py` reads the manifest, rebuilds narration timing, and writes the derived narration text.
4. `render_introduction_template_deck.mjs` renders the LinkedIn-style deck and slide frames through the presentation artifact tool.
5. `demo/audio/onto2ai_introduction_cedar.mp3` provides OpenAI `cedar` narration.
6. `demo/video/review/onto2ai_introduction_template.mp4` is the final review video.

## Durable Inputs

- `assets/onto2ai-qa-frontpage-4.png` - local copy of the LinkedIn article visual used as the cover/background style source.
- `introduction-script.md` - editorial narration reference; the current generator does not parse it.
- `onto2ai-linkedin-presentation-template.pptx` - editable template based on the Onto2AI LinkedIn article visual style.
- `../video/introduction/introduction_demo.json` - production manifest for slide content, narration, timing, and outputs.

## Generated Deliverables

- `onto2ai-introduction-template-video-deck.pptx` - populated editable deck used for video rendering.
- `../audio/onto2ai_introduction_cedar.mp3` - OpenAI `cedar` narration.
- `../video/introduction/introduction_demo.json` - single source of truth manifest for scenes, timing, slide content, audio, and output paths.
- `../video/introduction/introduction_narration.txt` - narration text derived from the manifest.
- `../video/review/onto2ai_introduction_template.mp4` - final template-style introduction video.

## Regenerate

Prerequisites:

- `ffmpeg` and `ffprobe`
- Node.js
- `uv`
- presentation artifact-tool setup from the installed presentations skill
- `OPENAI_API_KEY` only when refreshing narration with `--refresh-audio`

Reuse the existing `cedar` audio:

```bash
python3 demo/introduction/generate_introduction_video.py
```

Refresh the OpenAI `cedar` narration and rebuild the video:

```bash
python3 demo/introduction/generate_introduction_video.py --refresh-audio
```

Use `--keep-work` only when debugging rendered frames or segment assembly.

If the presentation skill path changes, set `ONTO2AI_PRESENTATION_SKILL_DIR`.
If the speech CLI path changes, set `ONTO2AI_TTS_SCRIPT`.
