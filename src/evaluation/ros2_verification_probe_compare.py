"""Comparison helpers for ROS2 verification-node probe artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import (
    ROS2_VERIFICATION_PROBE_RESULTS_SCHEMA_VERSION,
    validate_ros2_verification_probe_results,
)
from logging_replay.replay import compare_replay_run

DEFAULT_ROS2_VERIFICATION_SCENARIOS = ("s1_nominal", "s3_gnss_denied_zone")


def compare_ros2_verification_probe(
    *,
    baseline_run_dir: str | Path,
    verification_run_dir: str | Path,
    scenario_ids: tuple[str, ...] = DEFAULT_ROS2_VERIFICATION_SCENARIOS,
) -> dict[str, Any]:
    baseline_path = Path(baseline_run_dir)
    verification_path = Path(verification_run_dir)

    scenarios: list[dict[str, Any]] = []
    for scenario_id in scenario_ids:
        _assert_runtime_artifacts_exist(baseline_path, scenario_id)
        _assert_runtime_artifacts_exist(verification_path, scenario_id)

        verification_result_path = (
            verification_path / f"{scenario_id}_verification_node_results.json"
        )
        if not verification_result_path.exists():
            raise FileNotFoundError(
                f"Missing verification node result artifact: {verification_result_path}"
            )
        verification_result = json.loads(
            verification_result_path.read_text(encoding="utf-8")
        )
        logger_node_result = verification_result["logger_node"]["result"]
        evaluation_node_result = verification_result["evaluation_node"]["result"]
        failed_checks = list(verification_result["logger_node"]["failed_checks"]) + list(
            verification_result["evaluation_node"]["failed_checks"]
        )

        replay_result = compare_replay_run(
            scenario_id=scenario_id,
            original_run_dir=baseline_path,
            replay_run_dir=verification_path,
        )
        divergence = replay_result["divergence"]
        if replay_result["replay_result"] != "PASS":
            failed_checks.append("launch_parity_diverged")

        probe_result = (
            "PASS"
            if logger_node_result == "PASS"
            and evaluation_node_result == "PASS"
            and replay_result["replay_result"] == "PASS"
            else "FAIL"
        )
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "logger_node_result": logger_node_result,
                "evaluation_node_result": evaluation_node_result,
                "probe_result": probe_result,
                "failed_checks": failed_checks,
                "divergence": divergence,
            }
        )

    overall_result = (
        "PASS"
        if all(scenario["probe_result"] == "PASS" for scenario in scenarios)
        else "FAIL"
    )
    payload = {
        "schema_version": ROS2_VERIFICATION_PROBE_RESULTS_SCHEMA_VERSION,
        "baseline_run_id": baseline_path.name,
        "verification_run_id": verification_path.name,
        "scenario_ids": list(scenario_ids),
        "scenarios": scenarios,
        "overall_result": overall_result,
    }
    validate_ros2_verification_probe_results(payload)
    return payload


def write_ros2_verification_probe_files(
    output_dir: str | Path,
    payload: dict[str, Any],
) -> tuple[Path, Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validate_ros2_verification_probe_results(payload)

    json_path = output_path / "ros2_verification_probe_results.json"
    md_path = output_path / "ros2_verification_probe_results.md"
    csv_path = output_path / "ros2_verification_probe_results.csv"

    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(payload), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario_id",
                "logger_node_result",
                "evaluation_node_result",
                "probe_result",
                "failed_checks",
                "divergence_field",
                "divergence_tick_index",
            ],
        )
        writer.writeheader()
        for scenario in payload["scenarios"]:
            divergence = scenario["divergence"]
            writer.writerow(
                {
                    "scenario_id": scenario["scenario_id"],
                    "logger_node_result": scenario["logger_node_result"],
                    "evaluation_node_result": scenario["evaluation_node_result"],
                    "probe_result": scenario["probe_result"],
                    "failed_checks": ",".join(scenario["failed_checks"]),
                    "divergence_field": (
                        divergence["field_name"] if divergence is not None else ""
                    ),
                    "divergence_tick_index": (
                        divergence["tick_index"] if divergence is not None else ""
                    ),
                }
            )

    return json_path, md_path, csv_path


def _assert_runtime_artifacts_exist(run_dir: Path, scenario_id: str) -> None:
    required = (
        run_dir / f"{scenario_id}_runtime_trace.json",
        run_dir / f"{scenario_id}_mission_audit.json",
        run_dir / f"{scenario_id}_report.json",
        run_dir / f"{scenario_id}_ew_risk_map.json",
        run_dir / f"{scenario_id}_tactical_summary.json",
    )
    for artifact_path in required:
        if not artifact_path.exists():
            raise FileNotFoundError(f"Missing required artifact: {artifact_path}")


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# ROS2 Verification Probe Results",
        "",
        f"- Baseline run: `{payload['baseline_run_id']}`",
        f"- Verification run: `{payload['verification_run_id']}`",
        f"- Overall: `{payload['overall_result']}`",
        "",
        "| Scenario | Logger | Evaluation | Result | Failed Checks | Divergence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for scenario in payload["scenarios"]:
        divergence = scenario["divergence"]
        divergence_field = "-" if divergence is None else divergence["field_name"]
        failed_checks = ", ".join(scenario["failed_checks"]) or "-"
        lines.append(
            "| {scenario_id} | {logger_node_result} | {evaluation_node_result} | {probe_result} | {failed_checks} | {divergence} |".format(
                scenario_id=scenario["scenario_id"],
                logger_node_result=scenario["logger_node_result"],
                evaluation_node_result=scenario["evaluation_node_result"],
                probe_result=scenario["probe_result"],
                failed_checks=failed_checks,
                divergence=divergence_field,
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare verification-node probe outputs against baseline artifacts."
    )
    parser.add_argument("baseline_run_dir", help="Baseline run directory path.")
    parser.add_argument(
        "verification_run_dir", help="Verification-probe run directory path."
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=list(DEFAULT_ROS2_VERIFICATION_SCENARIOS),
        help="Scenario IDs to include in verification probe comparison.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for verification probe files. Defaults to baseline_run_dir.",
    )
    args = parser.parse_args()

    payload = compare_ros2_verification_probe(
        baseline_run_dir=args.baseline_run_dir,
        verification_run_dir=args.verification_run_dir,
        scenario_ids=tuple(args.scenarios),
    )
    output_dir = args.output_dir or args.baseline_run_dir
    paths = write_ros2_verification_probe_files(output_dir, payload)
    print(
        json.dumps(
            {
                "ros2_verification_probe_json": str(paths[0]),
                "ros2_verification_probe_markdown": str(paths[1]),
                "ros2_verification_probe_csv": str(paths[2]),
                "overall_result": payload["overall_result"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
