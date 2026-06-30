# Onto2AI Introduction Demo

This folder contains the standard, repeatable generation flow for the Onto2AI Toolset introduction demo.

## Standard Flow

The demo is generated from durable inputs and writes transient render work to the system temp directory:

1. `introduction-script.md` defines the long-form introduction script.
2. `generate_introduction_video.py` builds the demo manifest and narration text.
3. `render_introduction_template_deck.mjs` renders the LinkedIn-style deck and slide frames through the presentation artifact tool.
4. `demo/audio/onto2ai_introduction_cedar.mp3` provides OpenAI `cedar` narration.
5. `demo/video/review/onto2ai_introduction_template.mp4` is the final review video.

## Durable Inputs

- `assets/onto2ai-qa-frontpage-4.png` - local copy of the LinkedIn article visual used as the cover/background style source.
- `introduction-script.md` - full narration script and story source.
- `onto2ai-linkedin-presentation-template.pptx` - editable template based on the Onto2AI LinkedIn article visual style.

## Generated Deliverables

- `onto2ai-introduction-template-video-deck.pptx` - populated editable deck used for video rendering.
- `../audio/onto2ai_introduction_cedar.mp3` - OpenAI `cedar` narration.
- `../video/introduction/introduction_demo.json` - single source of truth manifest for scenes, timing, slide content, audio, and output paths.
- `../video/introduction/introduction_narration.txt` - narration text derived from the manifest.
- `../video/review/onto2ai_introduction_template.mp4` - final template-style introduction video.

## Regenerate

Reuse the existing `cedar` audio:

```bash
python3 demo/introduction/generate_introduction_video.py
```

Refresh the OpenAI `cedar` narration and rebuild the video:

```bash
python3 demo/introduction/generate_introduction_video.py --refresh-audio
```

Use `--keep-work` only when debugging rendered frames or segment assembly.
