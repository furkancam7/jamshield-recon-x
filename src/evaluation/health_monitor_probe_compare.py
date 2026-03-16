"""Comparison helpers for health-monitor probe artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import (
    HEALTH_MONITOR_PROBE_RESULTS_SCHEMA_VERSION,
    validate_fault_events,
    validate_health_monitor_probe_results,
    validate_mission_health_timeline,
)
from logging_replay.replay import compare_replay_run

DEFAULT_HEALTH_MONITOR_SCENARIOS = ("s1_nominal", "s13_sync_low_nominal")
_SEVERITY_RANK = {"nominal": 0, "warning": 1, "critical": 2}


def compare_health_monitor_probe(
    *,
    baseline_run_dir: str | Path,
    health_probe_run_dir: str | Path,
    scenario_ids: tuple[str, ...] = DEFAULT_HEALTH_MONITOR_SCENARIOS,
) -> dict[str, Any]:
    baseline_path = Path(baseline_run_dir)
    health_probe_path = Path(health_probe_run_dir)

    scenarios: list[dict[str, Any]] = []
    for scenario_id in scenario_ids:
        _assert_runtime_artifacts_exist(baseline_path, scenario_id)
        _assert_runtime_artifacts_exist(health_probe_path, scenario_id)

        failed_checks: list[str] = []
        health_payload, fault_payload, health_checks = _validate_health_artifacts(
            health_probe_path,
            scenario_id,
        )
        failed_checks.extend(health_checks)
        health_artifact_result = "PASS" if not health_checks else "FAIL"

        replay_result = compare_replay_run(
            scenario_id=scenario_id,
            original_run_dir=baseline_path,
            replay_run_dir=health_probe_path,
        )
        parity_result = "PASS" if replay_result["replay_result"] == "PASS" else "FAIL"
        if parity_result != "PASS":
            failed_checks.append("launch_parity_diverged")

        probe_result = (
            "PASS"
            if health_artifact_result == "PASS" and parity_result == "PASS"
            else "FAIL"
        )
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "health_artifact_result": health_artifact_result,
                "parity_result": parity_result,
                "probe_result": probe_result,
                "failed_checks": failed_checks,
                "divergence": replay_result["divergence"],
                "health_entry_count": (
                    len(health_payload["entries"]) if health_payload is not None else 0
                ),
                "fault_event_count": (
                    len(fault_payload["events"]) if fault_payload is not None else 0
                ),
                "max_health_severity": _resolve_max_severity(health_payload),
            }
        )

    overall_result = (
        "PASS"
        if all(scenario["probe_result"] == "PASS" for scenario in scenarios)
        else "FAIL"
    )
    payload = {
        "schema_version": HEALTH_MONITOR_PROBE_RESULTS_SCHEMA_VERSION,
        "baseline_run_id": baseline_path.name,
        "health_probe_run_id": health_probe_path.name,
        "scenario_ids": list(scenario_ids),
        "scenarios": scenarios,
        "overall_result": overall_result,
    }
    validate_health_monitor_probe_results(payload)
    return payload


def write_health_monitor_probe_files(
    output_dir: str | Path,
    payload: dict[str, Any],
) -> tuple[Path, Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    validate_health_monitor_probe_results(payload)

    json_path = output_path / "health_monitor_probe_results.json"
    md_path = output_path / "health_monitor_probe_results.md"
    csv_path = output_path / "health_monitor_probe_results.csv"

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
                "health_artifact_result",
                "parity_result",
                "probe_result",
                "health_entry_count",
                "fault_event_count",
                "max_health_severity",
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
                    "health_artifact_result": scenario["health_artifact_result"],
                    "parity_result": scenario["parity_result"],
                    "probe_result": scenario["probe_result"],
                    "health_entry_count": scenario["health_entry_count"],
                    "fault_event_count": scenario["fault_event_count"],
                    "max_health_severity": scenario["max_health_severity"],
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


def _validate_health_artifacts(
    run_dir: Path,
    scenario_id: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    failed_checks: list[str] = []
    health_payload: dict[str, Any] | None = None
    fault_payload: dict[str, Any] | None = None

    health_path = run_dir / f"{scenario_id}_mission_health.json"
    if not health_path.exists():
        failed_checks.append("mission_health_missing")
    else:
        try:
            health_payload = json.loads(health_path.read_text(encoding="utf-8"))
            validate_mission_health_timeline(health_payload)
            if not health_payload["entries"]:
                failed_checks.append("mission_health_empty")
        except Exception:  # noqa: BLE001 - surfaced through failed_checks
            failed_checks.append("mission_health_invalid")

    faults_path = run_dir / f"{scenario_id}_fault_events.json"
    if not faults_path.exists():
        failed_checks.append("fault_events_missing")
    else:
        try:
            fault_payload = json.loads(faults_path.read_text(encoding="utf-8"))
            validate_fault_events(fault_payload)
        except Exception:  # noqa: BLE001 - surfaced through failed_checks
            failed_checks.append("fault_events_invalid")

    return health_payload, fault_payload, failed_checks


def _resolve_max_severity(health_payload: dict[str, Any] | None) -> str:
    if health_payload is None:
        return "unknown"
    max_rank = 0
    for entry in health_payload["entries"]:
        max_rank = max(max_rank, _SEVERITY_RANK.get(entry["severity"], 0))
    for severity, rank in _SEVERITY_RANK.items():
        if rank == max_rank:
            return severity
    return "nominal"


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
        "# Health Monitor Probe Results",
        "",
        f"- Baseline run: `{payload['baseline_run_id']}`",
        f"- Health probe run: `{payload['health_probe_run_id']}`",
        f"- Overall: `{payload['overall_result']}`",
        "",
        "| Scenario | Health Artifacts | Parity | Result | Max Severity | Fault Events | Failed Checks | Divergence |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for scenario in payload["scenarios"]:
        divergence = scenario["divergence"]
        divergence_field = "-" if divergence is None else divergence["field_name"]
        failed_checks = ", ".join(scenario["failed_checks"]) or "-"
        lines.append(
            "| {scenario_id} | {health_artifact_result} | {parity_result} | {probe_result} | {max_severity} | {fault_events} | {failed_checks} | {divergence} |".format(
                scenario_id=scenario["scenario_id"],
                health_artifact_result=scenario["health_artifact_result"],
                parity_result=scenario["parity_result"],
                probe_result=scenario["probe_result"],
                max_severity=scenario["max_health_severity"],
                fault_events=scenario["fault_event_count"],
                failed_checks=failed_checks,
                divergence=divergence_field,
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare health-monitor probe outputs against baseline artifacts."
    )
    parser.add_argument("baseline_run_dir", help="Baseline run directory path.")
    parser.add_argument(
        "health_probe_run_dir", help="Health-monitor probe run directory path."
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=list(DEFAULT_HEALTH_MONITOR_SCENARIOS),
        help="Scenario IDs to include in health-monitor probe comparison.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for health-monitor probe files. Defaults to baseline_run_dir.",
    )
    args = parser.parse_args()

    payload = compare_health_monitor_probe(
        baseline_run_dir=args.baseline_run_dir,
        health_probe_run_dir=args.health_probe_run_dir,
        scenario_ids=tuple(args.scenarios),
    )
    output_dir = args.output_dir or args.baseline_run_dir
    paths = write_health_monitor_probe_files(output_dir, payload)
    print(
        json.dumps(
            {
                "health_monitor_probe_json": str(paths[0]),
                "health_monitor_probe_markdown": str(paths[1]),
                "health_monitor_probe_csv": str(paths[2]),
                "overall_result": payload["overall_result"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
