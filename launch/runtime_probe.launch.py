#!/usr/bin/env python3
"""Repo-local launch entrypoint for the Phase 12 runtime probe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from runtime.ros2_launch_runner import run_ros2_launch_scenario


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Phase 12 runtime probe through launch/runtime_probe.launch.py."
    )
    parser.add_argument("scenario", help="Path to the scenario YAML file.")
    parser.add_argument(
        "--output-dir",
        default="artifacts",
        help="Directory where node and launch-plan artifacts will be written.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to the simulation config file.",
    )
    parser.add_argument(
        "--config-override",
        help="Optional CLI override config applied after any scenario override.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run identifier written into node artifacts.",
    )
    parser.add_argument(
        "--vio-state",
        choices=["good", "weak", "lost"],
        help="Legacy categorical VIO health override.",
    )
    parser.add_argument(
        "--vio-health-score",
        type=float,
        help="Legacy continuous VIO health override (0.0-1.0).",
    )
    parser.add_argument(
        "--vio-unhealthy",
        action="store_true",
        help="(Deprecated) Sets vio_state=lost and vio_health_score=0.0.",
    )
    parser.add_argument(
        "--enable-verification-nodes",
        action="store_true",
        help="Enable hybrid logger/evaluation verification-node execution for this probe run.",
    )
    args = parser.parse_args()

    vio_state = args.vio_state
    vio_health_score = args.vio_health_score
    if args.vio_unhealthy:
        vio_state = "lost"
        vio_health_score = 0.0

    summary = run_ros2_launch_scenario(
        scenario_path=args.scenario,
        output_dir=args.output_dir,
        config_path=args.config,
        config_override_path=args.config_override,
        run_id=args.run_id,
        vio_state=vio_state,
        vio_health_score=vio_health_score,
        verification_nodes_enabled=args.enable_verification_nodes,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
