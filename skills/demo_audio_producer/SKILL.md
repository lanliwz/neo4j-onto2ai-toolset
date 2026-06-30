---
name: "Demo Audio Producer"
description: "Create Onto2AI product demo narration and OpenAI cedar audio files aligned to demo manifests."
---
# Demo Audio Producer Instructions

Use this skill when the user asks to create or update demo walkthrough content, voiceover scripts, narrated audio files, or demo audio for the standard Onto2AI introduction workflow.

## Scope
- Maintain demo assets under `demo/`.
- Keep narration scripts and audio outputs aligned.
- Use AI-generated voice narration for quick review and presentation drafts.
- Treat `demo/video/<demo_name>/<demo_name>_demo.json` as the single source of truth for narration text, timing, audio path, and final video path.
- For the introduction demo, prefer `demo/introduction/generate_introduction_video.py` because it builds narration text, audio, deck frames, and final review video from one manifest.

## Standard Output Layout
- `demo/introduction/introduction-script.md` - long-form source script for the standard introduction demo.
- `demo/introduction/generate_introduction_video.py` - canonical generator for the introduction video.
- `demo/audio/*.mp3` - generated narration files.
- `demo/video/<demo_name>/<demo_name>_demo.json` - single source of truth manifest.
- `demo/video/<demo_name>/*_narration.txt` - manifest-derived narration text.
- `demo/video/review/*.mp4` - rendered review videos.

## File Contract (Purpose + When to Use)
- `demo/introduction/introduction-script.md`
  Purpose: story source for the standard introduction demo.
  When to use: revise the demo message, structure, or voiceover.
- `demo/introduction/generate_introduction_video.py`
  Purpose: repeatable generator for manifest, narration text, audio, deck render, and final MP4.
  When to use: regenerate or refresh the introduction demo.
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
1. Update the durable script or manifest first.
2. Derive narration text from `narrative_lines[].text` in the manifest.
3. Generate audio into `demo/audio/`.
4. Verify expected file count, duration, and naming.
5. Keep all reusable demo assets in `demo/`; write temporary frames and segments to the system temp directory.

## Introduction Demo Audio
Reuse the existing OpenAI `cedar` narration:

```bash
python3 demo/introduction/generate_introduction_video.py
```

Refresh the OpenAI `cedar` narration and rebuild the review video:

```bash
python3 demo/introduction/generate_introduction_video.py --refresh-audio
```

## Single Clip Generation
Use when iterating one demo's audio only.

```bash
# derive narration from JSON manifest
jq -r '.narrative_lines | sort_by(.start_ms) | .[].text' \
  demo/video/introduction/introduction_demo.json \
  > demo/video/introduction/introduction_narration.txt

python /Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py speak \
  --model gpt-4o-mini-tts-2025-12-15 \
  --input-file demo/video/introduction/introduction_narration.txt \
  --voice cedar \
  --response-format mp3 \
  --instructions "Voice Affect: Warm and composed. Tone: Professional and clear. Pacing: Steady." \
  --out demo/audio/onto2ai_introduction_cedar.mp3 \
  --force
```

## Batch Audio Generation
Use this only when a future demo has a maintained JSONL batch file:

```bash
python /Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py speak-batch \
  --input demo/<demo_name>_tts_jobs.jsonl \
  --out-dir demo/audio \
  --model gpt-4o-mini-tts-2025-12-15 \
  --voice cedar \
  --response-format mp3 \
  --instructions "Voice Affect: Warm and composed. Tone: Professional and friendly. Pacing: Steady and clear." \
  --rpm 50 \
  --force
```

## Quality Rules
- Keep each narration clip concise and presentation-ready.
- Use deterministic file names like `onto2ai_introduction_cedar.mp3` or `<demo_name>_cedar.mp3`.
- If script text changes, regenerate the corresponding audio files.
- Disclose that generated narration is AI voice when presenting externally.
- Use `*_demo.json` as the single source of truth for both text and timing.
- Use OpenAI TTS model `gpt-4o-mini-tts-2025-12-15`, voice `cedar`, and MP3 output unless the user explicitly asks otherwise.

## Screen Recording Sync (Voice + Video)
To attach narration to a screen recording:

```bash
ffmpeg -y \
  -i demo/video/<demo_name>/<demo_name>.mov \
  -i demo/audio/<demo_name>_cedar.mp3 \
  -filter_complex "[1:a]apad[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  demo/video/review/<demo_name>_synced_with_voice.mp4
```

Optional timing offset (example +3 seconds):

```bash
ffmpeg -y \
  -i demo/video/<demo_name>/<demo_name>.mov \
  -i demo/audio/<demo_name>_cedar.mp3 \
  -filter_complex "[1:a]adelay=3000|3000,apad[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  demo/video/review/<demo_name>_synced_with_voice_offset3s.mp4
```

## Preconditions
- `OPENAI_API_KEY` must be set for live audio generation.
- Network access is required for API calls.
- Use the existing audio file when the user does not ask to refresh narration.
