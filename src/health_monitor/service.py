"""Deterministic health-monitor publication logic."""

from __future__ import annotations

from dataclasses import dataclass

NOMINAL_HEALTH_REASON = "trust_inputs_nominal"

_CRITICAL_REASON_ORDER = (
    "mission_abort_vio_lost",
    "vio_trust_low",
    "sync_quality_low",
    "gnss_denial_suspected",
    "gnss_measurement_quality_low",
    "localization_confidence_low",
)


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _dedupe_codes(reason_codes: list[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for code in reason_codes:
        if code in seen:
            continue
        seen.add(code)
        ordered.append(code)
    return tuple(ordered)


@dataclass(frozen=True)
class HealthStatusAssessment:
    tick_index: int
    timestamp_ns: int
    subsystem: str
    severity: str
    stale_duration_ms: float
    primary_reason_code: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class FaultEventAssessment:
    timestamp_ns: int
    event_id: str
    subsystem: str
    severity: str
    primary_reason_code: str
    reason_codes: tuple[str, ...]
    details: str


@dataclass(frozen=True)
class HealthMonitorAssessment:
    health_status: HealthStatusAssessment
    fault_event: FaultEventAssessment | None


class HealthMonitorService:
    """Computes deterministic health and fault publications for each runtime tick."""

    def __init__(
        self,
        *,
        sync_low_threshold: float,
        degraded_confidence_threshold: float,
        abort_confidence_threshold: float,
    ) -> None:
        self._sync_low_threshold = float(sync_low_threshold)
        self._degraded_confidence_threshold = float(degraded_confidence_threshold)
        self._abort_confidence_threshold = float(abort_confidence_threshold)

    def evaluate(
        self,
        *,
        scenario_id: str,
        tick_index: int,
        timestamp_ns: int,
        sync_quality: float,
        mission_confidence: float,
        gnss_state: str,
        effective_vio_state: str,
        localization_mode: str,
        mission_state: str,
    ) -> HealthMonitorAssessment:
        resolved_sync_quality = round(_clamp(float(sync_quality)), 3)
        resolved_mission_confidence = round(_clamp(float(mission_confidence)), 3)
        resolved_vio_state = str(effective_vio_state)
        resolved_gnss_state = str(gnss_state)
        resolved_mission_state = str(mission_state)

        reason_codes: list[str] = []
        if resolved_sync_quality < self._sync_low_threshold:
            reason_codes.append("sync_quality_low")
        if resolved_gnss_state == "denied":
            reason_codes.append("gnss_denial_suspected")
        elif resolved_gnss_state == "degraded":
            reason_codes.append("gnss_measurement_quality_low")
        if resolved_vio_state in {"weak", "lost"}:
            reason_codes.append("vio_trust_low")
        if resolved_mission_confidence < self._degraded_confidence_threshold:
            reason_codes.append("localization_confidence_low")
        if resolved_mission_state == "MISSION_ABORT":
            reason_codes.append("mission_abort_vio_lost")

        canonical_reasons = _dedupe_codes(reason_codes)
        severity = _resolve_severity(
            reason_codes=canonical_reasons,
            mission_state=resolved_mission_state,
            effective_vio_state=resolved_vio_state,
            mission_confidence=resolved_mission_confidence,
            abort_confidence_threshold=self._abort_confidence_threshold,
        )
        primary_reason_code = _resolve_primary_reason(canonical_reasons)
        stale_duration_ms = round(
            max(0.0, self._sync_low_threshold - resolved_sync_quality) * 1000.0,
            3,
        )

        health_status = HealthStatusAssessment(
            tick_index=tick_index,
            timestamp_ns=timestamp_ns,
            subsystem="navigation_runtime",
            severity=severity,
            stale_duration_ms=stale_duration_ms,
            primary_reason_code=primary_reason_code,
            reason_codes=canonical_reasons,
        )
        fault_event = _build_fault_event(
            scenario_id=scenario_id,
            tick_index=tick_index,
            timestamp_ns=timestamp_ns,
            severity=severity,
            primary_reason_code=primary_reason_code,
            reason_codes=canonical_reasons,
            sync_quality=resolved_sync_quality,
            mission_confidence=resolved_mission_confidence,
            gnss_state=resolved_gnss_state,
            effective_vio_state=resolved_vio_state,
            localization_mode=localization_mode,
            mission_state=resolved_mission_state,
        )
        return HealthMonitorAssessment(health_status=health_status, fault_event=fault_event)


def _resolve_primary_reason(reason_codes: tuple[str, ...]) -> str:
    if not reason_codes:
        return NOMINAL_HEALTH_REASON
    reason_set = set(reason_codes)
    for candidate in _CRITICAL_REASON_ORDER:
        if candidate in reason_set:
            return candidate
    return reason_codes[0]


def _resolve_severity(
    *,
    reason_codes: tuple[str, ...],
    mission_state: str,
    effective_vio_state: str,
    mission_confidence: float,
    abort_confidence_threshold: float,
) -> str:
    if not reason_codes:
        return "nominal"
    if mission_state == "MISSION_ABORT":
        return "critical"
    if effective_vio_state == "lost":
        return "critical"
    if mission_confidence < abort_confidence_threshold:
        return "critical"
    return "warning"


def _build_fault_event(
    *,
    scenario_id: str,
    tick_index: int,
    timestamp_ns: int,
    severity: str,
    primary_reason_code: str,
    reason_codes: tuple[str, ...],
    sync_quality: float,
    mission_confidence: float,
    gnss_state: str,
    effective_vio_state: str,
    localization_mode: str,
    mission_state: str,
) -> FaultEventAssessment | None:
    if severity == "nominal":
        return None

    details = (
        f"sync_quality={sync_quality:.3f}; "
        f"mission_confidence={mission_confidence:.3f}; "
        f"gnss_state={gnss_state}; "
        f"effective_vio_state={effective_vio_state}; "
        f"localization_mode={localization_mode}; "
        f"mission_state={mission_state}"
    )
    return FaultEventAssessment(
        timestamp_ns=timestamp_ns,
        event_id=f"{scenario_id}_fault_{tick_index:04d}",
        subsystem="health_monitor_node",
        severity=severity,
        primary_reason_code=primary_reason_code,
        reason_codes=reason_codes,
        details=details,
    )
