#!/usr/bin/env python3
"""Generate a single-file JSON demo skeleton from a .mov screen recording."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _probe_duration_seconds(video_path: Path) -> float | None:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nw=1:nk=1",
        str(video_path),
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
        return float(out)
    except Exception:
        return None


def _default_manifest(video_file: Path, duration_seconds: float | None) -> dict:
    stem = video_file.stem
    duration_ms = int(duration_seconds * 1000) if duration_seconds else None
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "demo_id": stem,
        "source_video": {
            "file_name": video_file.name,
            "path": str(video_file),
            "duration_seconds": duration_seconds,
            "duration_ms": duration_ms,
        },
        "assets": {
            "audio_output": f"demo/audio/{stem}.mp3",
            "review_output": f"demo/video/review/{stem}_synced_with_voice.mp4",
            "subtitle_output": f"demo/video/{stem}/{stem}.srt",
        },
        "narrative_lines": [
            {
                "line_id": "L01",
                "start_ms": 0,
                "end_ms": 5000,
                "text": "Introduction line.",
                "notes": "Replace with final narration text. Keep this as source of truth.",
            },
            {
                "line_id": "L02",
                "start_ms": 5000,
                "end_ms": 15000,
                "text": "Command typing and execution line.",
                "notes": "",
            },
        ],
        "scenes": [
            {
                "scene_id": "S01",
                "start_ms": 0,
                "end_ms": 5000,
                "visual": "Introduction",
                "overlay": "Demo title",
                "line_refs": ["L01"],
            },
            {
                "scene_id": "S02",
                "start_ms": 5000,
                "end_ms": 15000,
                "visual": "Command typing",
                "overlay": "Command",
                "line_refs": ["L02"],
            },
        ],
        "tts": {
            "voice": "cedar",
            "response_format": "mp3",
            "instructions": "Voice Affect: Warm and composed. Tone: Professional and clear. Pacing: Steady.",
        },
        "sync": {
            "default_audio_offset_ms": 0,
            "keep_full_video_length": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a single JSON demo skeleton from a .mov file.",
    )
    parser.add_argument("video_file", help="Path to source .mov file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing JSON manifest")
    parser.add_argument("--dry-run", action="store_true", help="Print planned output path only")
    args = parser.parse_args()

    video_file = Path(args.video_file).expanduser().resolve()
    if not video_file.exists():
        raise SystemExit(f"Input file does not exist: {video_file}")
    if video_file.suffix.lower() != ".mov":
        raise SystemExit(f"Expected a .mov input file, got: {video_file.suffix}")

    target_dir = video_file.parent / video_file.stem
    manifest_path = target_dir / f"{video_file.stem}_demo.json"

    if args.dry_run:
        print(f"Would create folder: {target_dir}")
        print(f"Would create/update: {manifest_path}")
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)
    if manifest_path.exists() and not args.overwrite:
        raise SystemExit(f"Manifest already exists (use --overwrite): {manifest_path}")

    duration = _probe_duration_seconds(video_file)
    manifest = _default_manifest(video_file, duration)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated demo manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
