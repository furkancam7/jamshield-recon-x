"""Deterministic mission decision policy for the vertical slice."""

from __future__ import annotations

from common.enums import MissionState


def decide_mission_state(
    mission_confidence: float,
    gnss_state: str,
    vio_healthy: bool,
) -> MissionState:
    if gnss_state == "nominal" and mission_confidence >= 0.80:
        return MissionState.MISSION_NORMAL

    if gnss_state == "degraded" and mission_confidence >= 0.50:
        return MissionState.MISSION_DEGRADED

    if gnss_state == "denied" and vio_healthy and mission_confidence >= 0.30:
        return MissionState.MISSION_FALLBACK

    if gnss_state == "degraded" and not vio_healthy:
        return MissionState.MISSION_RTL

    if mission_confidence < 0.20 and not vio_healthy:
        return MissionState.MISSION_EMERGENCY_LAND

    return MissionState.MISSION_SAFE_HOLD

