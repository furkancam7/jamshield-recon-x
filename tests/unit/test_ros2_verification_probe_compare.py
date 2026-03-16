import json
from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.artifact_schema import validate_ros2_verification_probe_results
from evaluation.ros2_verification_probe_compare import compare_ros2_verification_probe
from runtime.ros2_launch_runner import run_ros2_launch_scenario
from scenario_orchestrator.main import run_scenario


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"


class Ros2VerificationProbeCompareTests(unittest.TestCase):
    def test_validator_accepts_valid_payload(self) -> None:
        payload = {
            "schema_version": "1.0",
            "baseline_run_id": "baseline",
            "verification_run_id": "verification",
            "scenario_ids": ["s1_nominal"],
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "logger_node_result": "PASS",
                    "evaluation_node_result": "PASS",
                    "probe_result": "PASS",
                    "failed_checks": [],
                    "divergence": None,
                }
            ],
            "overall_result": "PASS",
        }
        validate_ros2_verification_probe_results(payload)

    def test_validator_rejects_fail_without_details(self) -> None:
        payload = {
            "schema_version": "1.0",
            "baseline_run_id": "baseline",
            "verification_run_id": "verification",
            "scenario_ids": ["s1_nominal"],
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "logger_node_result": "PASS",
                    "evaluation_node_result": "FAIL",
                    "probe_result": "FAIL",
                    "failed_checks": [],
                    "divergence": None,
                }
            ],
            "overall_result": "FAIL",
        }
        with self.assertRaises(ValueError):
            validate_ros2_verification_probe_results(payload)

    def test_compare_reports_forced_logger_failure(self) -> None:
        baseline_dir = make_temp_dir(self)
        verification_dir = make_temp_dir(self)

        run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=baseline_dir,
            config_path=CONFIG_PATH,
            run_id="baseline",
        )
        run_ros2_launch_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=verification_dir,
            config_path=CONFIG_PATH,
            run_id="verification",
            verification_nodes_enabled=True,
        )

        verification_result_path = (
            verification_dir / "s1_nominal_verification_node_results.json"
        )
        payload = json.loads(verification_result_path.read_text(encoding="utf-8"))
        payload["logger_node"]["result"] = "FAIL"
        payload["logger_node"]["failed_checks"] = ["forced_failure"]
        payload["overall_result"] = "FAIL"
        verification_result_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        compare_payload = compare_ros2_verification_probe(
            baseline_run_dir=baseline_dir,
            verification_run_dir=verification_dir,
            scenario_ids=("s1_nominal",),
        )
        self.assertEqual(compare_payload["overall_result"], "FAIL")
        self.assertEqual(compare_payload["scenarios"][0]["logger_node_result"], "FAIL")
        self.assertIn("forced_failure", compare_payload["scenarios"][0]["failed_checks"])


if __name__ == "__main__":
    unittest.main()
