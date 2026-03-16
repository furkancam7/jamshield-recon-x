import json
from pathlib import Path
import unittest

from _support import make_temp_dir
from runtime.node_runner import run_node_scenario
from runtime.verification_nodes import (
    run_evaluation_node_probe,
    run_logger_node_probe,
    run_verification_nodes_probe,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"


class VerificationNodeRunnerTests(unittest.TestCase):
    def test_verification_nodes_probe_passes_for_nominal(self) -> None:
        run_dir = make_temp_dir(self)
        run_node_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=run_dir,
            config_path=CONFIG_PATH,
            run_id="verification",
        )

        payload = run_verification_nodes_probe(
            scenario_id="s1_nominal",
            scenario_path=NOMINAL_SCENARIO,
            run_dir=run_dir,
            sim_config_path=CONFIG_PATH,
        )
        self.assertEqual(payload["overall_result"], "PASS")
        self.assertEqual(payload["logger_node"]["result"], "PASS")
        self.assertEqual(payload["evaluation_node"]["result"], "PASS")
        self.assertTrue((run_dir / "s1_nominal_verification_node_results.json").exists())

    def test_logger_probe_detects_missing_artifact(self) -> None:
        run_dir = make_temp_dir(self)
        run_node_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=run_dir,
            config_path=CONFIG_PATH,
            run_id="verification-missing",
        )
        (run_dir / "s1_nominal_truth_trace.json").unlink()

        logger_result = run_logger_node_probe(
            scenario_id="s1_nominal",
            run_dir=run_dir,
        )
        self.assertEqual(logger_result["result"], "FAIL")
        self.assertTrue(
            any("truth_trace" in check for check in logger_result["failed_checks"])
        )

    def test_evaluation_probe_detects_replay_divergence(self) -> None:
        run_dir = make_temp_dir(self)
        run_node_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=run_dir,
            config_path=CONFIG_PATH,
            run_id="verification-divergence",
        )
        runtime_trace_path = run_dir / "s1_nominal_runtime_trace.json"
        runtime_trace = json.loads(runtime_trace_path.read_text(encoding="utf-8"))
        runtime_trace["entries"][0]["mission_state"] = "MISSION_ABORT"
        runtime_trace_path.write_text(
            json.dumps(runtime_trace, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        evaluation_result = run_evaluation_node_probe(
            scenario_id="s1_nominal",
            scenario_path=NOMINAL_SCENARIO,
            run_dir=run_dir,
            sim_config_path=CONFIG_PATH,
        )
        self.assertEqual(evaluation_result["result"], "FAIL")
        self.assertEqual(evaluation_result["primary_reason_code"], "deterministic_replay_failed")


if __name__ == "__main__":
    unittest.main()
