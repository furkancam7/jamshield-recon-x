"""Artifact helpers for runtime trace and pseudo-truth outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ew_risk_map.service import interpolate_route_position
from evaluation.artifact_schema import (
    RUNTIME_TRACE_SCHEMA_VERSION,
    TRUTH_TRACE_SCHEMA_VERSION,
    validate_runtime_trace,
    validate_truth_trace,
)
from scenario_orchestrator.manifest_loader import Position3D, ScenarioManifest


def write_runtime_trace(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    entries: list[dict[str, Any]],
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": RUNTIME_TRACE_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "entries": entries,
    }
    validate_runtime_trace(payload)
    artifact_path = output_path / f"{scenario_id}_runtime_trace.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path


def write_truth_trace(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    entries: list[dict[str, Any]],
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": TRUTH_TRACE_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "entries": entries,
    }
    validate_truth_trace(payload)
    artifact_path = output_path / f"{scenario_id}_truth_trace.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path


def build_truth_trace_entries(
    manifest: ScenarioManifest,
    *,
    total_ticks: int,
    tick_period_s: float,
) -> list[dict[str, Any]]:
    route_points = [manifest.vehicle_spawn, *manifest.route_waypoints]
    positions = _interpolate_truth_positions(route_points, total_ticks)
    entries: list[dict[str, Any]] = []
    for tick_index, position in enumerate(positions):
        progress_pct = 100.0 if total_ticks <= 1 else round(
            (tick_index / (total_ticks - 1)) * 100.0, 3
        )
        entries.append(
            {
                "tick_index": tick_index,
                "timestamp_ns": int(round(tick_index * tick_period_s * 1_000_000_000)),
                "position_m": {
                    "x": position.x,
                    "y": position.y,
                    "z": position.z,
                },
                "route_progress_pct": progress_pct,
            }
        )
    return entries


def _interpolate_truth_positions(
    route_points: list[Position3D],
    total_ticks: int,
) -> list[Position3D]:
    if total_ticks <= 0:
        return []
    if total_ticks == 1:
        return [route_points[0]]

    z_start = route_points[0].z
    z_end = route_points[-1].z
    positions: list[Position3D] = []
    for tick_index in range(total_ticks):
        x_m, y_m = interpolate_route_position(route_points, tick_index, total_ticks)
        z_ratio = tick_index / (total_ticks - 1)
        z_m = round(z_start + ((z_end - z_start) * z_ratio), 3)
        positions.append(Position3D(x=x_m, y=y_m, z=z_m))
    return positions
