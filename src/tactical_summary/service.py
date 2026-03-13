"""Deterministic operator-facing tactical summary generation."""

from __future__ import annotations

from dataclasses import dataclass


_PRIMARY_PRIORITY = (
    "tactical_abort_active",
    "tactical_safe_hold_active",
    "tactical_fallback_active",
    "tactical_mission_degraded",
    "tactical_ew_hotspot_detected",
    "tactical_sync_risk_observed",
    "tactical_localization_instability_observed",
    "tactical_nominal_overview",
)

_MISSION_LABELS = {
    "MISSION_EXECUTE": "executing",
    "MISSION_DEGRADED": "degraded",
    "MISSION_FALLBACK": "fallback",
    "MISSION_SAFE_HOLD": "safe hold",
    "MISSION_ABORT": "abort",
}

_LOCALIZATION_LABELS = {
    "GNSS_PRIMARY": "GNSS-primary",
    "BLENDED": "blended",
    "VIO_PRIMARY": "VIO-primary",
    "HOLD_LAST_SAFE": "hold-last-safe",
}

_ADVISORY_TEXT = {
    "operator_continue_nominal": "Continue mission on the current route.",
    "operator_continue_with_caution": (
        "Continue with caution and monitor localization confidence."
    ),
    "operator_avoid_high_risk_corridor": (
        "Avoid the highlighted high-risk corridor and reassess route progress."
    ),
    "operator_prepare_manual_review": (
        "Prepare manual review of navigation confidence and route risk."
    ),
    "operator_hold_position_and_investigate": (
        "Hold position and investigate navigation degradation before resuming."
    ),
    "operator_abort_and_retask": "Abort the current route and retask before continuing.",
}


@dataclass(frozen=True)
class TacticalSummaryInputs:
    timestamp_ns: int
    mission_state: str
    mission_primary_reason_code: str
    mission_confidence: float
    localization_mode: str
    effective_vio_state: str
    trust_primary_reason_code: str
    ew_risk_level: str
    ew_primary_reason_code: str
    ew_corridor_cost: float
    ew_affected_cell_count: int


@dataclass(frozen=True)
class TacticalSummaryAssessment:
    timestamp_ns: int
    mission_state: str
    mission_confidence: float
    localization_mode: str
    ew_risk_level: str
    affected_area_count: int
    ew_corridor_cost: float
    primary_reason_code: str
    reason_codes: tuple[str, ...]
    advisory_code: str
    advisory_text: str
    summary_text: str


class TacticalSummaryService:
    """Maps runtime mission/trust/EW outputs into operator-facing summaries."""

    def evaluate(self, inputs: TacticalSummaryInputs) -> TacticalSummaryAssessment:
        primary_reason_code, reason_codes = _resolve_reasons(inputs)
        advisory_code = _resolve_advisory(inputs, primary_reason_code)
        advisory_text = _ADVISORY_TEXT[advisory_code]
        summary_text = _render_summary_text(inputs, advisory_text)
        return TacticalSummaryAssessment(
            timestamp_ns=inputs.timestamp_ns,
            mission_state=inputs.mission_state,
            mission_confidence=round(inputs.mission_confidence, 3),
            localization_mode=inputs.localization_mode,
            ew_risk_level=inputs.ew_risk_level,
            affected_area_count=inputs.ew_affected_cell_count,
            ew_corridor_cost=round(inputs.ew_corridor_cost, 3),
            primary_reason_code=primary_reason_code,
            reason_codes=reason_codes,
            advisory_code=advisory_code,
            advisory_text=advisory_text,
            summary_text=summary_text,
        )


def _resolve_reasons(inputs: TacticalSummaryInputs) -> tuple[str, tuple[str, ...]]:
    reasons: list[str] = []

    if inputs.mission_state == "MISSION_ABORT":
        reasons.append("tactical_abort_active")
    elif inputs.mission_state == "MISSION_SAFE_HOLD":
        reasons.append("tactical_safe_hold_active")
    elif inputs.mission_state == "MISSION_FALLBACK":
        reasons.append("tactical_fallback_active")
    elif inputs.mission_state == "MISSION_DEGRADED":
        if inputs.trust_primary_reason_code == "sync_quality_low":
            reasons.append("tactical_sync_risk_observed")
        else:
            reasons.append("tactical_mission_degraded")
    elif inputs.mission_state == "MISSION_EXECUTE" and inputs.ew_risk_level == "high":
        reasons.append("tactical_ew_hotspot_detected")
    elif inputs.trust_primary_reason_code == "sync_quality_low":
        reasons.append("tactical_sync_risk_observed")
    elif (
        inputs.trust_primary_reason_code == "localization_confidence_low"
        or inputs.ew_primary_reason_code == "ew_localization_instability"
        or inputs.effective_vio_state == "lost"
    ):
        reasons.append("tactical_localization_instability_observed")
    else:
        reasons.append("tactical_nominal_overview")

    if inputs.ew_primary_reason_code == "ew_gnss_denial_hotspot":
        _append_unique(reasons, "tactical_ew_hotspot_detected")
    if inputs.trust_primary_reason_code == "sync_quality_low":
        _append_unique(reasons, "tactical_sync_risk_observed")
    if (
        inputs.trust_primary_reason_code == "localization_confidence_low"
        or inputs.ew_primary_reason_code == "ew_localization_instability"
        or inputs.effective_vio_state == "lost"
    ):
        _append_unique(reasons, "tactical_localization_instability_observed")
    if (
        inputs.mission_state == "MISSION_DEGRADED"
        and "tactical_mission_degraded" not in reasons
        and inputs.trust_primary_reason_code != "sync_quality_low"
    ):
        _append_unique(reasons, "tactical_mission_degraded")

    ordered = tuple(reason for reason in _PRIMARY_PRIORITY if reason in reasons)
    return ordered[0], ordered


def _resolve_advisory(
    inputs: TacticalSummaryInputs,
    primary_reason_code: str,
) -> str:
    if inputs.mission_state == "MISSION_ABORT":
        return "operator_abort_and_retask"
    if inputs.mission_state == "MISSION_SAFE_HOLD":
        return "operator_hold_position_and_investigate"
    if inputs.mission_state == "MISSION_FALLBACK":
        if inputs.ew_risk_level in {"medium", "high"}:
            return "operator_avoid_high_risk_corridor"
        return "operator_prepare_manual_review"
    if inputs.mission_state == "MISSION_DEGRADED":
        return "operator_continue_with_caution"
    if primary_reason_code == "tactical_ew_hotspot_detected":
        return "operator_avoid_high_risk_corridor"
    if primary_reason_code in {
        "tactical_sync_risk_observed",
        "tactical_localization_instability_observed",
    }:
        return "operator_continue_with_caution"
    return "operator_continue_nominal"


def _render_summary_text(
    inputs: TacticalSummaryInputs,
    advisory_text: str,
) -> str:
    mission_label = _MISSION_LABELS[inputs.mission_state]
    localization_label = _LOCALIZATION_LABELS[inputs.localization_mode]
    sentence_one = (
        f"Mission is {mission_label} with {localization_label} localization; "
        f"EW risk is {inputs.ew_risk_level}."
    )
    return f"{sentence_one} {advisory_text}"


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)
