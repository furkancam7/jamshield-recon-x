"""Mission continuity audit artifact generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import (
    MISSION_AUDIT_SCHEMA_VERSION,
    validate_mission_audit,
)


def write_mission_audit(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    entries: list[dict[str, Any]],
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": MISSION_AUDIT_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "entries": entries,
    }
    validate_mission_audit(payload)

    audit_path = output_path / f"{scenario_id}_mission_audit.json"
    audit_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return audit_path
