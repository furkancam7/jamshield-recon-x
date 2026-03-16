"""Health-monitor artifact serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import (
    FAULT_EVENTS_SCHEMA_VERSION,
    HEALTH_TIMELINE_SCHEMA_VERSION,
    validate_fault_events,
    validate_mission_health_timeline,
)


def write_mission_health_timeline(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    entries: list[dict[str, Any]],
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": HEALTH_TIMELINE_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "entries": entries,
    }
    validate_mission_health_timeline(payload)
    artifact_path = output_path / f"{scenario_id}_mission_health.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path


def write_fault_events(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    events: list[dict[str, Any]],
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": FAULT_EVENTS_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "events": events,
    }
    validate_fault_events(payload)
    artifact_path = output_path / f"{scenario_id}_fault_events.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path
