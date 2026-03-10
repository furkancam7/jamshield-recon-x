"""Scenario orchestration for the first control-flow slice."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from .manifest_loader import Position3D, ScenarioManifest


@dataclass(frozen=True)
class GnssConditionSnapshot:
    scenario_id: str
    map_name: str
    run_seed: int
    gnss_condition: str
    route_length_m: float
    measurement_quality: float
    outage_ratio: float


class ScenarioOrchestrator:
    """Interprets a scenario manifest into a simplified GNSS condition snapshot."""

    def __init__(self, manifest: ScenarioManifest) -> None:
        self._manifest = manifest

    def build_snapshot(self) -> GnssConditionSnapshot:
        measurement_quality, outage_ratio = _condition_profile(
            self._manifest.gnss_condition
        )
        route_length_m = _compute_route_length(
            self._manifest.vehicle_spawn, self._manifest.route_waypoints
        )

        return GnssConditionSnapshot(
            scenario_id=self._manifest.scenario_id,
            map_name=self._manifest.map_name,
            run_seed=self._manifest.run_seed,
            gnss_condition=self._manifest.gnss_condition,
            route_length_m=route_length_m,
            measurement_quality=measurement_quality,
            outage_ratio=outage_ratio,
        )


def _condition_profile(gnss_condition: str) -> tuple[float, float]:
    profiles = {
        "nominal": (0.95, 0.00),
        "degraded": (0.55, 0.25),
        "denied": (0.05, 0.95),
    }
    return profiles[gnss_condition]


def _compute_route_length(spawn: Position3D, waypoints: list[Position3D]) -> float:
    total = 0.0
    previous = spawn

    for waypoint in waypoints:
        total += _distance(previous, waypoint)
        previous = waypoint

    return round(total, 3)


def _distance(a: Position3D, b: Position3D) -> float:
    dx = b.x - a.x
    dy = b.y - a.y
    dz = b.z - a.z
    return sqrt(dx * dx + dy * dy + dz * dz)

