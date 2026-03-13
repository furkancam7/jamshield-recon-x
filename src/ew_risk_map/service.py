"""Deterministic EW risk-map generation for the tactical slice."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import ceil, hypot

from common.config import EwRiskMapConfig
from scenario_orchestrator.manifest_loader import Position3D, ScenarioManifest


_PRIMARY_REASON_PRIORITY = (
    "ew_gnss_denial_hotspot",
    "ew_sync_instability_corridor",
    "ew_localization_instability",
    "ew_gnss_degraded_corridor",
)
_PRIMARY_REASON_EVIDENCE = {
    "ew_gnss_denial_hotspot": "gnss_denial_suspected",
    "ew_sync_instability_corridor": "sync_quality_low",
    "ew_localization_instability": "localization_confidence_low",
    "ew_gnss_degraded_corridor": "gnss_measurement_quality_low",
}


@dataclass(frozen=True)
class EwGridOrigin:
    x_m: float
    y_m: float


@dataclass(frozen=True)
class EwRiskTickInput:
    tick_index: int
    gnss_state: str
    sync_quality: float
    localization_mode: str
    localization_confidence: float
    trust_primary_reason_code: str
    trust_reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class EwRiskMapAssessment:
    timestamp_ns: int
    frame_id: str
    cell_size_m: float
    width_cells: int
    height_cells: int
    origin: EwGridOrigin
    risk_cells: tuple[float, ...]
    evidence_codes: tuple[str, ...]
    primary_reason_code: str
    reason_codes: tuple[str, ...]
    max_risk: float
    affected_cell_count: int
    corridor_cost: float
    risk_level: str
    risk_cells_hash: str


class EwRiskMapService:
    """Builds a tactical risk grid from deterministic runtime evidence."""

    def __init__(self, config: EwRiskMapConfig) -> None:
        self._config = config

    def evaluate(
        self,
        *,
        manifest: ScenarioManifest,
        tick_period_s: float,
        tick_inputs: list[EwRiskTickInput],
    ) -> EwRiskMapAssessment:
        route_points = [manifest.vehicle_spawn, *manifest.route_waypoints]
        origin, width_cells, height_cells = build_grid_bounds(route_points, self._config)
        if not tick_inputs:
            raise ValueError("EW risk map requires at least one tick input.")

        grid = [0.0] * (width_cells * height_cells)
        contributions = {reason: 0.0 for reason in _PRIMARY_REASON_PRIORITY}
        evidence_codes: list[str] = []
        total_ticks = len(tick_inputs)

        for tick in tick_inputs:
            _apply_global_decay(grid, self._config.global_decay_per_tick)
            position = interpolate_route_position(
                route_points,
                tick.tick_index,
                total_ticks,
            )
            stamp_weight, tick_evidence, tick_reasons = _resolve_tick_evidence(
                tick,
                self._config,
            )
            for evidence in tick_evidence:
                if evidence not in evidence_codes:
                    evidence_codes.append(evidence)
            for reason_code, weight in tick_reasons.items():
                contributions[reason_code] += weight
            if stamp_weight > 0.0:
                _apply_stamp(
                    grid,
                    position,
                    origin,
                    width_cells,
                    height_cells,
                    self._config.cell_size_m,
                    self._config.stamp_radius_m,
                    stamp_weight,
                )

        rounded_cells = tuple(round(value, 3) for value in grid)
        max_risk = round(max(rounded_cells), 3)
        affected_cell_count = sum(
            1 for value in rounded_cells if value >= self._config.risk_low_floor
        )
        corridor_cost = compute_corridor_cost(
            route_points,
            origin,
            width_cells,
            height_cells,
            self._config,
            rounded_cells,
        )
        primary_reason_code, reason_codes = _resolve_primary_reason(contributions)
        risk_level = _risk_level(
            max_risk=max_risk,
            affected_cell_count=affected_cell_count,
            config=self._config,
        )
        risk_cells_hash = _hash_risk_cells(rounded_cells)
        timestamp_ns = int(round((total_ticks - 1) * tick_period_s * 1_000_000_000))

        return EwRiskMapAssessment(
            timestamp_ns=timestamp_ns,
            frame_id="map",
            cell_size_m=self._config.cell_size_m,
            width_cells=width_cells,
            height_cells=height_cells,
            origin=origin,
            risk_cells=rounded_cells,
            evidence_codes=tuple(evidence_codes),
            primary_reason_code=primary_reason_code,
            reason_codes=reason_codes,
            max_risk=max_risk,
            affected_cell_count=affected_cell_count,
            corridor_cost=corridor_cost,
            risk_level=risk_level,
            risk_cells_hash=risk_cells_hash,
        )


def build_grid_bounds(
    route_points: list[Position3D],
    config: EwRiskMapConfig,
) -> tuple[EwGridOrigin, int, int]:
    xs = [point.x for point in route_points]
    ys = [point.y for point in route_points]
    min_x = min(xs) - config.grid_padding_m
    max_x = max(xs) + config.grid_padding_m
    min_y = min(ys) - config.grid_padding_m
    max_y = max(ys) + config.grid_padding_m

    width_span = max(config.cell_size_m, max_x - min_x)
    height_span = max(config.cell_size_m, max_y - min_y)
    width_cells = int(ceil(width_span / config.cell_size_m)) + 1
    height_cells = int(ceil(height_span / config.cell_size_m)) + 1

    return EwGridOrigin(x_m=round(min_x, 3), y_m=round(min_y, 3)), width_cells, height_cells


def interpolate_route_position(
    route_points: list[Position3D],
    tick_index: int,
    total_ticks: int,
) -> tuple[float, float]:
    if total_ticks <= 1:
        return route_points[0].x, route_points[0].y

    segment_lengths = [
        _distance_xy(route_points[index], route_points[index + 1])
        for index in range(len(route_points) - 1)
    ]
    total_length = sum(segment_lengths)
    if total_length <= 0.0:
        return route_points[0].x, route_points[0].y

    progress = tick_index / (total_ticks - 1)
    target_distance = total_length * progress
    traversed = 0.0
    for index, segment_length in enumerate(segment_lengths):
        if traversed + segment_length >= target_distance:
            start = route_points[index]
            end = route_points[index + 1]
            if segment_length <= 0.0:
                return start.x, start.y
            ratio = (target_distance - traversed) / segment_length
            return (
                round(start.x + ((end.x - start.x) * ratio), 3),
                round(start.y + ((end.y - start.y) * ratio), 3),
            )
        traversed += segment_length
    end_point = route_points[-1]
    return end_point.x, end_point.y


def compute_corridor_cost(
    route_points: list[Position3D],
    origin: EwGridOrigin,
    width_cells: int,
    height_cells: int,
    config: EwRiskMapConfig,
    risk_cells: tuple[float, ...],
) -> float:
    segment_lengths = [
        _distance_xy(route_points[index], route_points[index + 1])
        for index in range(len(route_points) - 1)
    ]
    total_length = sum(segment_lengths)
    if total_length <= 0.0:
        return 0.0

    sample_count = max(2, int(ceil(total_length / config.corridor_sample_step_m)) + 1)
    sample_costs: list[float] = []
    for sample_index in range(sample_count):
        progress = sample_index / (sample_count - 1)
        sample_position = interpolate_route_position(route_points, sample_index, sample_count)
        sample_costs.append(
            _sample_band_cost(
                risk_cells=risk_cells,
                sample_position=sample_position,
                origin=origin,
                width_cells=width_cells,
                height_cells=height_cells,
                cell_size_m=config.cell_size_m,
                band_half_width_m=config.corridor_band_half_width_m,
            )
        )
    return round(sum(sample_costs) / len(sample_costs), 3)


def _resolve_tick_evidence(
    tick: EwRiskTickInput,
    config: EwRiskMapConfig,
) -> tuple[float, tuple[str, ...], dict[str, float]]:
    evidence_codes: list[str] = []
    contributions = {reason: 0.0 for reason in _PRIMARY_REASON_PRIORITY}
    total_weight = 0.0
    trust_codes = {tick.trust_primary_reason_code, *tick.trust_reason_codes}

    if tick.gnss_state == "denied" or "gnss_denial_suspected" in trust_codes:
        evidence_codes.append("gnss_denial_suspected")
        contributions["ew_gnss_denial_hotspot"] += config.weight_gnss_denied
        total_weight += config.weight_gnss_denied
    elif tick.gnss_state == "degraded":
        evidence_codes.append("gnss_measurement_quality_low")
        contributions["ew_gnss_degraded_corridor"] += config.weight_gnss_degraded
        total_weight += config.weight_gnss_degraded

    if "sync_quality_low" in trust_codes:
        evidence_codes.append("sync_quality_low")
        contributions["ew_sync_instability_corridor"] += config.weight_sync_low
        total_weight += config.weight_sync_low

    if (
        "localization_confidence_low" in trust_codes
        or tick.localization_mode in {"VIO_PRIMARY", "HOLD_LAST_SAFE"}
    ):
        evidence_codes.append("localization_confidence_low")
        if tick.localization_mode == "VIO_PRIMARY":
            evidence_codes.append("vio_primary_active")
        if tick.localization_mode == "HOLD_LAST_SAFE":
            evidence_codes.append("hold_last_safe_active")
        contributions["ew_localization_instability"] += (
            config.weight_localization_unstable
        )
        total_weight += config.weight_localization_unstable

    deduped_evidence = []
    for code in evidence_codes:
        if code not in deduped_evidence:
            deduped_evidence.append(code)

    return min(1.0, total_weight), tuple(deduped_evidence), contributions


def _resolve_primary_reason(contributions: dict[str, float]) -> tuple[str, tuple[str, ...]]:
    non_zero_reasons = [
        reason_code
        for reason_code in _PRIMARY_REASON_PRIORITY
        if contributions[reason_code] > 0.0
    ]
    if not non_zero_reasons:
        return "ew_risk_nominal", tuple()

    primary_reason_code = max(
        _PRIMARY_REASON_PRIORITY,
        key=lambda code: (contributions[code], -_PRIMARY_REASON_PRIORITY.index(code)),
    )
    if contributions[primary_reason_code] <= 0.0:
        return "ew_risk_nominal", tuple()
    ordered_reasons = tuple(
        reason_code
        for reason_code in _PRIMARY_REASON_PRIORITY
        if contributions[reason_code] > 0.0
    )
    return primary_reason_code, ordered_reasons


def _risk_level(
    *,
    max_risk: float,
    affected_cell_count: int,
    config: EwRiskMapConfig,
) -> str:
    if affected_cell_count == 0 and max_risk <= 0.0:
        return "none"
    if max_risk < config.risk_low_floor:
        return "low"
    if max_risk < config.risk_medium_floor:
        return "medium"
    return "high"


def _apply_global_decay(grid: list[float], decay: float) -> None:
    multiplier = max(0.0, 1.0 - decay)
    for index, value in enumerate(grid):
        grid[index] = round(value * multiplier, 6)


def _apply_stamp(
    grid: list[float],
    position: tuple[float, float],
    origin: EwGridOrigin,
    width_cells: int,
    height_cells: int,
    cell_size_m: float,
    stamp_radius_m: float,
    stamp_weight: float,
) -> None:
    for y_index in range(height_cells):
        center_y = origin.y_m + (y_index * cell_size_m)
        for x_index in range(width_cells):
            center_x = origin.x_m + (x_index * cell_size_m)
            distance = hypot(center_x - position[0], center_y - position[1])
            if distance > stamp_radius_m:
                continue
            decay = 1.0 - (distance / stamp_radius_m if stamp_radius_m else 0.0)
            delta = stamp_weight * max(0.0, decay)
            flat_index = (y_index * width_cells) + x_index
            grid[flat_index] = min(1.0, round(grid[flat_index] + delta, 6))


def _sample_band_cost(
    *,
    risk_cells: tuple[float, ...],
    sample_position: tuple[float, float],
    origin: EwGridOrigin,
    width_cells: int,
    height_cells: int,
    cell_size_m: float,
    band_half_width_m: float,
) -> float:
    sample_values: list[float] = []
    for y_index in range(height_cells):
        center_y = origin.y_m + (y_index * cell_size_m)
        for x_index in range(width_cells):
            center_x = origin.x_m + (x_index * cell_size_m)
            if hypot(center_x - sample_position[0], center_y - sample_position[1]) > band_half_width_m:
                continue
            flat_index = (y_index * width_cells) + x_index
            sample_values.append(risk_cells[flat_index])
    if not sample_values:
        return 0.0
    return round(sum(sample_values) / len(sample_values), 6)


def _hash_risk_cells(risk_cells: tuple[float, ...]) -> str:
    payload = json.dumps(risk_cells, separators=(",", ":"), ensure_ascii=True)
    return sha256(payload.encode("ascii")).hexdigest()


def _distance_xy(a: Position3D, b: Position3D) -> float:
    return hypot(b.x - a.x, b.y - a.y)
