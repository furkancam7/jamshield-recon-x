#!/usr/bin/env python3
"""ROS2 launch entrypoint for the Phase 12 runtime probe."""

from __future__ import annotations

import sys
from typing import Any

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import LaunchConfiguration


def _build_runtime_probe_process(context: Any) -> list[ExecuteProcess]:
    scenario_path = LaunchConfiguration("scenario_path").perform(context).strip()
    output_dir = LaunchConfiguration("output_dir").perform(context).strip()
    config_path = LaunchConfiguration("config_path").perform(context).strip()
    run_id = LaunchConfiguration("run_id").perform(context).strip()
    enable_verification_nodes = (
        LaunchConfiguration("enable_verification_nodes").perform(context).strip().lower()
    )
    vio_state = LaunchConfiguration("vio_state").perform(context).strip()
    vio_health_score = LaunchConfiguration("vio_health_score").perform(context).strip()
    vio_unhealthy = LaunchConfiguration("vio_unhealthy").perform(context).strip().lower()

    if not scenario_path:
        raise RuntimeError("scenario_path launch argument must be a non-empty string.")
    if not config_path:
        raise RuntimeError("config_path launch argument must be a non-empty string.")

    cmd = [
        sys.executable,
        "-m",
        "runtime.ros2_launch_runner",
        scenario_path,
        "--output-dir",
        output_dir or "artifacts",
        "--config",
        config_path,
        "--run-id",
        run_id or "ros2-launch-probe",
    ]

    if enable_verification_nodes == "true":
        cmd.append("--enable-verification-nodes")
    if vio_unhealthy == "true":
        cmd.append("--vio-unhealthy")
    else:
        if vio_state:
            cmd.extend(["--vio-state", vio_state])
        if vio_health_score:
            cmd.extend(["--vio-health-score", vio_health_score])

    return [ExecuteProcess(cmd=cmd, output="screen")]


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "scenario_path",
                default_value="",
                description="Path to the scenario YAML file.",
            ),
            DeclareLaunchArgument(
                "output_dir",
                default_value="artifacts",
                description="Directory where runtime-probe artifacts will be written.",
            ),
            DeclareLaunchArgument(
                "config_path",
                default_value="configs/sim/default.yaml",
                description="Path to the simulation config file.",
            ),
            DeclareLaunchArgument(
                "run_id",
                default_value="",
                description="Optional run identifier written into generated artifacts.",
            ),
            DeclareLaunchArgument(
                "enable_verification_nodes",
                default_value="false",
                description="Enable hybrid logger/evaluation verification-node execution.",
            ),
            DeclareLaunchArgument(
                "vio_state",
                default_value="",
                description="Optional categorical VIO state override.",
            ),
            DeclareLaunchArgument(
                "vio_health_score",
                default_value="",
                description="Optional continuous VIO health score override.",
            ),
            DeclareLaunchArgument(
                "vio_unhealthy",
                default_value="false",
                description="Set true to force vio_state=lost and vio_health_score=0.0.",
            ),
            OpaqueFunction(function=_build_runtime_probe_process),
        ]
    )
