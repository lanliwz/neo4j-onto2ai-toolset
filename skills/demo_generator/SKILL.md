---
name: "Demo Generator"
description: "Generate a per-recording single JSON demo manifest from a .mov file using demo/demo_generator.py."
---
# Demo Generator Instructions

Use this skill when the user wants to bootstrap demo production files from a screen recording.

## Tool
- Script: `demo/demo_generator.py`
- Input: one `.mov` file path
- Output: a sibling folder named after the movie stem, with one editable JSON manifest

## Generated File
For input `path/to/demo01.mov`, output folder is `path/to/demo01/` with:
- `demo01_demo.json`
  Purpose: single source of truth for script text, timing, scenes, and TTS config.
  When to use: all demo authoring, timing, and sync workflows.

## Commands
Dry run (no writes):
```bash
python demo/demo_generator.py path/to/demo01.mov --dry-run
```

Generate skeleton:
```bash
python demo/demo_generator.py path/to/demo01.mov
```

Overwrite existing skeleton files:
```bash
python demo/demo_generator.py path/to/demo01.mov --overwrite
```

## Rules
- Input must be `.mov`.
- Keep generated JSON as the only canonical per-demo content file.
- Prefer `--dry-run` first when working in existing demo folders.
- `narrative_lines[].text` is authoritative narration content.
- `narrative_lines[].start_ms` / `end_ms` are authoritative timing values.
