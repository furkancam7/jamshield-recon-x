import unittest

from common.enums import MissionState
from mission_continuity.state_machine import MissionStateMachine


class MissionContinuityTests(unittest.TestCase):
    def test_denied_with_healthy_vio_enters_fallback(self) -> None:
        state = MissionStateMachine().update(
            mission_confidence=0.35,
            gnss_state="denied",
            vio_healthy=True,
        )
        self.assertEqual(state, MissionState.MISSION_FALLBACK)

    def test_degraded_without_vio_routes_home(self) -> None:
        state = MissionStateMachine().update(
            mission_confidence=0.45,
            gnss_state="degraded",
            vio_healthy=False,
        )
        self.assertEqual(state, MissionState.MISSION_RTL)

    def test_low_confidence_without_vio_lands(self) -> None:
        state = MissionStateMachine().update(
            mission_confidence=0.10,
            gnss_state="denied",
            vio_healthy=False,
        )
        self.assertEqual(state, MissionState.MISSION_EMERGENCY_LAND)


if __name__ == "__main__":
    unittest.main()

