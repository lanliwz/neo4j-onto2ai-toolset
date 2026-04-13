#!/usr/bin/env python3
"""Shared JSONL logging helpers for harness scripts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = REPO_ROOT / "log"
HARNESS_LOG_PATH = LOG_DIR / "harness_runs.jsonl"


def append_harness_log(script: str, mode: str, status: str, **details: Any) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "script": script,
        "mode": mode,
        "status": status,
        **details,
    }
    with HARNESS_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
