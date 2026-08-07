#!/usr/bin/env python3
"""Generate the standard Onto2AI entitlement demo video.

Standard flow:
1. Load the manifest for the Onto2AI domain-package workflow.
2. Build or reuse OpenAI cedar narration.
3. Render the LinkedIn-style presentation deck and slide frames.
4. Assemble a review MP4 from rendered frames plus narration.

Durable outputs stay under demo/. Intermediate frames and segments are written
to the system temp directory so the repository stays clean.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "demo" / "entitlement" / "entitlement-script.md"
DECK_BUILDER = ROOT / "demo" / "entitlement" / "render_entitlement_template_deck.mjs"
REFERENCE_IMAGE = ROOT / "demo" / "entitlement" / "assets" / "onto2ai-qa-frontpage-4.png"
VIDEO_DIR = ROOT / "demo" / "video" / "entitlement"
REVIEW_DIR = ROOT / "demo" / "video" / "review"
MANIFEST_PATH = VIDEO_DIR / "entitlement_demo.json"
NARRATION_TEXT_PATH = VIDEO_DIR / "entitlement_narration.txt"
AUDIO_PATH = ROOT / "demo" / "audio" / "onto2ai_entitlement_cedar.mp3"
DECK_PATH = ROOT / "demo" / "entitlement" / "onto2ai-entitlement-template-video-deck.pptx"
REVIEW_PATH = REVIEW_DIR / "onto2ai_entitlement_template.mp4"

ARTIFACT_SKILL_DIR = Path(
    os.environ.get(
        "ONTO2AI_PRESENTATION_SKILL_DIR",
        "/Users/weizhang/.codex/plugins/cache/openai-primary-runtime/"
        "presentations/26.623.12021/skills/presentations",
    )
)
ARTIFACT_SETUP = ARTIFACT_SKILL_DIR / "container_tools" / "setup_artifact_tool_workspace.mjs"
TTS_SCRIPT = Path(
    os.environ.get(
        "ONTO2AI_TTS_SCRIPT",
        "/Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py",
    )
)

WIDTH = 1280
HEIGHT = 720
FPS = 30
TTS_MODEL = "gpt-4o-mini-tts-2025-12-15"
TTS_VOICE = "cedar"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def output_text(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def ensure_inputs() -> None:
    missing = [path for path in [SCRIPT_PATH, DECK_BUILDER, REFERENCE_IMAGE] if not path.exists()]
    if missing:
        raise SystemExit("Missing required input(s):\n" + "\n".join(str(path) for path in missing))


def load_source_slides() -> list[dict[str, object]]:
    if not MANIFEST_PATH.exists():
        raise SystemExit(f"Missing canonical demo manifest: {MANIFEST_PATH}")

    source = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    slides = source.get("slides") or []
    narrative_lines = source.get("narrative_lines") or []
    if len(slides) != len(narrative_lines):
        raise SystemExit(
            f"Manifest slide/narration count mismatch: {len(slides)} slides, "
            f"{len(narrative_lines)} narrative lines"
        )

    loaded_slides: list[dict[str, object]] = []
    for slide, narrative in zip(slides, narrative_lines, strict=True):
        narration = str(narrative.get("text") or "").strip()
        bullets = slide.get("bullets") or []
        if not slide.get("title") or not narration or not bullets:
            raise SystemExit("Manifest slides must include title, bullets, and narration text.")
        loaded_slides.append(
            {
                "title": slide["title"],
                "subtitle": slide.get("subtitle"),
                "bullets": bullets,
                "narration": narration,
            }
        )
    return loaded_slides


def weighted_scene_timings(slides: list[dict[str, object]], duration: float) -> list[tuple[int, int]]:
    weights = [max(1, len(str(slide["narration"]).split())) for slide in slides]
    total_weight = sum(weights)
    total_ms = int(round(duration * 1000))
    timings: list[tuple[int, int]] = []
    start_ms = 0
    for index, weight in enumerate(weights, start=1):
        if index == len(weights):
            end_ms = total_ms
        else:
            end_ms = start_ms + int(round(total_ms * weight / total_weight))
        timings.append((start_ms, end_ms))
        start_ms = end_ms
    return timings


def audio_duration_seconds() -> float:
    return float(
        output_text(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(AUDIO_PATH),
            ]
        )
    )


def build_manifest(slides: list[dict[str, object]], duration: float, *, silent: bool = False) -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    narrative_lines = []
    for index, (slide, timing) in enumerate(zip(slides, weighted_scene_timings(slides, duration), strict=True), start=1):
        start_ms, end_ms = timing
        narrative_lines.append(
            {
                "id": f"entitlement_{index:02d}",
                "start_ms": start_ms,
                "end_ms": end_ms,
                "title": slide["title"],
                "text": slide["narration"],
            }
        )

    manifest = {
        "demo": "onto2ai_domain_package_workflow",
        "worked_example": "entitlement",
        "final_package": "onto2ai-entitlement",
        "source_script": str(SCRIPT_PATH.relative_to(ROOT)),
        "presentation_template": "demo/entitlement/onto2ai-linkedin-presentation-template.pptx",
        "rendered_deck": str(DECK_PATH.relative_to(ROOT)),
        "output_video": str(REVIEW_PATH.relative_to(ROOT)),
        "output_audio": None if silent else str(AUDIO_PATH.relative_to(ROOT)),
        "silent": silent,
        "resolution": f"{WIDTH}x{HEIGHT}",
        "fps": FPS,
        "narrative_lines": narrative_lines,
        "slides": [
            {
                "id": f"entitlement_{index:02d}",
                "title": slide["title"],
                "subtitle": slide.get("subtitle"),
                "bullets": slide["bullets"],
            }
            for index, slide in enumerate(slides, start=1)
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    NARRATION_TEXT_PATH.write_text(
        "\n\n".join(str(slide["narration"]) for slide in slides) + "\n",
        encoding="utf-8",
    )


def generate_audio(refresh: bool) -> None:
    if AUDIO_PATH.exists() and not refresh:
        return
    if not TTS_SCRIPT.exists():
        raise SystemExit(f"Missing speech CLI: {TTS_SCRIPT}")
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required to refresh OpenAI cedar narration.")
    AUDIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "uv",
            "run",
            "--with",
            "openai",
            "python",
            str(TTS_SCRIPT),
            "speak",
            "--model",
            TTS_MODEL,
            "--input-file",
            str(NARRATION_TEXT_PATH),
            "--voice",
            TTS_VOICE,
            "--response-format",
            "mp3",
            "--instructions",
            (
                "Voice Affect: Warm and composed. Tone: Professional, clear, and confident. "
                "Pacing: Steady and moderate. Delivery: Natural product-demo narration with "
                "short pauses between ideas. Pronunciation: Enunciate Onto2AI as Onto two A I, "
                "and MCP as M C P."
            ),
            "--out",
            str(AUDIO_PATH),
            "--force",
        ]
    )


def resolve_artifact_setup() -> Path:
    if ARTIFACT_SETUP.exists():
        return ARTIFACT_SETUP

    candidates = sorted(
        Path("/Users/weizhang/.codex/plugins/cache/openai-primary-runtime").glob(
            "presentations/*/skills/presentations/container_tools/setup_artifact_tool_workspace.mjs"
        ),
        reverse=True,
    )
    if candidates:
        return candidates[0]
    return ARTIFACT_SETUP


def setup_artifact_workspace(workspace: Path) -> None:
    artifact_setup = resolve_artifact_setup()
    if not artifact_setup.exists():
        raise SystemExit(
            "Missing artifact-tool setup script. Set ONTO2AI_PRESENTATION_SKILL_DIR "
            f"or install the presentations skill. Tried: {ARTIFACT_SETUP}"
        )
    workspace.mkdir(parents=True, exist_ok=True)
    run(["node", str(artifact_setup), "--workspace", str(workspace)])
    shutil.copyfile(DECK_BUILDER, workspace / DECK_BUILDER.name)


def render_deck_and_frames(workspace: Path, frames_dir: Path) -> None:
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "ONTO2AI_REPO_ROOT": str(ROOT),
            "ONTO2AI_DEMO_MANIFEST": str(MANIFEST_PATH),
            "ONTO2AI_REFERENCE_IMAGE": str(REFERENCE_IMAGE),
            "ONTO2AI_RENDERED_DECK": str(DECK_PATH),
            "ONTO2AI_FRAME_DIR": str(frames_dir),
            "ONTO2AI_PREVIEW_DIR": str(workspace / "preview"),
        }
    )
    run(["node", str(workspace / DECK_BUILDER.name)], cwd=workspace, env=env)
    sidecar = DECK_PATH.with_suffix(DECK_PATH.suffix + ".inspect.ndjson")
    if sidecar.exists():
        sidecar.unlink()


def build_silent_video(frames_dir: Path, segments_dir: Path, silent_video: Path, duration: float) -> None:
    if segments_dir.exists():
        shutil.rmtree(segments_dir)
    segments_dir.mkdir(parents=True, exist_ok=True)
    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        raise SystemExit(f"No rendered frames found in {frames_dir}")
    duration_per_slide = duration / len(frames)
    segment_paths = []
    for index, frame in enumerate(frames, start=1):
        segment = segments_dir / f"segment-{index:02d}.mp4"
        run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-loop",
                "1",
                "-i",
                str(frame),
                "-t",
                f"{duration_per_slide:.3f}",
                "-vf",
                f"fps={FPS},format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                str(segment),
            ]
        )
        segment_paths.append(segment)

    concat_file = segments_dir / "segments.txt"
    concat_file.write_text("".join(f"file {segment}\n" for segment in segment_paths), encoding="utf-8")
    run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(silent_video),
        ]
    )


def mux_audio(silent_video: Path) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(silent_video),
            "-i",
            str(AUDIO_PATH),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(REVIEW_PATH),
        ]
    )


def write_silent_review_video(silent_video: Path) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(silent_video, REVIEW_PATH)


def verify_video() -> dict[str, object]:
    raw = output_text(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,duration,bit_rate",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(REVIEW_PATH),
        ]
    )
    return json.loads(raw)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh-audio",
        action="store_true",
        help="Regenerate OpenAI cedar narration instead of reusing the existing MP3.",
    )
    parser.add_argument(
        "--keep-work",
        action="store_true",
        help="Keep scratch render frames and segments for debugging.",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Render a silent review video without generating or muxing narration audio.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_inputs()
    slides = load_source_slides()
    build_manifest(slides, duration=92.4, silent=args.silent)
    if args.silent:
        duration = 92.4
    else:
        generate_audio(refresh=args.refresh_audio)
        duration = audio_duration_seconds()
        build_manifest(slides, duration=duration)

    work_root = Path(tempfile.gettempdir()) / "onto2ai-demo-generation" / "entitlement"
    if work_root.exists() and not args.keep_work:
        shutil.rmtree(work_root)
    artifact_workspace = work_root / "artifact-tool"
    frames_dir = work_root / "frames"
    segments_dir = work_root / "segments"
    silent_video = work_root / "onto2ai_entitlement_template_silent.mp4"

    setup_artifact_workspace(artifact_workspace)
    render_deck_and_frames(artifact_workspace, frames_dir)
    build_silent_video(frames_dir, segments_dir, silent_video, duration)
    if args.silent:
        write_silent_review_video(silent_video)
    else:
        mux_audio(silent_video)
    probe = verify_video()

    if not args.keep_work and work_root.exists():
        shutil.rmtree(work_root)

    print(f"Wrote {REVIEW_PATH}")
    print(f"Wrote {DECK_PATH}")
    print(f"Wrote {MANIFEST_PATH}")
    print(json.dumps(probe, indent=2))


if __name__ == "__main__":
    main()
