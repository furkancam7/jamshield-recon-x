"""Deterministic replay and offline evaluation bundle generation."""

from __future__ import annotations

import argparse
import csv
import json
from math import sqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from evaluation.artifact_schema import (
    EVALUATION_METRICS_SCHEMA_VERSION,
    EVALUATION_VERDICTS_SCHEMA_VERSION,
    REPLAY_RESULTS_SCHEMA_VERSION,
    validate_evaluation_metrics_bundle,
    validate_evaluation_verdicts_bundle,
    validate_replay_results_bundle,
)
from evaluation.profiles import DEFAULT_EVAL_CONFIG_PATH, EvaluationProfile, load_evaluation_profiles
from evaluation.regression_compare import EXPECTED_SCENARIO_IDS, load_reports
from logging_replay.replay import compare_replay_run


def run_replay_and_evaluation(
    run_dir: str | Path,
    *,
    sim_config_path: str | Path,
    eval_config_path: str | Path = DEFAULT_EVAL_CONFIG_PATH,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    base_path = Path(run_dir)
    reports = load_reports(base_path)
    profiles = load_evaluation_profiles(eval_config_path)

    replay_scenarios: list[dict[str, Any]] = []
    metrics_scenarios: list[dict[str, Any]] = []
    verdict_scenarios: list[dict[str, Any]] = []

    for scenario_id in EXPECTED_SCENARIO_IDS:
        manifest_path = _resolve_manifest_path(scenario_id)
        profile_name = reports[scenario_id]["evaluation_profile"]
        if profile_name not in profiles:
            replay_result = {
                "scenario_id": scenario_id,
                "replay_result": "INVALID",
                "divergence": {
                    "tick_index": None,
                    "field_name": "evaluation_profile",
                    "original_value": profile_name,
                    "replay_value": None,
                },
            }
        else:
            with TemporaryDirectory(prefix=f"{scenario_id}_replay_") as replay_dir:
                from scenario_orchestrator.main import run_scenario

                run_scenario(
                    scenario_path=manifest_path,
                    output_dir=replay_dir,
                    config_path=sim_config_path,
                    run_id="replay_validation",
                )
                replay_result = compare_replay_run(
                    scenario_id=scenario_id,
                    original_run_dir=base_path,
                    replay_run_dir=replay_dir,
                )
        replay_scenarios.append(replay_result)

        metrics = _compute_metrics_for_scenario(base_path, scenario_id)
        profile = profiles.get(profile_name)
        failed_metrics = (
            _failed_metrics(metrics, profile) if profile is not None else ["profile_missing"]
        )
        metrics_scenarios.append(
            {
                "scenario_id": scenario_id,
                "evaluation_profile": profile_name,
                "metrics": metrics,
                "failed_metrics": failed_metrics,
            }
        )

        verdict_scenarios.append(
            _build_verdict(
                scenario_id=scenario_id,
                profile_name=profile_name,
                profile=profile,
                replay_result=replay_result,
                metrics=metrics,
                failed_metrics=failed_metrics,
            )
        )

    replay_bundle = {
        "schema_version": REPLAY_RESULTS_SCHEMA_VERSION,
        "run_id": base_path.name,
        "scenarios": replay_scenarios,
    }
    metrics_bundle = {
        "schema_version": EVALUATION_METRICS_SCHEMA_VERSION,
        "run_id": base_path.name,
        "scenarios": metrics_scenarios,
    }
    verdicts_bundle = {
        "schema_version": EVALUATION_VERDICTS_SCHEMA_VERSION,
        "run_id": base_path.name,
        "scenarios": verdict_scenarios,
    }
    validate_replay_results_bundle(replay_bundle)
    validate_evaluation_metrics_bundle(metrics_bundle)
    validate_evaluation_verdicts_bundle(verdicts_bundle)

    _update_reports(base_path, replay_bundle, verdicts_bundle)
    return replay_bundle, metrics_bundle, verdicts_bundle


def write_replay_and_evaluation_files(
    run_dir: str | Path,
    replay_bundle: dict[str, Any],
    metrics_bundle: dict[str, Any],
    verdicts_bundle: dict[str, Any],
) -> tuple[tuple[Path, Path, Path], tuple[Path, Path, Path], tuple[Path, Path, Path]]:
    base_path = Path(run_dir)
    replay_paths = _write_bundle_files(
        base_path,
        stem="replay_results",
        payload=replay_bundle,
        markdown=_render_replay_markdown(replay_bundle),
        fieldnames=["scenario_id", "replay_result", "field_name", "tick_index"],
        row_builder=lambda scenario: {
            "scenario_id": scenario["scenario_id"],
            "replay_result": scenario["replay_result"],
            "field_name": (
                scenario["divergence"]["field_name"]
                if scenario["divergence"] is not None
                else ""
            ),
            "tick_index": (
                scenario["divergence"]["tick_index"]
                if scenario["divergence"] is not None
                else ""
            ),
        },
    )
    metrics_paths = _write_bundle_files(
        base_path,
        stem="evaluation_metrics",
        payload=metrics_bundle,
        markdown=_render_metrics_markdown(metrics_bundle),
        fieldnames=[
            "scenario_id",
            "evaluation_profile",
            "ATE_RMSE_M",
            "RPE_RMSE_M",
            "DRIFT_PCT",
            "LOCALIZATION_CONTINUITY_PCT",
            "FALLBACK_REACTION_TIME_S",
            "MISSION_SUCCESS",
            "failed_metrics",
        ],
        row_builder=lambda scenario: {
            "scenario_id": scenario["scenario_id"],
            "evaluation_profile": scenario["evaluation_profile"],
            **scenario["metrics"],
            "failed_metrics": ",".join(scenario["failed_metrics"]),
        },
    )
    verdict_paths = _write_bundle_files(
        base_path,
        stem="evaluation_verdicts",
        payload=verdicts_bundle,
        markdown=_render_verdicts_markdown(verdicts_bundle),
        fieldnames=[
            "scenario_id",
            "evaluation_profile",
            "verdict",
            "primary_reason_code",
            "mission_success",
            "invalid_run",
            "failed_checks",
        ],
        row_builder=lambda scenario: {
            "scenario_id": scenario["scenario_id"],
            "evaluation_profile": scenario["evaluation_profile"],
            "verdict": scenario["verdict"],
            "primary_reason_code": scenario["primary_reason_code"],
            "mission_success": scenario["mission_success"],
            "invalid_run": scenario["invalid_run"],
            "failed_checks": ",".join(scenario["failed_checks"]),
        },
    )
    return replay_paths, metrics_paths, verdict_paths


def append_regression_checks(
    regression_result: dict[str, Any],
    *,
    reports: dict[str, dict[str, Any]],
    replay_bundle: dict[str, Any],
    metrics_bundle: dict[str, Any],
    verdicts_bundle: dict[str, Any],
    replay_paths: tuple[Path, Path, Path],
    metrics_paths: tuple[Path, Path, Path],
    verdict_paths: tuple[Path, Path, Path],
) -> dict[str, Any]:
    checks = [
        check
        for check in regression_result.get("checks", [])
        if check["name"]
        not in {
            "runtime_trace_present",
            "truth_trace_present",
            "replay_results_present",
            "evaluation_metrics_bundle_present",
            "evaluation_verdicts_present",
            "deterministic_replay_passed",
            "manifest_hash_recorded",
            "config_hash_recorded",
        }
    ]
    checks.extend(
        [
            {
                "name": "runtime_trace_present",
                "passed": all(
                    (Path(report["runtime_trace_path"])).exists()
                    for report in reports.values()
                ),
                "detail": "Every scenario must emit a runtime trace artifact.",
            },
            {
                "name": "truth_trace_present",
                "passed": all(
                    (Path(report["truth_trace_path"])).exists()
                    for report in reports.values()
                ),
                "detail": "Every scenario must emit a pseudo-truth trace artifact.",
            },
            {
                "name": "replay_results_present",
                "passed": all(path.exists() for path in replay_paths),
                "detail": "replay_results.json/.md/.csv must all be present.",
            },
            {
                "name": "evaluation_metrics_bundle_present",
                "passed": all(path.exists() for path in metrics_paths),
                "detail": "evaluation_metrics.json/.md/.csv must all be present.",
            },
            {
                "name": "evaluation_verdicts_present",
                "passed": all(path.exists() for path in verdict_paths),
                "detail": "evaluation_verdicts.json/.md/.csv must all be present.",
            },
            {
                "name": "deterministic_replay_passed",
                "passed": all(
                    scenario["replay_result"] == "PASS"
                    for scenario in replay_bundle["scenarios"]
                ),
                "detail": "All baseline scenarios must match deterministic replay.",
            },
            {
                "name": "manifest_hash_recorded",
                "passed": all(report["manifest_hash"] for report in reports.values()),
                "detail": "All reports must record manifest_hash.",
            },
            {
                "name": "config_hash_recorded",
                "passed": all(report["config_hash"] for report in reports.values()),
                "detail": "All reports must record config_hash.",
            },
        ]
    )
    regression_result["checks"] = checks
    regression_result["overall_result"] = (
        "PASS" if all(check["passed"] for check in checks) else "FAIL"
    )
    return regression_result


def _compute_metrics_for_scenario(run_dir: Path, scenario_id: str) -> dict[str, Any]:
    runtime_trace = _load_json(run_dir / f"{scenario_id}_runtime_trace.json")
    truth_trace = _load_json(run_dir / f"{scenario_id}_truth_trace.json")
    report = _load_json(run_dir / f"{scenario_id}_report.json")

    runtime_entries = runtime_trace["entries"]
    truth_entries = truth_trace["entries"]
    per_tick_errors: list[float] = []
    for runtime_entry, truth_entry in zip(runtime_entries, truth_entries):
        per_tick_errors.append(
            _distance(
                runtime_entry["estimated_position_m"],
                truth_entry["position_m"],
            )
        )
    ate_rmse = _rmse(per_tick_errors)

    rpe_errors: list[float] = []
    for index in range(1, len(runtime_entries)):
        runtime_delta = _distance(
            runtime_entries[index]["estimated_position_m"],
            runtime_entries[index - 1]["estimated_position_m"],
        )
        truth_delta = _distance(
            truth_entries[index]["position_m"],
            truth_entries[index - 1]["position_m"],
        )
        rpe_errors.append(abs(runtime_delta - truth_delta))
    rpe_rmse = _rmse(rpe_errors) if rpe_errors else 0.0

    final_error = per_tick_errors[-1] if per_tick_errors else 0.0
    route_length = max(float(report["route_length_m"]), 1.0)
    drift_pct = round((final_error / route_length) * 100.0, 3)
    localization_continuity_pct = round(
        (
            sum(
                1
                for entry in runtime_entries
                if entry["localization_mode"] != "HOLD_LAST_SAFE"
            )
            / len(runtime_entries)
        )
        * 100.0,
        3,
    )
    fallback_reaction_time_s = _compute_fallback_reaction_time_s(runtime_entries)
    mission_success = report["mission_state"] not in {
        "MISSION_SAFE_HOLD",
        "MISSION_ABORT",
    }
    return {
        "ATE_RMSE_M": ate_rmse,
        "RPE_RMSE_M": rpe_rmse,
        "DRIFT_PCT": drift_pct,
        "LOCALIZATION_CONTINUITY_PCT": localization_continuity_pct,
        "FALLBACK_REACTION_TIME_S": fallback_reaction_time_s,
        "MISSION_SUCCESS": mission_success,
    }


def _compute_fallback_reaction_time_s(runtime_entries: list[dict[str, Any]]) -> float:
    first_denied_tick = next(
        (entry["tick_index"] for entry in runtime_entries if entry["gnss_state"] == "denied"),
        None,
    )
    if first_denied_tick is None:
        return 0.0
    response_tick = next(
        (
            entry["tick_index"]
            for entry in runtime_entries
            if entry["tick_index"] >= first_denied_tick
            and entry["mission_state"]
            in {"MISSION_FALLBACK", "MISSION_SAFE_HOLD", "MISSION_ABORT"}
        ),
        None,
    )
    if response_tick is None:
        return 0.0
    return round(float(response_tick - first_denied_tick), 3)


def _failed_metrics(
    metrics: dict[str, Any],
    profile: EvaluationProfile,
) -> list[str]:
    failed: list[str] = []
    if float(metrics["ATE_RMSE_M"]) > profile.ate_rmse_m_max:
        failed.append("ATE_RMSE_M")
    if float(metrics["RPE_RMSE_M"]) > profile.rpe_rmse_m_max:
        failed.append("RPE_RMSE_M")
    if float(metrics["DRIFT_PCT"]) > profile.drift_pct_max:
        failed.append("DRIFT_PCT")
    if float(metrics["LOCALIZATION_CONTINUITY_PCT"]) < profile.localization_continuity_pct_min:
        failed.append("LOCALIZATION_CONTINUITY_PCT")
    if float(metrics["FALLBACK_REACTION_TIME_S"]) > profile.fallback_reaction_time_s_max:
        failed.append("FALLBACK_REACTION_TIME_S")
    if profile.require_mission_success and not bool(metrics["MISSION_SUCCESS"]):
        failed.append("MISSION_SUCCESS")
    return failed


def _build_verdict(
    *,
    scenario_id: str,
    profile_name: str,
    profile: EvaluationProfile | None,
    replay_result: dict[str, Any],
    metrics: dict[str, Any],
    failed_metrics: list[str],
) -> dict[str, Any]:
    if profile is None:
        return {
            "scenario_id": scenario_id,
            "evaluation_profile": profile_name,
            "verdict": "INVALID",
            "primary_reason_code": "evaluation_profile_missing",
            "reason_codes": ["evaluation_profile_missing"],
            "mission_success": bool(metrics["MISSION_SUCCESS"]),
            "invalid_run": True,
            "failed_checks": ["evaluation_profile_missing"],
        }
    if replay_result["replay_result"] != "PASS":
        return {
            "scenario_id": scenario_id,
            "evaluation_profile": profile_name,
            "verdict": "INVALID",
            "primary_reason_code": "deterministic_replay_failed",
            "reason_codes": ["deterministic_replay_failed"],
            "mission_success": bool(metrics["MISSION_SUCCESS"]),
            "invalid_run": True,
            "failed_checks": ["deterministic_replay_failed"],
        }
    if failed_metrics:
        return {
            "scenario_id": scenario_id,
            "evaluation_profile": profile_name,
            "verdict": "FAIL",
            "primary_reason_code": "evaluation_threshold_exceeded",
            "reason_codes": ["evaluation_threshold_exceeded"],
            "mission_success": bool(metrics["MISSION_SUCCESS"]),
            "invalid_run": False,
            "failed_checks": failed_metrics,
        }
    return {
        "scenario_id": scenario_id,
        "evaluation_profile": profile_name,
        "verdict": "PASS",
        "primary_reason_code": "evaluation_acceptance_passed",
        "reason_codes": ["evaluation_acceptance_passed"],
        "mission_success": bool(metrics["MISSION_SUCCESS"]),
        "invalid_run": False,
        "failed_checks": [],
    }


def _update_reports(
    run_dir: Path,
    replay_bundle: dict[str, Any],
    verdicts_bundle: dict[str, Any],
) -> None:
    replay_by_scenario = {
        scenario["scenario_id"]: scenario for scenario in replay_bundle["scenarios"]
    }
    verdict_by_scenario = {
        scenario["scenario_id"]: scenario for scenario in verdicts_bundle["scenarios"]
    }
    for scenario_id in EXPECTED_SCENARIO_IDS:
        report_path = run_dir / f"{scenario_id}_report.json"
        payload = _load_json(report_path)
        replay = replay_by_scenario[scenario_id]
        verdict = verdict_by_scenario[scenario_id]
        payload["deterministic_replay_passed"] = replay["replay_result"] == "PASS"
        payload["evaluation_verdict"] = verdict["verdict"]
        payload["invalid_run"] = verdict["invalid_run"]
        payload["evaluation_primary_reason_code"] = verdict["primary_reason_code"]
        report_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def _render_replay_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Replay Results",
        "",
        f"- Run ID: `{bundle['run_id']}`",
        "",
        "| Scenario | Replay Result | Divergence |",
        "| --- | --- | --- |",
    ]
    for scenario in bundle["scenarios"]:
        divergence = scenario["divergence"]
        detail = "-" if divergence is None else divergence["field_name"]
        lines.append(
            f"| {scenario['scenario_id']} | {scenario['replay_result']} | {detail} |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_metrics_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Evaluation Metrics",
        "",
        f"- Run ID: `{bundle['run_id']}`",
        "",
        "| Scenario | Profile | ATE | RPE | Drift % | Continuity % | Fallback s | Success | Failed Metrics |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for scenario in bundle["scenarios"]:
        metrics = scenario["metrics"]
        failed = ", ".join(scenario["failed_metrics"]) or "-"
        lines.append(
            "| {scenario_id} | {evaluation_profile} | {ATE_RMSE_M:.3f} | {RPE_RMSE_M:.3f} | {DRIFT_PCT:.3f} | {LOCALIZATION_CONTINUITY_PCT:.3f} | {FALLBACK_REACTION_TIME_S:.3f} | {MISSION_SUCCESS} | {failed} |".format(
                failed=failed,
                **scenario,
                **metrics,
            )
        )
    lines.append("")
    return "\n".join(lines)


def _render_verdicts_markdown(bundle: dict[str, Any]) -> str:
    lines = [
        "# Evaluation Verdicts",
        "",
        f"- Run ID: `{bundle['run_id']}`",
        "",
        "| Scenario | Profile | Verdict | Primary Reason | Mission Success | Invalid | Failed Checks |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for scenario in bundle["scenarios"]:
        failed = ", ".join(scenario["failed_checks"]) or "-"
        lines.append(
            "| {scenario_id} | {evaluation_profile} | {verdict} | {primary_reason_code} | {mission_success} | {invalid_run} | {failed} |".format(
                failed=failed,
                **scenario,
            )
        )
    lines.append("")
    return "\n".join(lines)


def _write_bundle_files(
    run_dir: Path,
    *,
    stem: str,
    payload: dict[str, Any],
    markdown: str,
    fieldnames: list[str],
    row_builder,
) -> tuple[Path, Path, Path]:
    json_path = run_dir / f"{stem}.json"
    md_path = run_dir / f"{stem}.md"
    csv_path = run_dir / f"{stem}.csv"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for scenario in payload["scenarios"]:
            writer.writerow(row_builder(scenario))
    return json_path, md_path, csv_path


def _resolve_manifest_path(scenario_id: str) -> Path:
    return Path(__file__).resolve().parents[2] / "scenarios" / "baseline" / f"{scenario_id}.yaml"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    dx = float(first["x"]) - float(second["x"])
    dy = float(first["y"]) - float(second["y"])
    dz = float(first["z"]) - float(second["z"])
    return sqrt((dx * dx) + (dy * dy) + (dz * dz))


def _rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sqrt(sum(value * value for value in values) / len(values)), 3)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run deterministic replay and offline evaluation bundles."
    )
    parser.add_argument("run_dir", help="Directory containing scenario artifacts.")
    parser.add_argument("--config", required=True, help="Path to simulation config.")
    parser.add_argument(
        "--eval-config",
        default=str(DEFAULT_EVAL_CONFIG_PATH),
        help="Path to evaluation profile config.",
    )
    parser.add_argument(
        "--regression-result",
        help="Optional path to regression_result.json to update with replay/eval checks.",
    )
    args = parser.parse_args()

    replay_bundle, metrics_bundle, verdicts_bundle = run_replay_and_evaluation(
        args.run_dir,
        sim_config_path=args.config,
        eval_config_path=args.eval_config,
    )
    paths = write_replay_and_evaluation_files(
        args.run_dir, replay_bundle, metrics_bundle, verdicts_bundle
    )
    if args.regression_result:
        regression_result = json.loads(
            Path(args.regression_result).read_text(encoding="utf-8")
        )
        reports = load_reports(args.run_dir)
        updated = append_regression_checks(
            regression_result,
            reports=reports,
            replay_bundle=replay_bundle,
            metrics_bundle=metrics_bundle,
            verdicts_bundle=verdicts_bundle,
            replay_paths=paths[0],
            metrics_paths=paths[1],
            verdict_paths=paths[2],
        )
        Path(args.regression_result).write_text(
            json.dumps(updated, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    print(
        json.dumps(
            {
                "replay_results_json": str(paths[0][0]),
                "evaluation_metrics_json": str(paths[1][0]),
                "evaluation_verdicts_json": str(paths[2][0]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
