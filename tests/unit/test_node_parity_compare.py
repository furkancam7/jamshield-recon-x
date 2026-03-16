import json
from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.artifact_schema import validate_node_parity_results
from evaluation.node_parity_compare import compare_node_parity
from runtime.node_runner import run_node_scenario
from scenario_orchestrator.main import run_scenario


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"


class NodeParityCompareTests(unittest.TestCase):
    def test_validator_accepts_valid_payload(self) -> None:
        payload = {
            "schema_version": "1.0",
            "baseline_run_id": "baseline",
            "node_run_id": "node",
            "scenario_ids": ["s1_nominal"],
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "parity_result": "PASS",
                    "divergence": None,
                }
            ],
            "overall_result": "PASS",
        }
        validate_node_parity_results(payload)

    def test_validator_rejects_fail_without_divergence(self) -> None:
        payload = {
            "schema_version": "1.0",
            "baseline_run_id": "baseline",
            "node_run_id": "node",
            "scenario_ids": ["s1_nominal"],
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "parity_result": "FAIL",
                    "divergence": None,
                }
            ],
            "overall_result": "FAIL",
        }
        with self.assertRaises(ValueError):
            validate_node_parity_results(payload)

    def test_compare_detects_runtime_divergence(self) -> None:
        baseline_dir = make_temp_dir(self)
        node_dir = make_temp_dir(self)

        run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=baseline_dir,
            config_path=CONFIG_PATH,
            run_id="baseline",
        )
        run_node_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=node_dir,
            config_path=CONFIG_PATH,
            run_id="node",
        )

        runtime_trace_path = node_dir / "s1_nominal_runtime_trace.json"
        runtime_trace = json.loads(runtime_trace_path.read_text(encoding="utf-8"))
        runtime_trace["entries"][0]["mission_state"] = "MISSION_ABORT"
        runtime_trace_path.write_text(
            json.dumps(runtime_trace, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        payload = compare_node_parity(
            baseline_run_dir=baseline_dir,
            node_run_dir=node_dir,
            scenario_ids=("s1_nominal",),
        )
        self.assertEqual(payload["overall_result"], "FAIL")
        self.assertEqual(payload["scenarios"][0]["parity_result"], "FAIL")
        self.assertIsNotNone(payload["scenarios"][0]["divergence"])


if __name__ == "__main__":
    unittest.main()
