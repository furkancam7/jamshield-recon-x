"""Parity comparison between file-based and node-oriented runtime outputs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import (
    NODE_PARITY_RESULTS_SCHEMA_VERSION,
    validate_node_parity_results,
)
from logging_replay.replay import compare_replay_run

DEFAULT_PARITY_SCENARIOS = ("s1_nominal", "s3_gnss_denied_zone")


def compare_node_parity(
    *,
    baseline_run_dir: str | Path,
    node_run_dir: str | Path,
    scenario_ids: tuple[str, ...] = DEFAULT_PARITY_SCENARIOS,
) -> dict[str, Any]:
    baseline_path = Path(baseline_run_dir)
    node_path = Path(node_run_dir)

    scenarios: list[dict[str, Any]] = []
    for scenario_id in scenario_ids:
        _assert_artifacts_exist(baseline_path, scenario_id)
        _assert_artifacts_exist(node_path, scenario_id)
        replay_result = compare_replay_run(
            scenario_id=scenario_id,
            original_run_dir=baseline_path,
            replay_run_dir=node_path,
        )
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "parity_result": replay_result["replay_result"],
                "divergence": replay_result["divergence"],
            }
        )

    overall_result = (
        "PASS"
        if all(scenario["parity_result"] == "PASS" for scenario in scenarios)
        else "FAIL"
    )
    return {
        "schema_version": NODE_PARITY_RESULTS_SCHEMA_VERSION,
        "baseline_run_id": baseline_path.name,
        "node_run_id": node_path.name,
        "scenario_ids": list(scenario_ids),
        "scenarios": scenarios,
        "overall_result": overall_result,
    }


def write_node_parity_files(
    output_dir: str | Path,
    payload: dict[str, Any],
) -> tuple[Path, Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validate_node_parity_results(payload)
    json_path = output_path / "node_parity_results.json"
    md_path = output_path / "node_parity_results.md"
    csv_path = output_path / "node_parity_results.csv"

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
                "parity_result",
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
                    "parity_result": scenario["parity_result"],
                    "divergence_field": (
                        divergence["field_name"] if divergence is not None else ""
                    ),
                    "divergence_tick_index": (
                        divergence["tick_index"] if divergence is not None else ""
                    ),
                }
            )

    return json_path, md_path, csv_path


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Node Parity Results",
        "",
        f"- Baseline run: `{payload['baseline_run_id']}`",
        f"- Node run: `{payload['node_run_id']}`",
        f"- Overall: `{payload['overall_result']}`",
        "",
        "| Scenario | Result | Divergence |",
        "| --- | --- | --- |",
    ]
    for scenario in payload["scenarios"]:
        divergence = scenario["divergence"]
        divergence_field = "-" if divergence is None else divergence["field_name"]
        lines.append(
            f"| {scenario['scenario_id']} | {scenario['parity_result']} | {divergence_field} |"
        )
    lines.append("")
    return "\n".join(lines)


def _assert_artifacts_exist(run_dir: Path, scenario_id: str) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare node runtime artifacts against a file-based baseline run."
    )
    parser.add_argument("baseline_run_dir", help="Baseline run directory path.")
    parser.add_argument("node_run_dir", help="Node run directory path.")
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=list(DEFAULT_PARITY_SCENARIOS),
        help="Scenario IDs to include in parity comparison.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for node parity files. Defaults to node_run_dir.",
    )
    args = parser.parse_args()

    payload = compare_node_parity(
        baseline_run_dir=args.baseline_run_dir,
        node_run_dir=args.node_run_dir,
        scenario_ids=tuple(args.scenarios),
    )
    output_dir = args.output_dir or args.node_run_dir
    paths = write_node_parity_files(output_dir, payload)
    print(
        json.dumps(
            {
                "node_parity_json": str(paths[0]),
                "node_parity_markdown": str(paths[1]),
                "node_parity_csv": str(paths[2]),
                "overall_result": payload["overall_result"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
