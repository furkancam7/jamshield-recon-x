"""Regression comparison for the first working vertical slice."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from common.config import MissionConfig, load_app_config
from evaluation.artifact_schema import validate_report

EXPECTED_SCENARIO_IDS = [
    "s1_nominal",
    "s2_gnss_degraded_corridor",
    "s3_gnss_denied_zone",
]


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def load_reports(run_dir: str | Path) -> dict[str, dict[str, Any]]:
    base_path = Path(run_dir)
    reports: dict[str, dict[str, Any]] = {}

    for scenario_id in EXPECTED_SCENARIO_IDS:
        report_path = base_path / f"{scenario_id}_report.json"
        if not report_path.exists():
            raise FileNotFoundError(f"Missing report artifact: {report_path}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        validate_report(report)
        reports[scenario_id] = report

    return reports


def compare_reports(
    reports: dict[str, dict[str, Any]],
    run_id: str,
    mission_config: MissionConfig | None = None,
    nominal_minimum_trust: float = 0.90,
) -> dict[str, Any]:
    nominal = reports["s1_nominal"]
    degraded = reports["s2_gnss_degraded_corridor"]
    denied = reports["s3_gnss_denied_zone"]
    denied_allowed_states = (
        set(mission_config.denied_allowed_states)
        if mission_config
        else {"MISSION_FALLBACK", "MISSION_SAFE_HOLD", "MISSION_EMERGENCY_LAND"}
    )

    checks = [
        CheckResult(
            name="trust_ordering",
            passed=(
                nominal["trust_score"] > degraded["trust_score"] > denied["trust_score"]
            ),
            detail=(
                "Expected nominal trust score > degraded trust score > denied trust score."
            ),
        ),
        CheckResult(
            name="denied_not_normal",
            passed=denied["mission_state"] != "MISSION_NORMAL",
            detail="Denied scenario must not end in MISSION_NORMAL.",
        ),
        CheckResult(
            name="degraded_not_denied",
            passed=degraded["gnss_state"] != "denied",
            detail="Degraded scenario must not be classified as denied.",
        ),
        CheckResult(
            name="nominal_not_emergency",
            passed=nominal["mission_state"] != "MISSION_EMERGENCY_LAND",
            detail="Nominal scenario must not collapse to MISSION_EMERGENCY_LAND.",
        ),
        CheckResult(
            name="nominal_minimum_trust_threshold",
            passed=nominal["trust_score"] >= nominal_minimum_trust,
            detail=(
                f"Nominal scenario trust score must remain at or above {nominal_minimum_trust:.2f}."
            ),
        ),
        CheckResult(
            name="denied_allowed_mission_states",
            passed=denied["mission_state"] in denied_allowed_states,
            detail="Denied scenario must end in the allowed denied-state set.",
        ),
    ]

    overall_passed = all(check.passed for check in checks)

    return {
        "run_id": run_id,
        "scenario_ids": EXPECTED_SCENARIO_IDS,
        "checks": [asdict(check) for check in checks],
        "overall_result": "PASS" if overall_passed else "FAIL",
    }


def write_regression_result(output_path: str | Path, result: dict[str, Any]) -> Path:
    target_path = Path(output_path)
    target_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline scenario artifacts.")
    parser.add_argument("run_dir", help="Directory containing scenario report artifacts.")
    parser.add_argument(
        "--output",
        help="Optional path for regression_result.json.",
    )
    parser.add_argument(
        "--config",
        help="Optional path to the simulation config file.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    reports = load_reports(run_dir)
    config = load_app_config(args.config) if args.config else None
    result = compare_reports(
        reports,
        run_id=run_dir.name,
        mission_config=config.mission if config else None,
    )

    if args.output:
        write_regression_result(args.output, result)

    print(json.dumps(result, indent=2))
    return 0 if result["overall_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
