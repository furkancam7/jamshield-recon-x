from pathlib import Path
import unittest

from mission_continuity.state_machine import MissionStateMachine
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator
from gnss_trust.trust_service import TrustService


ROOT_DIR = Path(__file__).resolve().parents[2]
DENIED_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s3_gnss_denied_zone.yaml"


def _execute_denied_scenario(vio_healthy: bool) -> tuple[str, float, float, str]:
    manifest = load_manifest(DENIED_SCENARIO)
    snapshot = ScenarioOrchestrator(manifest).build_snapshot()
    assessment = TrustService().evaluate(snapshot=snapshot, vio_healthy=vio_healthy)
    mission_state = MissionStateMachine().update(
        mission_confidence=assessment.mission_confidence,
        gnss_state=assessment.gnss_state,
        vio_healthy=assessment.vio_healthy,
    )
    return (
        assessment.gnss_state,
        assessment.trust_score,
        assessment.mission_confidence,
        mission_state.value,
    )


class ExecutionConsistencyTests(unittest.TestCase):
    def test_denied_scenario_is_deterministic_for_same_inputs(self) -> None:
        first = _execute_denied_scenario(vio_healthy=False)
        second = _execute_denied_scenario(vio_healthy=False)

        self.assertEqual(first, second)
        self.assertEqual(first[0], "denied")
        self.assertEqual(first[1], 0.05)
        self.assertEqual(first[2], 0.038)
        self.assertEqual(first[3], "MISSION_EMERGENCY_LAND")

    def test_denied_scenario_changes_only_when_vio_health_changes(self) -> None:
        unhealthy = _execute_denied_scenario(vio_healthy=False)
        healthy = _execute_denied_scenario(vio_healthy=True)

        self.assertEqual(unhealthy[0], healthy[0])
        self.assertEqual(unhealthy[1], healthy[1])
        self.assertNotEqual(unhealthy[2], healthy[2])
        self.assertNotEqual(unhealthy[3], healthy[3])


if __name__ == "__main__":
    unittest.main()
