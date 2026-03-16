"""ROS2 launch-wired runtime probe for Phase 12 migration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common.runtime_metadata import utc_timestamp
from runtime.node_runner import (
    FORBIDDEN_RUNTIME_TOPIC_FAMILIES,
    MISSION_DECISION_AUTHORITY,
    RUNTIME_TOPIC_FAMILIES,
    run_node_scenario,
)
from runtime.verification_nodes import run_verification_nodes_probe

LAUNCH_PLAN_SCHEMA_VERSION = "1.0"
RUNTIME_ROLE = "runtime_autonomy"
TACTICAL_ROLE = "tactical_intelligence"
VERIFICATION_ROLE = "verification"
OPERATOR_ROLE = "operator_interface"
MISSION_DECISION_TOPICS = {"/mission/state", "/mission/action", "/mission/explanation"}
MISSION_DECISION_NODE = "mission_continuity_node"


def build_ros2_launch_plan(
    *,
    scenario_id: str,
    run_id: str,
    config_id: str,
    verification_nodes_enabled: bool = False,
) -> dict[str, Any]:
    """Builds a launch-wiring plan for the node-oriented runtime probe."""

    return {
        "schema_version": LAUNCH_PLAN_SCHEMA_VERSION,
        "generated_at": utc_timestamp(),
        "scenario_id": scenario_id,
        "run_id": run_id,
        "config_id": config_id,
        "runtime_entrypoint": "runtime.node_runner",
        "launch_entrypoint": "launch/runtime_probe.launch.py",
        "runtime_topic_families": list(RUNTIME_TOPIC_FAMILIES),
        "forbidden_runtime_topic_families": list(FORBIDDEN_RUNTIME_TOPIC_FAMILIES),
        "mission_decision_authority": MISSION_DECISION_AUTHORITY,
        "nodes": [
            {
                "name": "scenario_orchestrator_node",
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": ["/events/*"],
                "subscribes": [],
            },
            {
                "name": "vio_node",
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": ["/localization/vio/estimate"],
                "subscribes": ["/sensors/*", "/sync/*"],
            },
            {
                "name": "gnss_trust_node",
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": ["/trust/gnss/value"],
                "subscribes": ["/sensors/gnss/fix", "/sync/*", "/localization/vio/estimate"],
            },
            {
                "name": "fusion_node",
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": ["/localization/fused/estimate", "/localization/source_status"],
                "subscribes": ["/localization/*", "/trust/*", "/sync/*"],
            },
            {
                "name": "trust_engine_node",
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": ["/trust/localization/confidence", "/trust/mission_confidence"],
                "subscribes": ["/trust/*", "/localization/*", "/mission/health"],
            },
            {
                "name": MISSION_DECISION_NODE,
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": sorted(MISSION_DECISION_TOPICS),
                "subscribes": ["/localization/*", "/trust/*", "/events/*", "/mission/health"],
            },
            {
                "name": "health_monitor_node",
                "role": RUNTIME_ROLE,
                "enabled": True,
                "publishes": ["/mission/health", "/events/faults"],
                "subscribes": ["/sync/*", "/localization/*", "/trust/*", "/mission/*"],
            },
            {
                "name": "ew_risk_map_node",
                "role": TACTICAL_ROLE,
                "enabled": True,
                "publishes": ["/tactical/ew_risk_map"],
                "subscribes": ["/trust/*", "/localization/*", "/events/*"],
            },
            {
                "name": "tactical_summary_node",
                "role": TACTICAL_ROLE,
                "enabled": True,
                "publishes": ["/tactical/summary"],
                "subscribes": ["/tactical/*", "/mission/*", "/trust/*", "/mission/health"],
            },
            {
                "name": "logger_node",
                "role": VERIFICATION_ROLE,
                "enabled": verification_nodes_enabled,
                "publishes": [],
                "subscribes": ["/events/*", "/sensors/*", "/sync/*", "/localization/*", "/trust/*", "/mission/*", "/tactical/*", "/truth/*"],
            },
            {
                "name": "evaluation_node",
                "role": VERIFICATION_ROLE,
                "enabled": verification_nodes_enabled,
                "publishes": ["/evaluation/*"],
                "subscribes": ["/truth/*"],
            },
            {
                "name": "operator_station_node",
                "role": OPERATOR_ROLE,
                "enabled": True,
                "publishes": [],
                "subscribes": ["/mission/*", "/tactical/*", "/evaluation/*"],
            },
        ],
    }


def validate_ros2_launch_plan(plan: dict[str, Any]) -> None:
    """Validates launch wiring constraints for the Phase 12 probe."""

    required_fields = {
        "schema_version",
        "generated_at",
        "scenario_id",
        "run_id",
        "config_id",
        "runtime_entrypoint",
        "launch_entrypoint",
        "runtime_topic_families",
        "forbidden_runtime_topic_families",
        "mission_decision_authority",
        "nodes",
    }
    missing = required_fields.difference(plan)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"ROS2 launch plan missing required fields: {missing_list}")

    if plan["schema_version"] != LAUNCH_PLAN_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported ROS2 launch plan schema_version: {plan['schema_version']}"
        )
    if plan["mission_decision_authority"] != MISSION_DECISION_NODE:
        raise ValueError(
            "mission_continuity_node must remain the sole mission decision authority."
        )

    runtime_families = plan["runtime_topic_families"]
    forbidden_families = plan["forbidden_runtime_topic_families"]
    if not isinstance(runtime_families, list) or not isinstance(forbidden_families, list):
        raise ValueError("runtime_topic_families and forbidden_runtime_topic_families must be lists.")
    if set(runtime_families).intersection(set(forbidden_families)):
        raise ValueError("Runtime topic families must not overlap forbidden topic families.")

    nodes = plan["nodes"]
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("nodes must be a non-empty list.")

    mission_decision_publishers: set[str] = set()
    forbidden_set = set(forbidden_families)
    for node in nodes:
        _validate_node_entry(node)
        node_name = node["name"]
        publishes = set(node["publishes"])
        subscribes = set(node["subscribes"])
        role = node["role"]

        if role == RUNTIME_ROLE and subscribes.intersection(forbidden_set):
            overlap = ", ".join(sorted(subscribes.intersection(forbidden_set)))
            raise ValueError(
                f"Runtime node {node_name} subscribes to forbidden families: {overlap}"
            )
        if MISSION_DECISION_TOPICS.intersection(publishes):
            mission_decision_publishers.add(node_name)

    if mission_decision_publishers != {MISSION_DECISION_NODE}:
        publishers = ", ".join(sorted(mission_decision_publishers)) or "<none>"
        raise ValueError(
            "Mission decision topics must be published only by mission_continuity_node. "
            f"Observed publishers: {publishers}"
        )


def write_ros2_launch_plan(
    output_dir: str | Path,
    plan: dict[str, Any],
) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validate_ros2_launch_plan(plan)

    json_path = output_path / "ros2_launch_plan.json"
    md_path = output_path / "ros2_launch_plan.md"

    json_path.write_text(
        json.dumps(plan, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(_render_launch_markdown(plan), encoding="utf-8")
    return json_path, md_path


def run_ros2_launch_scenario(
    scenario_path: str | Path,
    output_dir: str | Path,
    *,
    config_path: str | Path,
    config_override_path: str | Path | None = None,
    run_id: str | None = None,
    vio_state: str | None = None,
    vio_health_score: float | None = None,
    verification_nodes_enabled: bool = False,
) -> dict[str, Any]:
    """Runs a scenario via launch-wired node runtime probe and writes launch plan artifacts."""

    summary = run_node_scenario(
        scenario_path=scenario_path,
        output_dir=output_dir,
        config_path=config_path,
        config_override_path=config_override_path,
        run_id=run_id,
        vio_state=vio_state,
        vio_health_score=vio_health_score,
    )
    plan = build_ros2_launch_plan(
        scenario_id=str(summary["scenario_id"]),
        run_id=str(summary["run_id"]),
        config_id=str(summary["config_id"]),
        verification_nodes_enabled=verification_nodes_enabled,
    )
    plan_json_path, plan_md_path = write_ros2_launch_plan(output_dir, plan)
    summary["ros2_launch_plan_path"] = str(plan_json_path)
    summary["ros2_launch_plan_markdown_path"] = str(plan_md_path)
    if verification_nodes_enabled:
        verification_summary = run_verification_nodes_probe(
            scenario_id=str(summary["scenario_id"]),
            scenario_path=scenario_path,
            run_dir=output_dir,
            sim_config_path=config_path,
        )
        summary["verification_nodes_enabled"] = True
        summary["verification_node_result"] = verification_summary["overall_result"]
        summary["verification_node_results_path"] = verification_summary["artifact_path"]
        summary["logger_node_result"] = verification_summary["logger_node"]["result"]
        summary["evaluation_node_result"] = verification_summary["evaluation_node"]["result"]
    else:
        summary["verification_nodes_enabled"] = False
    return summary


def _render_launch_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# ROS2 Launch Plan",
        "",
        f"- Run: `{plan['run_id']}`",
        f"- Scenario: `{plan['scenario_id']}`",
        f"- Config: `{plan['config_id']}`",
        f"- Decision authority: `{plan['mission_decision_authority']}`",
        "",
        "| Node | Role | Enabled |",
        "| --- | --- | --- |",
    ]
    for node in plan["nodes"]:
        lines.append(f"| {node['name']} | {node['role']} | {node['enabled']} |")
    lines.append("")
    return "\n".join(lines)


def _validate_node_entry(node: Any) -> None:
    if not isinstance(node, dict):
        raise ValueError("Each node entry must be a mapping.")
    required = {"name", "role", "enabled", "publishes", "subscribes"}
    missing = required.difference(node)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Node entry missing required fields: {missing_list}")
    if not isinstance(node["name"], str) or not node["name"].strip():
        raise ValueError("Node entry name must be a non-empty string.")
    if node["role"] not in {RUNTIME_ROLE, TACTICAL_ROLE, VERIFICATION_ROLE, OPERATOR_ROLE}:
        raise ValueError(f"Unsupported node role: {node['role']}")
    if not isinstance(node["enabled"], bool):
        raise ValueError("Node enabled must be a boolean.")
    if not isinstance(node["publishes"], list) or not all(
        isinstance(topic, str) and topic.strip() for topic in node["publishes"]
    ):
        raise ValueError("Node publishes must be a list of non-empty topic strings.")
    if not isinstance(node["subscribes"], list) or not all(
        isinstance(topic, str) and topic.strip() for topic in node["subscribes"]
    ):
        raise ValueError("Node subscribes must be a list of non-empty topic strings.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the ROS2 launch-wired runtime probe for Phase 12 migration."
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
        help="Enable hybrid logger/evaluation verification-node execution for the probe run.",
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
