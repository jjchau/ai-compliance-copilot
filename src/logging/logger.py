"""
logger.py

Shared JSONL logging utility for structured audit events.

Purpose:
    Provides reusable append-only JSONL logging helpers
    for AI decision logs and human reviewer audit logs.

Author: Jason Chau
Date: 2026-05-27
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Union, Any

def append_jsonl(
    file_path: Union[str, Path],
    payload: dict[str, Any]
) -> None:
    """
    Appends a structured JSON object to a JSONL file.

    Automatically injects timestamp if missing.
    Creates parent directories if needed.
    """

    Path(file_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if "timestamp" not in payload:
        payload["timestamp"] = datetime.now().isoformat()

    with open(
        file_path,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(payload) + "\n"
        )