"""Scenario manifest loading, canonicalization, and validation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from common.config import load_yaml_file

VALID_GNSS_CONDITIONS = {"nominal", "degraded", "denied"}
VALID_VIO_STATES = {"good", "weak", "lost"}


@dataclass(frozen=True)
class Position3D:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class MissionTimelineStep:
    repeats: int
    gnss_condition: str
    runtime_sync_quality: float
    vio_profile_id: str
    vio_reported_state_override: str | None = None
    vio_health_score_override: float | None = None


@dataclass(frozen=True)
class MissionTimeline:
    tick_period_s: float
    steps: tuple[MissionTimelineStep, ...]


@dataclass(frozen=True)
class ScenarioManifest:
    scenario_id: str
    map_name: str
    vehicle_spawn: Position3D
    route_waypoints: list[Position3D]
    gnss_condition: str
    run_seed: int
    evaluation_profile: str
    metadata: dict[str, str]
    runtime_sync_quality: float = 1.0
    vio_profile_id: str = "nominal_v1"
    vio_reported_state_override: str | None = None
    vio_health_score_override: float | None = None
    config_override_path: Path | None = None
    mission_timeline: MissionTimeline | None = None
    source_path: Path | None = None

    def resolved_mission_timeline(self) -> MissionTimeline:
        if self.mission_timeline is not None:
            return self.mission_timeline
        return MissionTimeline(
            tick_period_s=1.0,
            steps=(
                MissionTimelineStep(
                    repeats=1,
                    gnss_condition=self.gnss_condition,
                    runtime_sync_quality=self.runtime_sync_quality,
                    vio_profile_id=self.vio_profile_id,
                    vio_reported_state_override=self.vio_reported_state_override,
                    vio_health_score_override=self.vio_health_score_override,
                ),
            ),
        )


def load_manifest(path: str | Path) -> ScenarioManifest:
    source_path = Path(path)
    payload = load_yaml_file(source_path)
    return _validate_manifest(payload, source_path)


def load_manifest_payload(path: str | Path) -> dict[str, Any]:
    return load_yaml_file(path)


def canonicalize_manifest_payload(payload: dict[str, Any]) -> str:
    normalized = _normalize_manifest_value(deepcopy(payload))
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def serialize_canonical_manifest(path: str | Path) -> str:
    return canonicalize_manifest_payload(load_manifest_payload(path))


def _validate_manifest(payload: dict[str, Any], source_path: Path) -> ScenarioManifest:
    required_fields = {
        "scenario_id",
        "map_name",
        "vehicle_spawn",
        "route_waypoints",
        "gnss_condition",
        "run_seed",
        "evaluation_profile",
        "metadata",
    }
    missing = required_fields.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Scenario manifest missing required fields: {missing_list}")

    scenario_id = str(payload["scenario_id"]).strip()
    map_name = str(payload["map_name"]).strip()
    gnss_condition = str(payload["gnss_condition"]).strip().lower()
    evaluation_profile = str(payload["evaluation_profile"]).strip()

    if not scenario_id:
        raise ValueError(f"Scenario manifest has empty scenario_id: {source_path}")
    if not map_name:
        raise ValueError(f"Scenario manifest has empty map_name: {source_path}")
    if not evaluation_profile:
        raise ValueError(
            f"Scenario manifest has empty evaluation_profile: {source_path}"
        )
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
    runtime_sync_quality = _parse_runtime_health(payload.get("runtime_health"))
    vio_profile_id, vio_reported_state_override, vio_health_score_override = _parse_vio(
        payload
    )
    mission_timeline = _parse_mission_timeline(
        payload.get("mission_timeline"),
        default_gnss_condition=gnss_condition,
        default_sync_quality=runtime_sync_quality,
        default_vio_profile_id=vio_profile_id,
        default_vio_reported_state=vio_reported_state_override,
        default_vio_health_score=vio_health_score_override,
    )
    config_override_path = _parse_config_override_path(
        payload.get("config_override"),
        source_path,
    )

    return ScenarioManifest(
        scenario_id=scenario_id,
        map_name=map_name,
        vehicle_spawn=vehicle_spawn,
        route_waypoints=route_waypoints,
        gnss_condition=gnss_condition,
        run_seed=run_seed,
        evaluation_profile=evaluation_profile,
        metadata=metadata,
        runtime_sync_quality=runtime_sync_quality,
        vio_profile_id=vio_profile_id,
        vio_reported_state_override=vio_reported_state_override,
        vio_health_score_override=vio_health_score_override,
        config_override_path=config_override_path,
        mission_timeline=mission_timeline,
        source_path=source_path,
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


def _parse_config_override_path(value: Any, source_path: Path) -> Path | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError("config_override must be a string path when provided.")

    raw_path = value.strip()
    if not raw_path:
        raise ValueError("config_override must not be empty.")

    override_path = Path(raw_path)
    if not override_path.is_absolute():
        override_path = source_path.parent / override_path

    return override_path


def _parse_runtime_health(value: Any, default_sync_quality: float = 1.0) -> float:
    if value is None:
        return default_sync_quality
    if not isinstance(value, dict):
        raise ValueError("runtime_health must be a mapping when provided.")
    sync_quality = value.get("sync_quality", default_sync_quality)
    try:
        resolved = float(sync_quality)
    except (TypeError, ValueError) as exc:
        raise ValueError("runtime_health.sync_quality must be numeric.") from exc
    if not (0.0 <= resolved <= 1.0):
        raise ValueError("runtime_health.sync_quality must be within 0.0-1.0.")
    return resolved


def _parse_vio(
    payload: dict[str, Any],
    *,
    default_profile_id: str = "nominal_v1",
    default_reported_state: str | None = None,
    default_health_score_override: float | None = None,
) -> tuple[str, str | None, float | None]:
    profile_id = default_profile_id
    reported_state = default_reported_state
    health_score_override = default_health_score_override

    vio_payload = payload.get("vio")
    if vio_payload is not None:
        if not isinstance(vio_payload, dict):
            raise ValueError("vio must be a mapping when provided.")
        if "profile_id" in vio_payload:
            profile_id = str(vio_payload["profile_id"]).strip()
            if not profile_id:
                raise ValueError("vio.profile_id must not be empty.")
        if "reported_state" in vio_payload:
            reported_state = str(vio_payload["reported_state"]).strip().lower()
            if reported_state not in VALID_VIO_STATES:
                raise ValueError("vio.reported_state must be one of good, weak, lost.")
        if "health_score_override" in vio_payload:
            health_score_override = float(vio_payload["health_score_override"])

    legacy_state = payload.get("vio_state")
    if legacy_state is not None:
        reported_state = str(legacy_state).strip().lower()
        if reported_state not in VALID_VIO_STATES:
            raise ValueError("vio_state must be one of good, weak, lost.")

    legacy_score = payload.get("vio_health_score")
    if legacy_score is not None:
        health_score_override = float(legacy_score)

    if health_score_override is not None and not (0.0 <= health_score_override <= 1.0):
        raise ValueError("vio health score override must be within 0.0-1.0.")

    return profile_id, reported_state, health_score_override


def _parse_mission_timeline(
    value: Any,
    *,
    default_gnss_condition: str,
    default_sync_quality: float,
    default_vio_profile_id: str,
    default_vio_reported_state: str | None,
    default_vio_health_score: float | None,
) -> MissionTimeline | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("mission_timeline must be a mapping when provided.")

    tick_period_s = value.get("tick_period_s")
    if tick_period_s is None:
        raise ValueError("mission_timeline.tick_period_s is required.")
    try:
        resolved_tick_period_s = float(tick_period_s)
    except (TypeError, ValueError) as exc:
        raise ValueError("mission_timeline.tick_period_s must be numeric.") from exc
    if resolved_tick_period_s <= 0.0:
        raise ValueError("mission_timeline.tick_period_s must be positive.")

    raw_steps = value.get("steps")
    if not isinstance(raw_steps, list) or not raw_steps:
        raise ValueError("mission_timeline.steps must be a non-empty list.")

    steps: list[MissionTimelineStep] = []
    for index, raw_step in enumerate(raw_steps):
        if not isinstance(raw_step, dict):
            raise ValueError(f"mission_timeline.steps[{index}] must be a mapping.")

        repeats = int(raw_step.get("repeats", 1))
        if repeats <= 0:
            raise ValueError(
                f"mission_timeline.steps[{index}].repeats must be a positive integer."
            )

        gnss_condition = str(
            raw_step.get("gnss_condition", default_gnss_condition)
        ).strip().lower()
        if gnss_condition not in VALID_GNSS_CONDITIONS:
            raise ValueError(
                f"mission_timeline.steps[{index}].gnss_condition must be one of: "
                f"{', '.join(sorted(VALID_GNSS_CONDITIONS))}"
            )

        runtime_sync_quality = (
            _parse_runtime_health(
                raw_step.get("runtime_health"),
                default_sync_quality=default_sync_quality,
            )
            if "runtime_health" in raw_step
            else default_sync_quality
        )
        (
            vio_profile_id,
            vio_reported_state_override,
            vio_health_score_override,
        ) = _parse_vio(
            raw_step,
            default_profile_id=default_vio_profile_id,
            default_reported_state=default_vio_reported_state,
            default_health_score_override=default_vio_health_score,
        )

        steps.append(
            MissionTimelineStep(
                repeats=repeats,
                gnss_condition=gnss_condition,
                runtime_sync_quality=runtime_sync_quality,
                vio_profile_id=vio_profile_id,
                vio_reported_state_override=vio_reported_state_override,
                vio_health_score_override=vio_health_score_override,
            )
        )

    return MissionTimeline(
        tick_period_s=resolved_tick_period_s,
        steps=tuple(steps),
    )


def _normalize_manifest_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _normalize_manifest_value(value[key]) for key in sorted(value)}
    if isinstance(value, tuple):
        return [_normalize_manifest_value(item) for item in value]
    if isinstance(value, list):
        return [_normalize_manifest_value(item) for item in value]
    return value
