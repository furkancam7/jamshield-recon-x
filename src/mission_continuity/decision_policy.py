"""Deterministic mission decision policy for the vertical slice."""

from __future__ import annotations

from common.config import MissionConfig
from common.enums import MissionState


def decide_mission_state(
    mission_confidence: float,
    gnss_state: str,
    vio_healthy: bool,
    config: MissionConfig,
) -> MissionState:
    if (
        gnss_state == "nominal"
        and mission_confidence >= config.nominal_confidence_threshold
    ):
        return MissionState.MISSION_NORMAL

    if (
        gnss_state == "degraded"
        and mission_confidence >= config.degraded_confidence_threshold
    ):
        return MissionState.MISSION_DEGRADED

    if (
        gnss_state == "denied"
        and vio_healthy
        and mission_confidence >= config.denied_fallback_confidence_threshold
    ):
        return MissionState.MISSION_FALLBACK

    if gnss_state == "degraded" and not vio_healthy:
        return MissionState.MISSION_RTL

    if (
        mission_confidence < config.emergency_land_confidence_threshold
        and not vio_healthy
    ):
        return MissionState.MISSION_EMERGENCY_LAND

    return MissionState.MISSION_SAFE_HOLD
