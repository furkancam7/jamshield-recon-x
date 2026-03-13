"""Calibration bundle generation for trust-engine regression runs."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from common.config import TrustEngineConfig
from common.config import load_app_config
from evaluation.regression_compare import load_reports


def generate_trust_calibration(
    reports: dict[str, dict[str, Any]],
    regression_result: dict[str, Any],
    config: TrustEngineConfig,
) -> dict[str, Any]:
    checks = regression_result.get("checks", [])
    scenarios: list[dict[str, Any]] = []

    for scenario_id in sorted(reports):
        report = reports[scenario_id]
        observed_band = _confidence_band(report["mission_confidence"], config)
        expected_band = _expected_band(report, config)
        failed_checks: list[str] = []
        if observed_band != expected_band:
            failed_checks.append("band_mismatch")
        if not report["trust_primary_reason_code"]:
            failed_checks.append("missing_primary_reason")
        if report["trust_primary_reason_code"] != "trust_inputs_nominal" and not report["trust_reason_codes"]:
            failed_checks.append("missing_supporting_reasons")

        scenarios.append(
            {
                "scenario_id": scenario_id,
                "gnss_trust": report["gnss_trust"],
                "vio_trust": report["vio_trust"],
                "sync_quality": report["sync_quality"],
                "localization_confidence": report["localization_confidence"],
                "mission_confidence": report["mission_confidence"],
                "primary_reason": report["trust_primary_reason_code"],
                "expected_band": expected_band,
                "observed_band": observed_band,
                "failed_checks": failed_checks,
            }
        )

    calibration = {
        "schema_version": "1.0",
        "run_id": regression_result["run_id"],
        "checks_snapshot": checks,
        "scenarios": scenarios,
    }
    return calibration


def write_trust_calibration_files(
    run_dir: str | Path,
    calibration: dict[str, Any],
) -> tuple[Path, Path, Path]:
    base_path = Path(run_dir)
    json_path = base_path / "trust_calibration.json"
    md_path = base_path / "trust_calibration.md"
    csv_path = base_path / "trust_calibration.csv"

    json_path.write_text(
        json.dumps(calibration, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    md_path.write_text(_render_markdown(calibration), encoding="utf-8")
    _write_csv(csv_path, calibration)
    return json_path, md_path, csv_path


def _write_csv(path: Path, calibration: dict[str, Any]) -> None:
    fieldnames = [
        "scenario_id",
        "gnss_trust",
        "vio_trust",
        "sync_quality",
        "localization_confidence",
        "mission_confidence",
        "primary_reason",
        "expected_band",
        "observed_band",
        "failed_checks",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for scenario in calibration["scenarios"]:
            writer.writerow(
                {
                    **scenario,
                    "failed_checks": ",".join(scenario["failed_checks"]),
                }
            )


def _render_markdown(calibration: dict[str, Any]) -> str:
    lines = [
        "# Trust Calibration",
        "",
        f"- Run ID: `{calibration['run_id']}`",
        "",
        "| Scenario | GNSS | VIO | Sync | Loc Conf | Mission Conf | Primary Reason | Expected | Observed | Failed Checks |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for scenario in calibration["scenarios"]:
        lines.append(
            "| {scenario_id} | {gnss_trust:.3f} | {vio_trust:.3f} | {sync_quality:.3f} | {localization_confidence:.3f} | {mission_confidence:.3f} | {primary_reason} | {expected_band} | {observed_band} | {failed_checks} |".format(
                **{
                    **scenario,
                    "failed_checks": ", ".join(scenario["failed_checks"]) or "-",
                }
            )
        )
    lines.append("")
    return "\n".join(lines)


def _confidence_band(value: float, config: TrustEngineConfig) -> str:
    if value >= config.calibration_high_floor:
        return "high"
    if value >= config.calibration_medium_floor:
        return "medium"
    return "low"


def _expected_band(report: dict[str, Any], config: TrustEngineConfig) -> str:
    if report["gnss_state"] == "nominal":
        return "high"
    if report["gnss_state"] == "degraded":
        return "medium"
    if report["effective_vio_state"] == "good":
        return "medium"
    return "low"


def _append_calibration_check(
    regression_result: dict[str, Any],
    calibration_paths: tuple[Path, Path, Path],
) -> dict[str, Any]:
    checks = [
        check
        for check in regression_result.get("checks", [])
        if check["name"] != "calibration_bundle_present"
    ]
    checks.append(
        {
            "name": "calibration_bundle_present",
            "passed": all(path.exists() for path in calibration_paths),
            "detail": "trust_calibration.json/.md/.csv must all be present.",
        }
    )
    regression_result["checks"] = checks
    regression_result["overall_result"] = (
        "PASS" if all(check["passed"] for check in checks) else "FAIL"
    )
    return regression_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate trust calibration bundle.")
    parser.add_argument("run_dir", help="Directory containing report artifacts.")
    parser.add_argument("--config", required=True, help="Path to simulation config.")
    parser.add_argument(
        "--regression-result",
        help="Optional path to regression_result.json to update with calibration check.",
    )
    args = parser.parse_args()

    reports = load_reports(args.run_dir)
    config = load_app_config(args.config)
    regression_result = (
        json.loads(Path(args.regression_result).read_text(encoding="utf-8"))
        if args.regression_result
        else {"run_id": Path(args.run_dir).name, "checks": [], "overall_result": "PASS"}
    )
    calibration = generate_trust_calibration(
        reports=reports,
        regression_result=regression_result,
        config=config.trust_engine,
    )
    calibration_paths = write_trust_calibration_files(args.run_dir, calibration)

    if args.regression_result:
        updated_result = _append_calibration_check(regression_result, calibration_paths)
        Path(args.regression_result).write_text(
            json.dumps(updated_result, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "trust_calibration_json": str(calibration_paths[0]),
                "trust_calibration_md": str(calibration_paths[1]),
                "trust_calibration_csv": str(calibration_paths[2]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
