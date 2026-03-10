"""Mission state enum for the first working vertical slice."""

from enum import Enum


class MissionState(str, Enum):
    MISSION_NORMAL = "MISSION_NORMAL"
    MISSION_DEGRADED = "MISSION_DEGRADED"
    MISSION_FALLBACK = "MISSION_FALLBACK"
    MISSION_SAFE_HOLD = "MISSION_SAFE_HOLD"
    MISSION_RTL = "MISSION_RTL"
    MISSION_EMERGENCY_LAND = "MISSION_EMERGENCY_LAND"

