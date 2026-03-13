from pathlib import Path
import unittest

from common.config import load_app_config
from common.enums import MissionState
from mission_continuity.decision_policy import decide_candidate_mission_state
from mission_continuity.state_machine import MissionStateMachine


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


class MissionContinuityTests(unittest.TestCase):
    def test_denied_with_good_vio_enters_fallback(self) -> None:
        config = load_app_config(CONFIG_PATH)
        decision = MissionStateMachine(config=config.mission).update(
            mission_confidence=0.35,
            gnss_state="denied",
            effective_vio_state="good",
        )
        self.assertEqual(decision.final_state, MissionState.MISSION_FALLBACK)
        self.assertEqual(decision.primary_reason_code, "mission_fallback_vio_primary")

    def test_recovery_dwell_delays_return_to_execute(self) -> None:
        config = load_app_config(CONFIG_PATH)
        machine = MissionStateMachine(config=config.mission)

        first = machine.update(
            mission_confidence=0.35,
            gnss_state="denied",
            effective_vio_state="good",
        )
        candidate = decide_candidate_mission_state(
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
            config=config.mission,
        )
        second = machine.update(
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
        )
        third = machine.update(
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
        )

        self.assertEqual(first.final_state, MissionState.MISSION_FALLBACK)
        self.assertEqual(candidate.candidate_state, MissionState.MISSION_EXECUTE)
        self.assertEqual(second.candidate_state, MissionState.MISSION_EXECUTE)
        self.assertEqual(second.final_state, MissionState.MISSION_FALLBACK)
        self.assertEqual(second.primary_reason_code, "mission_recovery_dwell_active")
        self.assertEqual(third.final_state, MissionState.MISSION_EXECUTE)

    def test_safe_hold_timeout_escalates_to_abort(self) -> None:
        config = load_app_config(CONFIG_PATH)
        machine = MissionStateMachine(config=config.mission)

        first = machine.update(
            mission_confidence=0.35,
            gnss_state="denied",
            effective_vio_state="weak",
        )
        second = machine.update(
            mission_confidence=0.35,
            gnss_state="denied",
            effective_vio_state="weak",
        )
        third = machine.update(
            mission_confidence=0.35,
            gnss_state="denied",
            effective_vio_state="weak",
        )

        self.assertEqual(first.final_state, MissionState.MISSION_SAFE_HOLD)
        self.assertEqual(second.final_state, MissionState.MISSION_SAFE_HOLD)
        self.assertEqual(third.final_state, MissionState.MISSION_ABORT)
        self.assertEqual(third.primary_reason_code, "mission_abort_safe_hold_timeout")

    def test_abort_is_terminal_once_entered(self) -> None:
        config = load_app_config(CONFIG_PATH)
        machine = MissionStateMachine(config=config.mission)

        first = machine.update(
            mission_confidence=0.10,
            gnss_state="denied",
            effective_vio_state="lost",
        )
        second = machine.update(
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
        )

        self.assertEqual(first.final_state, MissionState.MISSION_ABORT)
        self.assertEqual(first.primary_reason_code, "mission_abort_vio_lost")
        self.assertEqual(second.final_state, MissionState.MISSION_ABORT)
        self.assertEqual(second.primary_reason_code, "mission_abort_terminal_latched")

    def test_oscillation_detection_forces_safe_hold(self) -> None:
        config = load_app_config(CONFIG_PATH)
        machine = MissionStateMachine(config=config.mission)

        first = machine.update(
            mission_confidence=0.62,
            gnss_state="degraded",
            effective_vio_state="good",
        )
        second = machine.update(
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
        )
        third = machine.update(
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
        )
        fourth = machine.update(
            mission_confidence=0.62,
            gnss_state="degraded",
            effective_vio_state="good",
        )

        self.assertEqual(first.final_state, MissionState.MISSION_DEGRADED)
        self.assertEqual(second.primary_reason_code, "mission_recovery_dwell_active")
        self.assertEqual(third.final_state, MissionState.MISSION_EXECUTE)
        self.assertEqual(fourth.final_state, MissionState.MISSION_SAFE_HOLD)
        self.assertEqual(
            fourth.primary_reason_code,
            "mission_state_oscillation_detected",
        )


if __name__ == "__main__":
    unittest.main()
