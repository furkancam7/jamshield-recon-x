"""State manager for deterministic mission continuity."""

from __future__ import annotations

from dataclasses import dataclass

from common.config import MissionConfig
from common.enums import MissionState

from .decision_policy import decide_mission_state


@dataclass
class MissionStateMachine:
    config: MissionConfig
    current_state: MissionState = MissionState.MISSION_NORMAL

    def update(
        self,
        mission_confidence: float,
        gnss_state: str,
        vio_healthy: bool,
    ) -> MissionState:
        self.current_state = decide_mission_state(
            mission_confidence=mission_confidence,
            gnss_state=gnss_state,
            vio_healthy=vio_healthy,
            config=self.config,
        )
        return self.current_state
