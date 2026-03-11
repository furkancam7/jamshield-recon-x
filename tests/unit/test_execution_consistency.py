from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from common.config import load_app_config
from mission_continuity.state_machine import MissionStateMachine
from scenario_orchestrator.main import run_scenario
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator
from gnss_trust.trust_service import TrustService


ROOT_DIR = Path(__file__).resolve().parents[2]
DENIED_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s3_gnss_denied_zone.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


def _execute_denied_scenario(vio_healthy: bool) -> tuple[str, float, float, str]:
    config = load_app_config(CONFIG_PATH)
    manifest = load_manifest(DENIED_SCENARIO)
    snapshot = ScenarioOrchestrator(manifest).build_snapshot()
    assessment = TrustService(config.trust).evaluate(
        snapshot=snapshot, vio_healthy=vio_healthy
    )
    mission_state = MissionStateMachine(config=config.mission).update(
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

    def test_repeated_runs_produce_equivalent_artifact_logic(self) -> None:
        with TemporaryDirectory() as first_dir, TemporaryDirectory() as second_dir:
            first = run_scenario(
                scenario_path=NOMINAL_SCENARIO,
                output_dir=first_dir,
                config_path=CONFIG_PATH,
                run_id="repeatable-run",
                vio_healthy=True,
            )
            second = run_scenario(
                scenario_path=NOMINAL_SCENARIO,
                output_dir=second_dir,
                config_path=CONFIG_PATH,
                run_id="repeatable-run",
                vio_healthy=True,
            )

            for key in (
                "scenario_id",
                "gnss_state",
                "trust_score",
                "mission_confidence",
                "mission_state",
                "config_id",
                "software_revision",
            ):
                self.assertEqual(first[key], second[key])


if __name__ == "__main__":
    unittest.main()
