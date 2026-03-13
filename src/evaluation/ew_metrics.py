"""EW risk-map metrics bundle generation for regression runs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import EW_METRICS_SCHEMA_VERSION, validate_ew_metrics_bundle
from evaluation.regression_compare import load_ew_risk_maps, load_reports


def generate_ew_metrics_bundle(
    reports: dict[str, dict[str, Any]],
    ew_risk_maps: dict[str, dict[str, Any]],
    regression_result: dict[str, Any],
) -> dict[str, Any]:
    scenarios: list[dict[str, Any]] = []
    for scenario_id in sorted(reports):
        report = reports[scenario_id]
        ew_map = ew_risk_maps[scenario_id]
        failed_checks: list[str] = []
        if report["ew_primary_reason_code"] != ew_map["primary_reason_code"]:
            failed_checks.append("primary_reason_mismatch")
        if round(report["ew_max_risk"], 3) != round(ew_map["max_risk"], 3):
            failed_checks.append("max_risk_mismatch")
        if report["ew_affected_cell_count"] != ew_map["affected_cell_count"]:
            failed_checks.append("affected_cell_count_mismatch")
        if round(report["ew_corridor_cost"], 3) != round(ew_map["corridor_cost"], 3):
            failed_checks.append("corridor_cost_mismatch")

        scenarios.append(
            {
                "scenario_id": scenario_id,
                "ew_risk_level": report["ew_risk_level"],
                "max_risk": report["ew_max_risk"],
                "affected_cell_count": report["ew_affected_cell_count"],
                "corridor_cost": report["ew_corridor_cost"],
                "primary_reason_code": report["ew_primary_reason_code"],
                "risk_cells_hash": ew_map["risk_cells_hash"],
                "failed_checks": failed_checks,
            }
        )

    payload = {
        "schema_version": EW_METRICS_SCHEMA_VERSION,
        "run_id": regression_result["run_id"],
        "checks_snapshot": regression_result.get("checks", []),
        "scenarios": scenarios,
    }
    validate_ew_metrics_bundle(payload)
    return payload


def write_ew_metrics_files(
    run_dir: str | Path,
    bundle: dict[str, Any],
) -> tuple[Path, Path, Path]:
    base_path = Path(run_dir)
    json_path = base_path / "ew_metrics.json"
    md_path = base_path / "ew_metrics.md"
    csv_path = base_path / "ew_metrics.csv"

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
        "ew_risk_level",
        "max_risk",
        "affected_cell_count",
        "corridor_cost",
        "primary_reason_code",
        "risk_cells_hash",
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
        "# EW Metrics",
        "",
        f"- Run ID: `{bundle['run_id']}`",
        "",
        "| Scenario | EW Level | Max Risk | Cells | Corridor Cost | Primary Reason | Failed Checks |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for scenario in bundle["scenarios"]:
        lines.append(
            "| {scenario_id} | {ew_risk_level} | {max_risk:.3f} | {affected_cell_count} | {corridor_cost:.3f} | {primary_reason_code} | {failed_checks} |".format(
                **{
                    **scenario,
                    "failed_checks": ", ".join(scenario["failed_checks"]) or "-",
                }
            )
        )
    lines.append("")
    return "\n".join(lines)


def _append_ew_metrics_check(
    regression_result: dict[str, Any],
    bundle_paths: tuple[Path, Path, Path],
) -> dict[str, Any]:
    checks = [
        check
        for check in regression_result.get("checks", [])
        if check["name"] != "ew_metrics_bundle_present"
    ]
    checks.append(
        {
            "name": "ew_metrics_bundle_present",
            "passed": all(path.exists() for path in bundle_paths),
            "detail": "ew_metrics.json/.md/.csv must all be present.",
        }
    )
    regression_result["checks"] = checks
    regression_result["overall_result"] = (
        "PASS" if all(check["passed"] for check in checks) else "FAIL"
    )
    return regression_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate EW metrics bundle.")
    parser.add_argument("run_dir", help="Directory containing report artifacts.")
    parser.add_argument(
        "--regression-result",
        help="Optional path to regression_result.json to update with EW metrics check.",
    )
    args = parser.parse_args()

    reports = load_reports(args.run_dir)
    ew_risk_maps = load_ew_risk_maps(args.run_dir, reports)
    regression_result = (
        json.loads(Path(args.regression_result).read_text(encoding="utf-8"))
        if args.regression_result
        else {"run_id": Path(args.run_dir).name, "checks": [], "overall_result": "PASS"}
    )
    bundle = generate_ew_metrics_bundle(
        reports=reports,
        ew_risk_maps=ew_risk_maps,
        regression_result=regression_result,
    )
    bundle_paths = write_ew_metrics_files(args.run_dir, bundle)

    if args.regression_result:
        updated_result = _append_ew_metrics_check(regression_result, bundle_paths)
        Path(args.regression_result).write_text(
            json.dumps(updated_result, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "ew_metrics_json": str(bundle_paths[0]),
                "ew_metrics_md": str(bundle_paths[1]),
                "ew_metrics_csv": str(bundle_paths[2]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
