#!/usr/bin/env python3
"""Generate the Onto2AI custodian wealth-management demo video."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_GENERATOR_PATH = ROOT / "demo" / "entitlement" / "generate_entitlement_video.py"


def load_base_generator():
    spec = importlib.util.spec_from_file_location("onto2ai_demo_generator", BASE_GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Unable to load demo generator: {BASE_GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = load_base_generator()
base.SCRIPT_PATH = ROOT / "demo" / "custodian_wealth" / "custodian-wealth-script.md"
base.DECK_BUILDER = ROOT / "demo" / "custodian_wealth" / "render_custodian_wealth_deck.mjs"
base.REFERENCE_IMAGE = ROOT / "demo" / "introduction" / "assets" / "onto2ai-qa-frontpage-4.png"
base.VIDEO_DIR = ROOT / "demo" / "video" / "custodian_wealth"
base.REVIEW_DIR = ROOT / "demo" / "video" / "review"
base.MANIFEST_PATH = base.VIDEO_DIR / "custodian_wealth_demo.json"
base.NARRATION_TEXT_PATH = base.VIDEO_DIR / "custodian_wealth_narration.txt"
base.AUDIO_PATH = ROOT / "demo" / "audio" / "onto2ai_custodian_wealth_cedar.mp3"
base.DECK_PATH = ROOT / "demo" / "custodian_wealth" / "onto2ai-custodian-wealth-video-deck.pptx"
base.REVIEW_PATH = base.REVIEW_DIR / "onto2ai_custodian_wealth.mp4"


def build_manifest(slides: list[dict[str, object]], duration: float, *, silent: bool = False) -> None:
    base.VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    narrative_lines = []
    timings = base.weighted_scene_timings(slides, duration)
    for index, (slide, timing) in enumerate(zip(slides, timings, strict=True), start=1):
        start_ms, end_ms = timing
        narrative_lines.append(
            {
                "id": f"custodian_wealth_{index:02d}",
                "start_ms": start_ms,
                "end_ms": end_ms,
                "title": slide["title"],
                "text": slide["narration"],
            }
        )

    manifest = {
        "demo": "onto2ai_custodian_wealth_workflow",
        "worked_example": "fictional global custodian bank",
        "institution": "Northstar Custody Bank",
        "final_package": "northstar-client-ontology",
        "source_script": str(base.SCRIPT_PATH.relative_to(ROOT)),
        "presentation_template": "demo/introduction/onto2ai-linkedin-presentation-template.pptx",
        "rendered_deck": str(base.DECK_PATH.relative_to(ROOT)),
        "output_video": str(base.REVIEW_PATH.relative_to(ROOT)),
        "output_audio": None if silent else str(base.AUDIO_PATH.relative_to(ROOT)),
        "silent": silent,
        "resolution": f"{base.WIDTH}x{base.HEIGHT}",
        "fps": base.FPS,
        "narrative_lines": narrative_lines,
        "slides": [
            {
                "id": f"custodian_wealth_{index:02d}",
                "title": slide["title"],
                "subtitle": slide.get("subtitle"),
                "bullets": slide["bullets"],
            }
            for index, slide in enumerate(slides, start=1)
        ],
    }
    base.MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    base.NARRATION_TEXT_PATH.write_text(
        "\n\n".join(str(slide["narration"]) for slide in slides) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = base.parse_args()
    base.ensure_inputs()
    slides = base.load_source_slides()
    build_manifest(slides, duration=120.0, silent=args.silent)
    if args.silent:
        duration = 120.0
    else:
        base.generate_audio(refresh=args.refresh_audio)
        duration = base.audio_duration_seconds()
        build_manifest(slides, duration=duration)

    work_root = Path(tempfile.gettempdir()) / "onto2ai-demo-generation" / "custodian_wealth"
    if work_root.exists() and not args.keep_work:
        shutil.rmtree(work_root)
    artifact_workspace = work_root / "artifact-tool"
    frames_dir = work_root / "frames"
    segments_dir = work_root / "segments"
    silent_video = work_root / "onto2ai_custodian_wealth_silent.mp4"

    base.setup_artifact_workspace(artifact_workspace)
    base.render_deck_and_frames(artifact_workspace, frames_dir)
    base.build_silent_video(frames_dir, segments_dir, silent_video, duration)
    if args.silent:
        base.write_silent_review_video(silent_video)
    else:
        base.mux_audio(silent_video)
    probe = base.verify_video()

    if not args.keep_work and work_root.exists():
        shutil.rmtree(work_root)

    print(f"Wrote {base.REVIEW_PATH}")
    print(f"Wrote {base.DECK_PATH}")
    print(f"Wrote {base.MANIFEST_PATH}")
    print(json.dumps(probe, indent=2))


if __name__ == "__main__":
    main()
