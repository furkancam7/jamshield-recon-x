"""Scenario manifest loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.config import load_yaml_file

VALID_GNSS_CONDITIONS = {"nominal", "degraded", "denied"}


@dataclass(frozen=True)
class Position3D:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class ScenarioManifest:
    scenario_id: str
    map_name: str
    vehicle_spawn: Position3D
    route_waypoints: list[Position3D]
    gnss_condition: str
    run_seed: int
    metadata: dict[str, str]


def load_manifest(path: str | Path) -> ScenarioManifest:
    payload = load_yaml_file(path)
    return _validate_manifest(payload, Path(path))


def _validate_manifest(payload: dict[str, Any], source_path: Path) -> ScenarioManifest:
    required_fields = {
        "scenario_id",
        "map_name",
        "vehicle_spawn",
        "route_waypoints",
        "gnss_condition",
        "run_seed",
        "metadata",
    }
    missing = required_fields.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Scenario manifest missing required fields: {missing_list}")

    scenario_id = str(payload["scenario_id"]).strip()
    map_name = str(payload["map_name"]).strip()
    gnss_condition = str(payload["gnss_condition"]).strip().lower()

    if not scenario_id:
        raise ValueError(f"Scenario manifest has empty scenario_id: {source_path}")
    if not map_name:
        raise ValueError(f"Scenario manifest has empty map_name: {source_path}")
    if gnss_condition not in VALID_GNSS_CONDITIONS:
        allowed = ", ".join(sorted(VALID_GNSS_CONDITIONS))
        raise ValueError(
            f"Scenario manifest has invalid gnss_condition '{gnss_condition}'. "
            f"Expected one of: {allowed}"
        )

    vehicle_spawn = _parse_position(payload["vehicle_spawn"], "vehicle_spawn")
    route_waypoints_raw = payload["route_waypoints"]
    if not isinstance(route_waypoints_raw, list) or not route_waypoints_raw:
        raise ValueError("Scenario manifest requires at least one route waypoint.")

    route_waypoints = [
        _parse_position(waypoint, f"route_waypoints[{index}]")
        for index, waypoint in enumerate(route_waypoints_raw)
    ]

    run_seed = int(payload["run_seed"])
    if run_seed < 0:
        raise ValueError("run_seed must be non-negative.")

    metadata = _parse_metadata(payload["metadata"])

    return ScenarioManifest(
        scenario_id=scenario_id,
        map_name=map_name,
        vehicle_spawn=vehicle_spawn,
        route_waypoints=route_waypoints,
        gnss_condition=gnss_condition,
        run_seed=run_seed,
        metadata=metadata,
    )


def _parse_position(value: Any, field_name: str) -> Position3D:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping with x, y, z fields.")

    missing = {"x", "y", "z"}.difference(value)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"{field_name} missing coordinates: {missing_list}")

    return Position3D(
        x=float(value["x"]),
        y=float(value["y"]),
        z=float(value["z"]),
    )


def _parse_metadata(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError("metadata must be a mapping.")

    required_fields = {"title", "description", "owner"}
    missing = required_fields.difference(value)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"metadata missing required fields: {missing_list}")

    metadata: dict[str, str] = {}
    for field_name in sorted(required_fields):
        field_value = str(value[field_name]).strip()
        if not field_value:
            raise ValueError(f"metadata.{field_name} must not be empty.")
        metadata[field_name] = field_value

    return metadata
