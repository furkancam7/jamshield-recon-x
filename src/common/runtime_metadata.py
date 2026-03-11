"""Runtime metadata helpers for deterministic artifacts."""

from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone


def resolve_software_revision() -> str:
    env_revision = os.environ.get("SOFTWARE_REVISION")
    if env_revision:
        return env_revision.strip()

    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"

    return completed.stdout.strip() or "unknown"


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
