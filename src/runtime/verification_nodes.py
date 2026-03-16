"""Hybrid bridge runners for Phase 12 verification nodes."""

from __future__ import annotations

import json
import os
from math import sqrt
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from evaluation.artifact_schema import (
    validate_ew_risk_map,
    validate_mission_audit,
    validate_report,
    validate_runtime_trace,
    validate_tactical_summary,
    validate_truth_trace,
)
from evaluation.profiles import DEFAULT_EVAL_CONFIG_PATH, EvaluationProfile, load_evaluation_profiles
from logging_replay.replay import compare_replay_run

LOGGER_NODE_RESULT_SCHEMA_VERSION = "1.0"
EVALUATION_NODE_RESULT_SCHEMA_VERSION = "1.0"
VERIFICATION_NODE_RESULTS_SCHEMA_VERSION = "1.0"


def run_verification_nodes_probe(
    *,
    scenario_id: str,
    scenario_path: str | Path,
    run_dir: str | Path,
    sim_config_path: str | Path,
    eval_config_path: str | Path | None = None,
) -> dict[str, Any]:
    run_path = Path(run_dir)
    eval_config = _resolve_eval_config_path(eval_config_path)

    logger_result = run_logger_node_probe(
        scenario_id=scenario_id,
        run_dir=run_path,
    )
    evaluation_result = run_evaluation_node_probe(
        scenario_id=scenario_id,
        scenario_path=scenario_path,
        run_dir=run_path,
        sim_config_path=sim_config_path,
        eval_config_path=eval_config,
    )
    overall_result = (
        "PASS"
        if logger_result["result"] == "PASS" and evaluation_result["result"] == "PASS"
        else "FAIL"
    )
    payload = {
        "schema_version": VERIFICATION_NODE_RESULTS_SCHEMA_VERSION,
        "run_id": run_path.name,
        "scenario_id": scenario_id,
        "logger_node": logger_result,
        "evaluation_node": evaluation_result,
        "overall_result": overall_result,
    }
    artifact_path = run_path / f"{scenario_id}_verification_node_results.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    payload["artifact_path"] = str(artifact_path)
    return payload


def run_logger_node_probe(
    *,
    scenario_id: str,
    run_dir: str | Path,
) -> dict[str, Any]:
    run_path = Path(run_dir)
    artifact_validators: dict[str, Any] = {
        f"{scenario_id}_report.json": validate_report,
        f"{scenario_id}_mission_audit.json": validate_mission_audit,
        f"{scenario_id}_runtime_trace.json": validate_runtime_trace,
        f"{scenario_id}_truth_trace.json": validate_truth_trace,
        f"{scenario_id}_ew_risk_map.json": validate_ew_risk_map,
        f"{scenario_id}_tactical_summary.json": validate_tactical_summary,
    }

    failed_checks: list[str] = []
    details: list[dict[str, Any]] = []
    for artifact_name, validator in artifact_validators.items():
        artifact_path = run_path / artifact_name
        if not artifact_path.exists():
            failed_checks.append(f"{artifact_name.replace('.', '_')}_missing")
            details.append(
                {
                    "artifact": artifact_name,
                    "status": "MISSING",
                    "error": "artifact_missing",
                }
            )
            continue
        try:
            payload = json.loads(artifact_path.read_text(encoding="utf-8"))
            validator(payload)
            details.append({"artifact": artifact_name, "status": "PASS"})
        except Exception as exc:  # noqa: BLE001 - we need full validation coverage
            failed_checks.append(f"{artifact_name.replace('.', '_')}_invalid")
            details.append(
                {
                    "artifact": artifact_name,
                    "status": "FAIL",
                    "error": str(exc),
                }
            )

    result = "PASS" if not failed_checks else "FAIL"
    return {
        "schema_version": LOGGER_NODE_RESULT_SCHEMA_VERSION,
        "node_name": "logger_node",
        "scenario_id": scenario_id,
        "result": result,
        "failed_checks": failed_checks,
        "checks": details,
    }


