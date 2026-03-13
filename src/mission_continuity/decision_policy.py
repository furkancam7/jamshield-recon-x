"""Deterministic mission candidate policy for mission continuity."""

from __future__ import annotations

from dataclasses import dataclass

from common.config import MissionConfig
from common.enums import MissionState

MISSION_STATE_SEVERITY: dict[MissionState, int] = {
    MissionState.MISSION_EXECUTE: 0,
    MissionState.MISSION_DEGRADED: 1,
    MissionState.MISSION_FALLBACK: 2,
    MissionState.MISSION_SAFE_HOLD: 3,
    MissionState.MISSION_ABORT: 4,
}


@dataclass(frozen=True)
class MissionCandidateDecision:
    candidate_state: MissionState
    primary_reason_code: str
    reason_codes: tuple[str, ...]


def decide_candidate_mission_state(
    mission_confidence: float,
    gnss_state: str,
    effective_vio_state: str,
    config: MissionConfig,
) -> MissionCandidateDecision:
    if (
        gnss_state == "nominal"
        and mission_confidence >= config.nominal_confidence_threshold
    ):
        return _decision(
            MissionState.MISSION_EXECUTE,
            "mission_execute_nominal",
        )

    if (
        gnss_state == "degraded"
        and mission_confidence >= config.degraded_confidence_threshold
    ):
        return _decision(
            MissionState.MISSION_DEGRADED,
            "mission_degraded_gnss_reduced",
        )

    if (
        gnss_state == "denied"
        and effective_vio_state == "good"
        and mission_confidence >= config.denied_fallback_confidence_threshold
    ):
        return _decision(
            MissionState.MISSION_FALLBACK,
            "mission_fallback_vio_primary",
        )

    if gnss_state == "denied" and effective_vio_state == "weak":
        return _decision(
            MissionState.MISSION_SAFE_HOLD,
            "mission_safe_hold_vio_weak",
        )

    if gnss_state == "degraded" and effective_vio_state == "lost":
        return _decision(
            MissionState.MISSION_ABORT,
            "mission_abort_vio_lost",
        )

    if (
        mission_confidence < config.emergency_land_confidence_threshold
        and effective_vio_state == "lost"
    ):
        return _decision(
            MissionState.MISSION_ABORT,
            "mission_abort_vio_lost",
        )

    return _decision(
        MissionState.MISSION_SAFE_HOLD,
        "mission_safe_hold_localization_unstable",
    )


def decide_mission_state(
    mission_confidence: float,
    gnss_state: str,
    effective_vio_state: str,
    config: MissionConfig,
) -> MissionState:
    return decide_candidate_mission_state(
        mission_confidence=mission_confidence,
        gnss_state=gnss_state,
        effective_vio_state=effective_vio_state,
        config=config,
    ).candidate_state


def _decision(
    state: MissionState,
    primary_reason_code: str,
) -> MissionCandidateDecision:
    return MissionCandidateDecision(
        candidate_state=state,
        primary_reason_code=primary_reason_code,
        reason_codes=(primary_reason_code,),
    )
