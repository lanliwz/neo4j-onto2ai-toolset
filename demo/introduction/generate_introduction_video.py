#!/usr/bin/env python3
"""Generate the standard Onto2AI introduction demo video.

Standard flow:
1. Build the per-demo manifest from the introduction storyline.
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
SCRIPT_PATH = ROOT / "demo" / "introduction" / "introduction-script.md"
DECK_BUILDER = ROOT / "demo" / "introduction" / "render_introduction_template_deck.mjs"
REFERENCE_IMAGE = ROOT / "demo" / "introduction" / "assets" / "onto2ai-qa-frontpage-4.png"
VIDEO_DIR = ROOT / "demo" / "video" / "introduction"
REVIEW_DIR = ROOT / "demo" / "video" / "review"
MANIFEST_PATH = VIDEO_DIR / "introduction_demo.json"
NARRATION_TEXT_PATH = VIDEO_DIR / "introduction_narration.txt"
AUDIO_PATH = ROOT / "demo" / "audio" / "onto2ai_introduction_cedar.mp3"
DECK_PATH = ROOT / "demo" / "introduction" / "onto2ai-introduction-template-video-deck.pptx"
REVIEW_PATH = REVIEW_DIR / "onto2ai_introduction_template.mp4"

ARTIFACT_SKILL_DIR = Path(
    "/Users/weizhang/.codex/plugins/cache/openai-primary-runtime/"
    "presentations/26.623.12021/skills/presentations"
)
ARTIFACT_SETUP = ARTIFACT_SKILL_DIR / "container_tools" / "setup_artifact_tool_workspace.mjs"
TTS_SCRIPT = Path("/Users/weizhang/.codex/skills/speech/scripts/text_to_speech.py")

WIDTH = 1280
HEIGHT = 720
FPS = 30
TTS_MODEL = "gpt-4o-mini-tts-2025-12-15"
TTS_VOICE = "cedar"


SLIDES = [
    {
        "title": "Onto2AI Toolset",
        "subtitle": "From industry ontology to application-ready domain models",
        "bullets": [
            "Start from trusted standards, not a blank page.",
            "Extract the domain subset that matters.",
            "Turn ontology meaning into deployable model artifacts.",
        ],
        "narration": (
            "Onto2AI Toolset helps data and AI teams move from trusted industry "
            "ontology to application-ready domain models."
        ),
    },
    {
        "title": "The Challenge",
        "bullets": [
            "Ontology, databases, code models, and prompts often drift apart.",
            "Every project repeats local decisions about names and relationships.",
            "Large industry ontologies are valuable, but too broad for direct delivery.",
        ],
        "narration": (
            "The challenge is drift. Ontology files, database schemas, code models, "
            "and AI prompts often carry different versions of the same business meaning."
        ),
    },
    {
        "title": "The Goal",
        "bullets": [
            "Neo4j is the workbench technology, not the destination.",
            "Pydantic is one supported output, not the only target.",
            "The goal is aligned, implementation-ready application code models.",
        ],
        "narration": (
            "The goal is not Neo4j, and it is not Pydantic alone. The goal is "
            "alignment between semantic source and application delivery."
        ),
    },
    {
        "title": "Start From Standards",
        "bullets": [
            "Load a source ontology such as FIBO or an enterprise standard.",
            "Inspect classes, properties, restrictions, definitions, and imports.",
            "Use the source ontology as the semantic landscape.",
        ],
        "narration": (
            "Instead of beginning from scratch, teams can load a source ontology, "
            "inspect the semantic landscape, and find the concepts that matter."
        ),
    },
    {
        "title": "Select The Subset",
        "bullets": [
            "Search for concepts like account, parcel, entitlement, or policy.",
            "Preview neighborhoods and relationship context.",
            "Collect extraction seeds for the focused business slice.",
        ],
        "narration": (
            "Onto2AI Modeller and the shared MCP tools help users search, preview, "
            "and select the focused subset needed for a business problem."
        ),
    },
    {
        "title": "Create The Target Ontology",
        "bullets": [
            "Curate the extracted subset into an enterprise target ontology.",
            "Consolidate duplicate concepts and preserve source provenance.",
            "Add application-specific concepts only where needed.",
        ],
        "narration": (
            "The target ontology is curated. Teams consolidate duplicate concepts, "
            "align to standards, and add local concepts only where they are truly needed."
        ),
    },
    {
        "title": "Prototype Artifacts",
        "bullets": [
            "Generate constraints, query context, code models, and documentation.",
            "Validate whether ontology meaning supports real implementation workflows.",
            "Keep tests and artifacts tied to the same semantic foundation.",
        ],
        "narration": (
            "Onto2AI then prototypes implementation artifacts, so the ontology can be "
            "tested as a working contract, not only as an RDF file."
        ),
    },
    {
        "title": "Package And Publish",
        "bullets": [
            "Package domain models independently from the toolset.",
            "Include finalized RDF, generated models, constraints, and smoke tests.",
            "Publish the domain package as an enterprise standard.",
        ],
        "narration": (
            "Finalized domains can be packaged independently, letting application teams "
            "consume a governed model without copying the whole toolset."
        ),
    },
    {
        "title": "Where Modeller Fits",
        "bullets": [
            "Source Ontology: inspect standards and enterprise source models.",
            "Target Ontology: review and tune the working domain model.",
            "Semantic Interaction and Native Query: ask, inspect, and troubleshoot.",
        ],
        "narration": (
            "Onto2AI Modeller makes the workflow visible through Source Ontology, "
            "Target Ontology, Semantic Interaction, and Native Query."
        ),
    },
    {
        "title": "Why It Matters For AI",
        "bullets": [
            "AI needs governed semantic context, not loose prompt fragments.",
            "MCP tools expose ontology search, schema extraction, and validation.",
            "Data, AI, ontology, and application teams work from one foundation.",
        ],
        "narration": (
            "For AI workflows, Onto2AI provides governed semantic context. Agents and "
            "applications can work from structured meaning instead of loose prompt text."
        ),
    },
    {
        "title": "Onto2AI Toolset",
        "subtitle": "Ontology-driven architecture made practical",
        "bullets": [
            "Start with an industry ontology.",
            "Extract, review, prototype, validate, and package.",
            "Publish application-ready domain ontology as an enterprise standard.",
        ],
        "narration": (
            "That is the purpose of Onto2AI Toolset: to make ontology-driven "
            "architecture practical for data, AI, and application delivery."
        ),
    },
]


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def output_text(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def ensure_inputs() -> None:
    missing = [path for path in [SCRIPT_PATH, DECK_BUILDER, REFERENCE_IMAGE] if not path.exists()]
    if missing:
        raise SystemExit("Missing required input(s):\n" + "\n".join(str(path) for path in missing))


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


def build_manifest(duration: float) -> None:
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    duration_per_slide_ms = int(duration * 1000 / len(SLIDES))
    start_ms = 0
    narrative_lines = []
    for index, slide in enumerate(SLIDES, start=1):
        narrative_lines.append(
            {
                "id": f"intro_{index:02d}",
                "start_ms": start_ms,
                "end_ms": start_ms + duration_per_slide_ms,
                "title": slide["title"],
                "text": slide["narration"],
            }
        )
        start_ms += duration_per_slide_ms

    manifest = {
        "demo": "onto2ai_introduction",
        "source_script": str(SCRIPT_PATH.relative_to(ROOT)),
        "presentation_template": "demo/introduction/onto2ai-linkedin-presentation-template.pptx",
        "rendered_deck": str(DECK_PATH.relative_to(ROOT)),
        "output_video": str(REVIEW_PATH.relative_to(ROOT)),
        "output_audio": str(AUDIO_PATH.relative_to(ROOT)),
        "resolution": f"{WIDTH}x{HEIGHT}",
        "fps": FPS,
        "narrative_lines": narrative_lines,
        "slides": [
            {
                "id": f"intro_{index:02d}",
                "title": slide["title"],
                "subtitle": slide.get("subtitle"),
                "bullets": slide["bullets"],
            }
            for index, slide in enumerate(SLIDES, start=1)
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    NARRATION_TEXT_PATH.write_text(
        "\n\n".join(str(slide["narration"]) for slide in SLIDES) + "\n",
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


def setup_artifact_workspace(workspace: Path) -> None:
    if not ARTIFACT_SETUP.exists():
        raise SystemExit(f"Missing artifact-tool setup script: {ARTIFACT_SETUP}")
    workspace.mkdir(parents=True, exist_ok=True)
    run(["node", str(ARTIFACT_SETUP), "--workspace", str(workspace)])
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_inputs()
    build_manifest(duration=92.4)
    generate_audio(refresh=args.refresh_audio)
    duration = audio_duration_seconds()
    build_manifest(duration=duration)

    work_root = Path(tempfile.gettempdir()) / "onto2ai-demo-generation" / "introduction"
    if work_root.exists() and not args.keep_work:
        shutil.rmtree(work_root)
    artifact_workspace = work_root / "artifact-tool"
    frames_dir = work_root / "frames"
    segments_dir = work_root / "segments"
    silent_video = work_root / "onto2ai_introduction_template_silent.mp4"

    setup_artifact_workspace(artifact_workspace)
    render_deck_and_frames(artifact_workspace, frames_dir)
    build_silent_video(frames_dir, segments_dir, silent_video, duration)
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
