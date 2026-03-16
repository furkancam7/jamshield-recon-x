import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from _support import make_temp_dir
from logging_replay.replay import compare_replay_run
from runtime.ros2_launch_runner import (
    build_ros2_launch_plan,
    run_ros2_launch_scenario,
    validate_ros2_launch_plan,
)
from scenario_orchestrator.main import run_scenario


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"
NOMINAL_SCENARIO_RELATIVE = "scenarios/baseline/s1_nominal.yaml"
LAUNCH_FILE = ROOT_DIR / "launch" / "runtime_probe.launch.py"
LAUNCH_SCRIPT = "scripts/run_ros2_launch_scenario.sh"


class Ros2LaunchRunnerTests(unittest.TestCase):
    def test_launch_plan_includes_health_monitor_node(self) -> None:
        plan = build_ros2_launch_plan(
            scenario_id="s1_nominal",
            run_id="launch",
            config_id="default",
        )
        node_names = {node["name"] for node in plan["nodes"]}
        self.assertIn("health_monitor_node", node_names)

    def test_validate_rejects_runtime_truth_subscription(self) -> None:
        plan = build_ros2_launch_plan(
            scenario_id="s1_nominal",
            run_id="launch",
            config_id="default",
        )
        for node in plan["nodes"]:
            if node["name"] == "fusion_node":
                node["subscribes"].append("/truth/*")
                break
        with self.assertRaises(ValueError):
            validate_ros2_launch_plan(plan)

    def test_launch_runner_writes_plan_and_matches_baseline(self) -> None:
        baseline_dir = make_temp_dir(self)
        launch_dir = make_temp_dir(self)

        run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=baseline_dir,
            config_path=CONFIG_PATH,
            run_id="baseline",
        )
        summary = run_ros2_launch_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=launch_dir,
            config_path=CONFIG_PATH,
            run_id="launch",
        )

        plan_path = launch_dir / "ros2_launch_plan.json"
        plan_md_path = launch_dir / "ros2_launch_plan.md"
        self.assertTrue(plan_path.exists())
        self.assertTrue(plan_md_path.exists())
        self.assertEqual(summary["scenario_id"], "s1_nominal")
        self.assertEqual(summary["run_id"], "launch")
        self.assertTrue((launch_dir / "s1_nominal_mission_health.json").exists())
        self.assertTrue((launch_dir / "s1_nominal_fault_events.json").exists())

        plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
        validate_ros2_launch_plan(plan_payload)

        replay_result = compare_replay_run(
            scenario_id="s1_nominal",
            original_run_dir=baseline_dir,
            replay_run_dir=launch_dir,
        )
        self.assertEqual(replay_result["replay_result"], "PASS")

    def test_launch_runner_executes_verification_nodes_when_enabled(self) -> None:
        launch_dir = make_temp_dir(self)

        summary = run_ros2_launch_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=launch_dir,
            config_path=CONFIG_PATH,
            run_id="launch-verification",
            verification_nodes_enabled=True,
        )
        self.assertTrue(summary["verification_nodes_enabled"])
        self.assertEqual(summary["verification_node_result"], "PASS")
        self.assertEqual(summary["logger_node_result"], "PASS")
        self.assertEqual(summary["evaluation_node_result"], "PASS")
        self.assertTrue((launch_dir / "s1_nominal_verification_node_results.json").exists())

    def test_launch_file_wrapper_runs_probe(self) -> None:
        launch_dir = make_temp_dir(self)
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = (
            f"{ROOT_DIR / 'src'}{os.pathsep}{existing_pythonpath}"
            if existing_pythonpath
            else str(ROOT_DIR / "src")
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(LAUNCH_FILE),
                str(NOMINAL_SCENARIO),
                "--output-dir",
                str(launch_dir),
                "--config",
                str(CONFIG_PATH),
                "--run-id",
                "launch-file",
            ],
            env=env,
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertTrue((launch_dir / "ros2_launch_plan.json").exists())

    def test_launch_script_repo_wrapper_backend_runs_probe(self) -> None:
        launch_dir = make_temp_dir(self)
        launch_dir_rel = launch_dir.relative_to(ROOT_DIR).as_posix()

        completed = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    "set -euo pipefail; "
                    "PYTHONPATH=src${PYTHONPATH:+:$PYTHONPATH} "
                    "ROS2_LAUNCH_BACKEND=repo_wrapper "
                    "RUN_ID=launch-script "
                    f"bash {LAUNCH_SCRIPT} {NOMINAL_SCENARIO_RELATIVE} {launch_dir_rel}"
                ),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertTrue((launch_dir / "ros2_launch_plan.json").exists())

    def test_launch_script_rejects_invalid_backend(self) -> None:
        launch_dir = make_temp_dir(self)
        launch_dir_rel = launch_dir.relative_to(ROOT_DIR).as_posix()

        completed = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    "set -euo pipefail; "
                    "ROS2_LAUNCH_BACKEND=invalid_backend "
                    "RUN_ID=launch-script-invalid "
                    f"bash {LAUNCH_SCRIPT} {NOMINAL_SCENARIO_RELATIVE} {launch_dir_rel}"
                ),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("Unsupported ROS2_LAUNCH_BACKEND", completed.stderr)

    def test_launch_script_colcon_backend_requires_ros2(self) -> None:
        if shutil.which("ros2") is not None:
            self.skipTest("ros2 is installed; missing-ros2 validation is not applicable.")

        launch_dir = make_temp_dir(self)
        launch_dir_rel = launch_dir.relative_to(ROOT_DIR).as_posix()

        completed = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    "set -euo pipefail; "
                    "ROS2_LAUNCH_BACKEND=colcon "
                    "RUN_ID=launch-script-colcon "
                    f"bash {LAUNCH_SCRIPT} {NOMINAL_SCENARIO_RELATIVE} {launch_dir_rel}"
                ),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("ros2 CLI not found", completed.stderr)

    def test_regression_verification_gate_requires_launch_probe(self) -> None:
        completed = subprocess.run(
            [
                "bash",
                "-lc",
                (
                    "set -euo pipefail; "
                    "ENABLE_ROS2_VERIFICATION_PROBE=true "
                    "bash scripts/run_regression.sh test_gate_guard"
                ),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "ENABLE_ROS2_VERIFICATION_PROBE=true requires ENABLE_ROS2_LAUNCH_PROBE=true",
            completed.stderr,
        )


if __name__ == "__main__":
    unittest.main()
