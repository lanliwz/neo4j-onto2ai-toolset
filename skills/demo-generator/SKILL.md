---
name: demo-generator
description: Generate or revise Onto2AI demo manifests, presentation review videos, and screen-recording demo skeletons. Use for introduction, entitlement, and other standardized product demos.
---
# Demo Generator Instructions

Use this skill when the user wants to create, regenerate, or standardize Onto2AI demo production files.

## Standard Demo Model

The current standard is the introduction demo:

- manifest-driven
- manifest-first
- presentation-rendered
- narrated with OpenAI `cedar`
- final review video under `demo/video/review/`

Use `demo/README4DEMO` as the workflow overview and `demo/introduction/README.md` as the reference implementation notes.

## Canonical Tool

- Script: `demo/introduction/generate_introduction_video.py`
- Durable script: `demo/introduction/introduction-script.md`
- Manifest output: `demo/video/introduction/introduction_demo.json`
- Narration output: `demo/video/introduction/introduction_narration.txt`
- Audio output: `demo/audio/onto2ai_introduction_cedar.mp3`
- Video output: `demo/video/review/onto2ai_introduction_template.mp4`

The entitlement demo uses the parallel canonical generator and outputs:

- Script: `demo/entitlement/generate_entitlement_video.py`
- Editorial source: `demo/entitlement/entitlement-script.md`
- Manifest: `demo/video/entitlement/entitlement_demo.json`
- Video: `demo/video/review/onto2ai_entitlement_template.mp4`

## Regenerate The Introduction Demo

Reuse the existing OpenAI `cedar` narration:

```bash
python3 demo/introduction/generate_introduction_video.py
```

Refresh the OpenAI `cedar` narration and rebuild the video:

```bash
python3 demo/introduction/generate_introduction_video.py --refresh-audio
```

Keep scratch frames and segment files for debugging:

```bash
python3 demo/introduction/generate_introduction_video.py --keep-work
```

## Manifest Contract

Every generated demo should have exactly one canonical manifest at:

```text
demo/video/<demo_name>/<demo_name>_demo.json
```

The manifest must carry:

- `narrative_lines[].text` is authoritative narration content.
- `narrative_lines[].start_ms` / `end_ms` are authoritative timing values.
- `slides[]` or scene records define what is rendered.
- `output_audio` points to the narration artifact.
- `output_video` points to the review/final video artifact.

The JSON manifest is authoritative for production narration and slides. Long-form Markdown scripts are editorial references and are not parsed by the current generators; when an editorial script changes, update the manifest explicitly before regeneration.

## Presentation-Style Demo Rules

- Keep durable source files under `demo/<demo_name>/`.
- Keep generated narration under `demo/audio/`.
- Keep the manifest and derived narration under `demo/video/<demo_name>/`.
- Keep final review videos under `demo/video/review/`.
- Write temporary rendered frames and video segments to the system temp directory.
- Verify final MP4 output with `ffprobe`.
- For the introduction demo, expected output is `1280x720`, `30fps`, H.264 video, AAC audio.

## Future Screen-Recording Demos

For UI walkthroughs based on raw recordings, follow the same file contract:

- raw recording: `demo/video/<demo_name>/<demo_name>.mov`
- manifest: `demo/video/<demo_name>/<demo_name>_demo.json`
- narration: `demo/audio/<demo_name>_cedar.mp3`
- final review export: `demo/video/review/<demo_name>_synced_with_voice.mp4`

When creating a new screen-recording demo, build the manifest first, then derive narration audio and mux it into the recording. Do not depend on the old recording-only helper pattern; the manifest-first workflow is now the standard path.

## Preconditions

- `ffmpeg` and `ffprobe` are required for video assembly and verification.
- `OPENAI_API_KEY` and network access are required only when refreshing TTS audio.
- Node.js is required for the introduction deck renderer.
