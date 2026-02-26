# Demo Workflow Guide

This guide contains the single-manifest demo workflow, audio generation steps, and video sync commands.

## Folder Structure
- `demo/demo-audio-scripts.md` — master script catalog across demos.
- `demo/demo_tts_jobs.jsonl` — batch TTS job list (`input`, `out`).
- `demo/audio/*.mp3` — generated narration clips.
- `demo/video/<demo_name>/<demo_name>.mov` — raw screen recording.
- `demo/video/<demo_name>/<demo_name>_demo.json` — single source of truth (script + timing + scenes + TTS config).
- `demo/video/review/*.mp4` — review exports.
- `demo/demo_generator.py` — scaffolds demo workspace from `.mov`.

## Single Source of Truth
Use `*_demo.json` as the only canonical file for per-demo production data:
- `narrative_lines[].text` = narration content (authoritative text)
- `narrative_lines[].start_ms` / `end_ms` = exact timing
- `scenes[]` = visual plan and line references
- `tts` = voice/style config

This avoids drift between separate script/timing/shot files.

## Generate Demo Skeleton
```bash
# dry run
python demo/demo_generator.py demo/video/demo01_launch_modeller/demo01.mov --dry-run

# generate scaffold folder + single JSON manifest
python demo/demo_generator.py demo/video/demo01_launch_modeller/demo01.mov
```

## Generate Audio
```bash
# prerequisite
export OPENAI_API_KEY="your_openai_key"

# build narration text directly from manifest (single source of truth)
jq -r '.narrative_lines | sort_by(.start_ms) | .[].text' \
  demo/video/demo01/demo01_demo.json \
  > /tmp/demo01_narration.txt

# single clip from manifest-derived narration
python /Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py speak \
  --input-file /tmp/demo01_narration.txt \
  --voice cedar \
  --response-format mp3 \
  --instructions "Voice Affect: Warm and composed. Tone: Professional and clear. Pacing: Steady." \
  --out demo/audio/demo01.mp3 \
  --force

# batch generation for all demos
python /Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py speak-batch \
  --input demo/demo_tts_jobs.jsonl \
  --out-dir demo/audio \
  --voice cedar \
  --response-format mp3 \
  --instructions "Voice Affect: Warm and composed. Tone: Professional and friendly. Pacing: Steady and clear." \
  --rpm 50 \
  --force
```

## Sync Audio With Screen Recording
```bash
# sync narration to video, keeping full video length
ffmpeg -y \
  -i demo/video/demo01.mov \
  -i demo/audio/demo01.mp3 \
  -filter_complex "[1:a]apad[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  demo/video/review/demo01_synced_with_voice.mp4

# optional delay (+3 seconds)
ffmpeg -y \
  -i demo/video/demo01.mov \
  -i demo/audio/demo01.mp3 \
  -filter_complex "[1:a]adelay=3000|3000,apad[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  demo/video/review/demo01_synced_with_voice_offset3s.mp4
```

## Notes
- Narration audio is AI-generated.
- Keep all demo artifacts under `demo/` for consistency.
