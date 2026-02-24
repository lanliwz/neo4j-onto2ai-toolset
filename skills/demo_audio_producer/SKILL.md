---
name: "Demo Audio Producer"
description: "Create Onto2AI product demos and generate AI narration audio files in the demo folder."
---
# Demo Audio Producer Instructions

Use this skill when the user asks to create or update demo walkthrough content, voiceover scripts, or narrated audio files.

## Scope
- Maintain demo assets under `demo/`.
- Keep narration scripts and audio outputs aligned.
- Use AI-generated voice narration for quick review and presentation drafts.

## Standard Output Layout
- `demo/demo-audio-scripts.md` — canonical script source.
- `demo/demo_tts_jobs.jsonl` — batch TTS job file.
- `demo/audio/*.mp3` — generated narration files.
- `demo/video/<demo_name>/<demo_name>_demo.json` — single source of truth manifest.
- `demo/video/review/*.mp4` — rendered review videos.

## File Contract (Purpose + When to Use)
- `demo/demo-audio-scripts.md`
  Purpose: master script catalog across demos.
  When to use: define or revise content before generating audio.
- `demo/demo_tts_jobs.jsonl`
  Purpose: batch job list for TTS (`input`, `out`).
  When to use: generate many audio clips in one pass.
- `demo/audio/<demo>.mp3`
  Purpose: narration output for one demo.
  When to use: attach to screen recording or review voice quality.
- `demo/video/<demo>/<demo>_demo.json`
  Purpose: canonical per-demo manifest (narrative text + timing + scenes + TTS config).
  When to use: every edit; avoid parallel duplicate files.
- `demo/video/review/*.mp4`
  Purpose: synced preview/final review outputs.
  When to use: approval rounds and iteration.

## Workflow
1. Draft or update `demo/demo-audio-scripts.md`.
2. Build/refresh `demo/demo_tts_jobs.jsonl` from script content (one JSON object per line with `input` and `out`).
3. Generate audio into `demo/audio/`.
4. Verify expected file count and naming.
5. Keep all demo assets in `demo/` (do not scatter files in `docs/` or `output/`).

## Single Clip Generation
Use when iterating one demo only.

```bash
# derive narration from JSON manifest
jq -r '.narrative_lines | sort_by(.start_ms) | .[].text' \
  demo/video/demo01/demo01_demo.json > /tmp/demo01_narration.txt

python /Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py speak \
  --input-file /tmp/demo01_narration.txt \
  --voice cedar \
  --response-format mp3 \
  --instructions "Voice Affect: Warm and composed. Tone: Professional and clear. Pacing: Steady." \
  --out demo/audio/demo01.mp3 \
  --force
```

## Audio Generation Command
Use the speech skill CLI:

```bash
python /Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py speak-batch \
  --input demo/demo_tts_jobs.jsonl \
  --out-dir demo/audio \
  --voice cedar \
  --response-format mp3 \
  --instructions "Voice Affect: Warm and composed. Tone: Professional and friendly. Pacing: Steady and clear." \
  --rpm 50 \
  --force
```

## Quality Rules
- Keep each narration clip concise and presentation-ready.
- Use deterministic file names like `demo01_*.mp3`, `demo02_*.mp3`, etc.
- If script text changes, regenerate the corresponding audio files.
- Disclose that generated narration is AI voice when presenting externally.
- Use `*_demo.json` as the single source of truth for both text and timing.

## Screen Recording Sync (Voice + Video)
To attach narration to a screen recording:

```bash
ffmpeg -y \
  -i demo/video/demo01.mov \
  -i demo/audio/demo01.mp3 \
  -filter_complex "[1:a]apad[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  demo/video/review/demo01_synced_with_voice.mp4
```

Optional timing offset (example +3 seconds):

```bash
ffmpeg -y \
  -i demo/video/demo01.mov \
  -i demo/audio/demo01.mp3 \
  -filter_complex "[1:a]adelay=3000|3000,apad[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  demo/video/review/demo01_synced_with_voice_offset3s.mp4
```

## Preconditions
- `OPENAI_API_KEY` must be set for live audio generation.
- Network access is required for API calls.
