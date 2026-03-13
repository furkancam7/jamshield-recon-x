"""Tactical summary bundle generation for regression runs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import (
    TACTICAL_SUMMARY_BUNDLE_SCHEMA_VERSION,
    validate_tactical_summary_bundle,
)
from evaluation.regression_compare import load_reports, load_tactical_summaries


def generate_tactical_summary_bundle(
    reports: dict[str, dict[str, Any]],
    tactical_summaries: dict[str, dict[str, Any]],
    regression_result: dict[str, Any],
) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for scenario_id in sorted(reports):
        report = reports[scenario_id]
        tactical_summary = tactical_summaries[scenario_id]
        failed_checks: list[str] = []
        if report["tactical_primary_reason_code"] != tactical_summary["primary_reason_code"]:
            failed_checks.append("primary_reason_mismatch")
        if report["tactical_advisory_code"] != tactical_summary["advisory_code"]:
            failed_checks.append("advisory_code_mismatch")
        if report["tactical_summary_text"] != tactical_summary["summary_text"]:
            failed_checks.append("summary_text_mismatch")

        scenarios.append(
            {
                "scenario_id": scenario_id,
                "mission_state": report["mission_state"],
                "tactical_primary_reason_code": report["tactical_primary_reason_code"],
                "tactical_advisory_code": report["tactical_advisory_code"],
                "tactical_summary_text": report["tactical_summary_text"],
                "tactical_summary_path": report["tactical_summary_path"],
                "failed_checks": failed_checks,
            }
        )

    payload = {
        "schema_version": TACTICAL_SUMMARY_BUNDLE_SCHEMA_VERSION,
        "run_id": regression_result["run_id"],
        "checks_snapshot": regression_result.get("checks", []),
        "scenarios": scenarios,
    }
    validate_tactical_summary_bundle(payload)
    return payload


def write_tactical_summary_bundle_files(
    run_dir: str | Path,
    bundle: dict[str, Any],
) -> tuple[Path, Path, Path]:
    base_path = Path(run_dir)
    json_path = base_path / "tactical_summary_bundle.json"
    md_path = base_path / "tactical_summary_bundle.md"
    csv_path = base_path / "tactical_summary_bundle.csv"

    json_path.write_text(
        json.dumps(bundle, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(bundle), encoding="utf-8")
    _write_csv(csv_path, bundle)
    return json_path, md_path, csv_path


def _write_csv(path: Path, bundle: dict[str, Any]) -> None:
    fieldnames = [
        "scenario_id",
        "mission_state",
        "tactical_primary_reason_code",
        "tactical_advisory_code",
        "tactical_summary_text",
        "tactical_summary_path",
        "failed_checks",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for scenario in bundle["scenarios"]:
            writer.writerow(
                {
                    **scenario,
                    "failed_checks": ",".join(scenario["failed_checks"]),
                }
            )


def _render_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Tactical Summary Bundle",
        "",
        f"- Run ID: `{bundle['run_id']}`",
        "",
        "| Scenario | Mission State | Tactical Reason | Advisory | Failed Checks |",
        "| --- | --- | --- | --- | --- |",
    ]
    for scenario in bundle["scenarios"]:
        lines.append(
            "| {scenario_id} | {mission_state} | {tactical_primary_reason_code} | {tactical_advisory_code} | {failed_checks} |".format(
                **{
                    **scenario,
                    "failed_checks": ", ".join(scenario["failed_checks"]) or "-",
                }
            )
        )
    lines.append("")
    return "\n".join(lines)


def _append_bundle_check(
    regression_result: dict[str, Any],
    bundle_paths: tuple[Path, Path, Path],
) -> dict[str, Any]:
    checks = [
        check
        for check in regression_result.get("checks", [])
        if check["name"] != "tactical_bundle_present"
    ]
    checks.append(
        {
            "name": "tactical_bundle_present",
            "passed": all(path.exists() for path in bundle_paths),
            "detail": (
                "tactical_summary_bundle.json/.md/.csv must all be present."
            ),
        }
    )
    regression_result["checks"] = checks
    regression_result["overall_result"] = (
        "PASS" if all(check["passed"] for check in checks) else "FAIL"
    )
    return regression_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate tactical summary bundle.")
    parser.add_argument("run_dir", help="Directory containing report artifacts.")
    parser.add_argument(
        "--regression-result",
        help="Optional path to regression_result.json to update with tactical bundle check.",
    )
    args = parser.parse_args()

    reports = load_reports(args.run_dir)
    tactical_summaries = load_tactical_summaries(args.run_dir, reports)
    regression_result = (
        json.loads(Path(args.regression_result).read_text(encoding="utf-8"))
        if args.regression_result
        else {"run_id": Path(args.run_dir).name, "checks": [], "overall_result": "PASS"}
    )
    bundle = generate_tactical_summary_bundle(
        reports=reports,
        tactical_summaries=tactical_summaries,
        regression_result=regression_result,
    )
    bundle_paths = write_tactical_summary_bundle_files(args.run_dir, bundle)

    if args.regression_result:
        updated_result = _append_bundle_check(regression_result, bundle_paths)
        Path(args.regression_result).write_text(
            json.dumps(updated_result, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "tactical_summary_bundle_json": str(bundle_paths[0]),
                "tactical_summary_bundle_md": str(bundle_paths[1]),
                "tactical_summary_bundle_csv": str(bundle_paths[2]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
