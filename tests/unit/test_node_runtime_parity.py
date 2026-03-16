from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.node_parity_compare import compare_node_parity
from logging_replay.replay import compare_replay_run
from runtime.node_runner import run_node_scenario
from scenario_orchestrator.main import run_scenario


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"
DENIED_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s3_gnss_denied_zone.yaml"


class NodeRuntimeParityTests(unittest.TestCase):
    def test_nominal_node_runtime_matches_file_runtime(self) -> None:
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

        result = compare_replay_run(
            scenario_id="s1_nominal",
            original_run_dir=baseline_dir,
            replay_run_dir=node_dir,
        )
        self.assertEqual(result["replay_result"], "PASS")
        self.assertIsNone(result["divergence"])

    def test_denied_node_runtime_matches_file_runtime(self) -> None:
        baseline_dir = make_temp_dir(self)
        node_dir = make_temp_dir(self)

        run_scenario(
            scenario_path=DENIED_SCENARIO,
            output_dir=baseline_dir,
            config_path=CONFIG_PATH,
            run_id="baseline",
        )
        run_node_scenario(
            scenario_path=DENIED_SCENARIO,
            output_dir=node_dir,
            config_path=CONFIG_PATH,
            run_id="node",
        )

        result = compare_replay_run(
            scenario_id="s3_gnss_denied_zone",
            original_run_dir=baseline_dir,
            replay_run_dir=node_dir,
        )
        self.assertEqual(result["replay_result"], "PASS")
        self.assertIsNone(result["divergence"])

    def test_node_parity_bundle_reports_pass_for_s1_and_s3(self) -> None:
        baseline_dir = make_temp_dir(self)
        node_dir = make_temp_dir(self)

        for scenario_path in (NOMINAL_SCENARIO, DENIED_SCENARIO):
            run_scenario(
                scenario_path=scenario_path,
                output_dir=baseline_dir,
                config_path=CONFIG_PATH,
                run_id="baseline",
            )
            run_node_scenario(
                scenario_path=scenario_path,
                output_dir=node_dir,
                config_path=CONFIG_PATH,
                run_id="node",
            )

        payload = compare_node_parity(
            baseline_run_dir=baseline_dir,
            node_run_dir=node_dir,
            scenario_ids=("s1_nominal", "s3_gnss_denied_zone"),
        )

        self.assertEqual(payload["overall_result"], "PASS")
        self.assertEqual(len(payload["scenarios"]), 2)
        self.assertTrue(all(item["parity_result"] == "PASS" for item in payload["scenarios"]))


if __name__ == "__main__":
    unittest.main()
