from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.artifact_schema import validate_health_monitor_probe_results
from evaluation.health_monitor_probe_compare import compare_health_monitor_probe
from runtime.ros2_launch_runner import run_ros2_launch_scenario
from scenario_orchestrator.main import run_scenario


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"


class HealthMonitorProbeCompareTests(unittest.TestCase):
    def test_compare_health_monitor_probe_passes_nominal(self) -> None:
        baseline_dir = make_temp_dir(self)
        probe_dir = make_temp_dir(self)

        run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=baseline_dir,
            config_path=CONFIG_PATH,
            run_id="baseline",
        )
        run_ros2_launch_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=probe_dir,
            config_path=CONFIG_PATH,
            run_id="health-probe",
        )

        payload = compare_health_monitor_probe(
            baseline_run_dir=baseline_dir,
            health_probe_run_dir=probe_dir,
            scenario_ids=("s1_nominal",),
        )
        validate_health_monitor_probe_results(payload)
        self.assertEqual(payload["overall_result"], "PASS")
        self.assertEqual(payload["scenarios"][0]["probe_result"], "PASS")

    def test_compare_health_monitor_probe_fails_when_health_artifact_missing(self) -> None:
        baseline_dir = make_temp_dir(self)
        probe_dir = make_temp_dir(self)

        run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=baseline_dir,
            config_path=CONFIG_PATH,
            run_id="baseline",
        )
        run_ros2_launch_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=probe_dir,
            config_path=CONFIG_PATH,
            run_id="health-probe",
        )
        (probe_dir / "s1_nominal_mission_health.json").unlink()

        payload = compare_health_monitor_probe(
            baseline_run_dir=baseline_dir,
            health_probe_run_dir=probe_dir,
            scenario_ids=("s1_nominal",),
        )
        validate_health_monitor_probe_results(payload)
        scenario = payload["scenarios"][0]
        self.assertEqual(payload["overall_result"], "FAIL")
        self.assertEqual(scenario["probe_result"], "FAIL")
        self.assertIn("mission_health_missing", scenario["failed_checks"])

    def test_probe_schema_rejects_missing_required_field(self) -> None:
        payload = {
            "schema_version": "1.0",
            "baseline_run_id": "baseline",
            "health_probe_run_id": "probe",
            "scenario_ids": ["s1_nominal"],
            "scenarios": [],
        }
        with self.assertRaises(ValueError):
            validate_health_monitor_probe_results(payload)


if __name__ == "__main__":
    unittest.main()