def run_evaluation_node_probe(
    *,
    scenario_id: str,
    scenario_path: str | Path,
    run_dir: str | Path,
    sim_config_path: str | Path,
    eval_config_path: str | Path | None = None,
) -> dict[str, Any]:
    run_path = Path(run_dir)
    replay_result = _run_deterministic_replay(
        scenario_id=scenario_id,
        scenario_path=scenario_path,
        run_dir=run_path,
        sim_config_path=sim_config_path,
    )
    report = _load_json(run_path / f"{scenario_id}_report.json")
    evaluation_profile_name = str(report["evaluation_profile"])
    profiles = load_evaluation_profiles(_resolve_eval_config_path(eval_config_path))
    profile = profiles.get(evaluation_profile_name)

    failed_checks: list[str] = []
    metrics: dict[str, Any] | None = None
    if profile is None:
        failed_checks.append("evaluation_profile_missing")
    else:
        try:
            metrics = _compute_metrics_for_scenario(run_path, scenario_id)
            failed_checks.extend(_failed_metrics(metrics, profile))
        except Exception:  # noqa: BLE001 - surfaced in payload
            failed_checks.append("metric_computation_failed")

    verdict = _build_verdict(
        replay_result=replay_result,
        profile_name=evaluation_profile_name,
        profile=profile,
        metrics=metrics,
        failed_metric_checks=failed_checks,
    )
    if verdict["verdict"] != "PASS" and not failed_checks:
        failed_checks.append("evaluation_verdict_not_pass")

    result = "PASS" if verdict["verdict"] == "PASS" else "FAIL"
    return {
        "schema_version": EVALUATION_NODE_RESULT_SCHEMA_VERSION,
        "node_name": "evaluation_node",
        "scenario_id": scenario_id,
        "result": result,
        "replay_result": replay_result["replay_result"],
        "divergence": replay_result["divergence"],
        "evaluation_profile": evaluation_profile_name,
        "verdict": verdict["verdict"],
        "primary_reason_code": verdict["primary_reason_code"],
        "reason_codes": verdict["reason_codes"],
        "mission_success": verdict["mission_success"],
        "invalid_run": verdict["invalid_run"],
        "failed_checks": failed_checks,
        "failed_metrics": verdict["failed_metrics"],
        "metrics": metrics,
    }


def _run_deterministic_replay(
    *,
    scenario_id: str,
    scenario_path: str | Path,
    run_dir: Path,
    sim_config_path: str | Path,
) -> dict[str, Any]:
    try:
        with TemporaryDirectory(prefix=f"{scenario_id}_verification_replay_") as replay_dir:
            from scenario_orchestrator.main import run_scenario

            run_scenario(
                scenario_path=scenario_path,
                output_dir=replay_dir,
                config_path=sim_config_path,
                run_id="verification_replay",
            )
            return compare_replay_run(
                scenario_id=scenario_id,
                original_run_dir=run_dir,
                replay_run_dir=replay_dir,
            )
    except Exception as exc:  # noqa: BLE001 - encoded into deterministic failure payload
        return {
            "replay_result": "INVALID",
            "divergence": {
                "tick_index": None,
                "field_name": "replay_execution",
                "original_value": "verification_replay",
                "replay_value": str(exc),
            },
        }


def _build_verdict(
    *,
    replay_result: dict[str, Any],
    profile_name: str,
    profile: EvaluationProfile | None,
    metrics: dict[str, Any] | None,
    failed_metric_checks: list[str],
) -> dict[str, Any]:
    mission_success = bool(metrics["MISSION_SUCCESS"]) if metrics is not None else False
    if profile is None:
        return {
            "evaluation_profile": profile_name,
            "verdict": "INVALID",
            "primary_reason_code": "evaluation_profile_missing",
            "reason_codes": ["evaluation_profile_missing"],
            "mission_success": mission_success,
            "invalid_run": True,
            "failed_metrics": ["profile_missing"],
        }
    if replay_result["replay_result"] != "PASS":
        return {
            "evaluation_profile": profile_name,
            "verdict": "INVALID",
            "primary_reason_code": "deterministic_replay_failed",
            "reason_codes": ["deterministic_replay_failed"],
            "mission_success": mission_success,
            "invalid_run": True,
            "failed_metrics": [],
        }
    if failed_metric_checks:
        return {
            "evaluation_profile": profile_name,
            "verdict": "FAIL",
            "primary_reason_code": "evaluation_threshold_exceeded",
            "reason_codes": ["evaluation_threshold_exceeded"],
            "mission_success": mission_success,
            "invalid_run": False,
            "failed_metrics": list(failed_metric_checks),
        }
    return {
        "evaluation_profile": profile_name,
        "verdict": "PASS",
        "primary_reason_code": "evaluation_acceptance_passed",
        "reason_codes": ["evaluation_acceptance_passed"],
        "mission_success": mission_success,
        "invalid_run": False,
        "failed_metrics": [],
    }


def _compute_metrics_for_scenario(run_dir: Path, scenario_id: str) -> dict[str, Any]:
    runtime_trace = _load_json(run_dir / f"{scenario_id}_runtime_trace.json")
    truth_trace = _load_json(run_dir / f"{scenario_id}_truth_trace.json")
    report = _load_json(run_dir / f"{scenario_id}_report.json")

    runtime_entries = runtime_trace["entries"]
    truth_entries = truth_trace["entries"]
    if not runtime_entries or not truth_entries:
        raise ValueError("runtime_trace/truth_trace entries must be non-empty.")

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

    final_error = per_tick_errors[-1]
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


def _distance(first: dict[str, Any], second: dict[str, Any]) -> float:
    return sqrt(
        (float(first["x"]) - float(second["x"])) ** 2
        + (float(first["y"]) - float(second["y"])) ** 2
        + (float(first["z"]) - float(second["z"])) ** 2
    )


def _rmse(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sqrt(sum(value * value for value in values) / len(values)), 3)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_eval_config_path(eval_config_path: str | Path | None) -> str | Path:
    if eval_config_path is not None:
        return eval_config_path
    env_path = os.environ.get("EVAL_CONFIG_PATH")
    if env_path:
        return env_path
    return DEFAULT_EVAL_CONFIG_PATH
