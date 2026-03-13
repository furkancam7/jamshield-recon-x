"""Mission state enum for the first working vertical slice."""

from enum import Enum


class MissionState(str, Enum):
    MISSION_EXECUTE = "MISSION_EXECUTE"
    MISSION_DEGRADED = "MISSION_DEGRADED"
    MISSION_FALLBACK = "MISSION_FALLBACK"
    MISSION_SAFE_HOLD = "MISSION_SAFE_HOLD"
    MISSION_ABORT = "MISSION_ABORT"
