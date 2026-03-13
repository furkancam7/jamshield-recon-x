"""Stable schema validation for evaluation artifacts."""

from __future__ import annotations

import re
from typing import Any

REPORT_SCHEMA_VERSION = "2.4"
SUMMARY_SCHEMA_VERSION = "2.4"
MISSION_AUDIT_SCHEMA_VERSION = "1.0"
EW_RISK_MAP_SCHEMA_VERSION = "1.0"
EW_METRICS_SCHEMA_VERSION = "1.0"
TACTICAL_SUMMARY_SCHEMA_VERSION = "1.0"
TACTICAL_SUMMARY_BUNDLE_SCHEMA_VERSION = "1.0"
RUNTIME_TRACE_SCHEMA_VERSION = "1.0"
TRUTH_TRACE_SCHEMA_VERSION = "1.0"
REPLAY_RESULTS_SCHEMA_VERSION = "1.0"
EVALUATION_METRICS_SCHEMA_VERSION = "1.0"
EVALUATION_VERDICTS_SCHEMA_VERSION = "1.0"

REQUIRED_REPORT_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "map_name",
    "run_seed",
    "gnss_condition",
    "gnss_state",
    "gnss_trust",
    "vio_trust",
    "sync_quality",
    "mission_confidence",
    "trust_primary_reason_code",
    "trust_reason_codes",
    "mission_state",
    "mission_primary_reason_code",
    "mission_reason_codes",
    "mission_transition_count",
    "mission_audit_path",
    "ew_risk_level",
    "ew_primary_reason_code",
    "ew_reason_codes",
    "ew_max_risk",
    "ew_affected_cell_count",
    "ew_corridor_cost",
    "ew_risk_map_path",
    "tactical_primary_reason_code",
    "tactical_reason_codes",
    "tactical_advisory_code",
    "tactical_advisory_text",
    "tactical_summary_text",
    "tactical_summary_path",
    "runtime_trace_path",
    "truth_trace_path",
    "vio_state",
    "vio_health_score",
    "effective_vio_state",
    "ate_m",
    "route_length_m",
    "ground_truth_usage",
    "config_id",
    "manifest_hash",
    "config_hash",
    "evaluation_profile",
    "deterministic_replay_passed",
    "evaluation_verdict",
    "invalid_run",
    "evaluation_primary_reason_code",
    "software_revision",
    "timestamp",
    "scenario_metadata",
    "vio_metrics_source",
    "vio_metrics",
    "localization_mode",
    "localization_confidence",
    "gnss_weight",
    "vio_weight",
}

REQUIRED_SUMMARY_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_ids",
    "scenarios",
    "checks",
    "overall_regression_result",
    "config_id",
    "evaluation_profiles",
    "software_revision",
    "generated_at",
}

SCENARIO_METADATA_FIELDS = {"title", "description", "owner"}
VALID_MISSION_STATES = {
    "MISSION_EXECUTE",
    "MISSION_DEGRADED",
    "MISSION_FALLBACK",
    "MISSION_SAFE_HOLD",
    "MISSION_ABORT",
}
VALID_LOCALIZATION_MODES = {
    "GNSS_PRIMARY",
    "BLENDED",
    "VIO_PRIMARY",
    "HOLD_LAST_SAFE",
}
VALID_EW_RISK_LEVELS = {"none", "low", "medium", "high"}
VALID_EVALUATION_VERDICTS = {"PENDING", "PASS", "FAIL", "INVALID"}
LEGACY_MISSION_STATES = {"MISSION_NORMAL", "MISSION_RTL", "MISSION_EMERGENCY_LAND"}
LEGACY_LOCALIZATION_MODES = {"FUSED", "VIO_ONLY", "DEAD_RECKONING"}
SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
VIO_METRIC_FIELDS = {
    "timestamp_ns",
    "profile_id",
    "feature_count",
    "matched_feature_count",
    "track_continuity",
    "reprojection_error_px",
    "pose_delta_xy_m",
    "yaw_delta_rad",
    "imu_alignment_error",
    "vio_health_score",
    "vio_state",
    "effective_vio_state",
    "reason_codes",
}
REQUIRED_MISSION_AUDIT_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "entries",
}
REQUIRED_EW_RISK_MAP_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "timestamp_ns",
    "frame_id",
    "cell_size_m",
    "width_cells",
    "height_cells",
    "origin",
    "risk_cells",
    "evidence_codes",
    "primary_reason_code",
    "reason_codes",
    "max_risk",
    "affected_cell_count",
    "corridor_cost",
    "risk_cells_hash",
}
REQUIRED_EW_METRICS_FIELDS = {
    "schema_version",
    "run_id",
    "checks_snapshot",
    "scenarios",
}
REQUIRED_TACTICAL_SUMMARY_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "timestamp_ns",
    "mission_state",
    "mission_confidence",
    "localization_mode",
    "ew_risk_level",
    "affected_area_count",
    "ew_corridor_cost",
    "primary_reason_code",
    "reason_codes",
    "advisory_code",
    "advisory_text",
    "summary_text",
}
REQUIRED_TACTICAL_SUMMARY_BUNDLE_FIELDS = {
    "schema_version",
    "run_id",
    "checks_snapshot",
    "scenarios",
}
REQUIRED_RUNTIME_TRACE_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "entries",
}
REQUIRED_TRUTH_TRACE_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "entries",
}
REQUIRED_REPLAY_RESULTS_FIELDS = {
    "schema_version",
    "run_id",
    "scenarios",
}
REQUIRED_EVALUATION_METRICS_FIELDS = {
    "schema_version",
    "run_id",
    "scenarios",
}
REQUIRED_EVALUATION_VERDICTS_FIELDS = {
    "schema_version",
    "run_id",
    "scenarios",
}
MISSION_AUDIT_ENTRY_FIELDS = {
    "tick_index",
    "step_inputs",
    "gnss_state",
    "mission_confidence",
    "effective_vio_state",
    "trust_primary_reason_code",
    "candidate_state",
    "final_state",
    "primary_reason_code",
    "reason_codes",
    "transition_count",
}
RUNTIME_TRACE_ENTRY_FIELDS = {
    "tick_index",
    "timestamp_ns",
    "step_inputs",
    "gnss_state",
    "gnss_trust",
    "vio_trust",
    "effective_vio_state",
    "sync_quality",
    "localization_mode",
    "localization_confidence",
    "mission_confidence",
    "trust_primary_reason_code",
    "mission_state",
    "mission_primary_reason_code",
    "estimated_position_m",
    "route_progress_pct",
}
TRUTH_TRACE_ENTRY_FIELDS = {
    "tick_index",
    "timestamp_ns",
    "position_m",
    "route_progress_pct",
}
REQUIRED_SUMMARY_SCENARIO_FIELDS = {
    "scenario_id",
    "gnss_state",
    "gnss_trust",
    "vio_trust",
    "sync_quality",
    "mission_confidence",
    "trust_primary_reason_code",
    "mission_primary_reason_code",
    "mission_transition_count",
    "ew_risk_level",
    "ew_primary_reason_code",
    "ew_max_risk",
    "ew_affected_cell_count",
    "ew_corridor_cost",
    "ew_risk_map_path",
    "tactical_primary_reason_code",
    "tactical_advisory_code",
    "tactical_summary_text",
    "tactical_summary_path",
    "manifest_hash",
    "config_hash",
    "evaluation_profile",
    "deterministic_replay_passed",
    "evaluation_verdict",
    "invalid_run",
    "evaluation_primary_reason_code",
    "mission_state",
    "effective_vio_state",
    "vio_profile_id",
    "localization_mode",
    "localization_confidence",
    "ate_rmse",
    "mission_audit_path",
    "timestamp",
}


def validate_report(payload: dict[str, Any]) -> None:
    missing = REQUIRED_REPORT_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Report missing required fields: {missing_list}")

    metadata = payload["scenario_metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("scenario_metadata must be a mapping.")
    metadata_missing = SCENARIO_METADATA_FIELDS.difference(metadata)
    if metadata_missing:
        missing_list = ", ".join(sorted(metadata_missing))
        raise ValueError(f"scenario_metadata missing required fields: {missing_list}")

    if payload["mission_state"] in LEGACY_MISSION_STATES:
        raise ValueError(f"Legacy mission_state is not allowed: {payload['mission_state']}")
    if payload["mission_state"] not in VALID_MISSION_STATES:
        raise ValueError(f"Unsupported mission_state: {payload['mission_state']}")

    if payload["localization_mode"] in LEGACY_LOCALIZATION_MODES:
        raise ValueError(
            f"Legacy localization_mode is not allowed: {payload['localization_mode']}"
        )
    if payload["localization_mode"] not in VALID_LOCALIZATION_MODES:
        raise ValueError(f"Unsupported localization_mode: {payload['localization_mode']}")

    if payload["vio_metrics_source"] != "pipeline_v1":
        raise ValueError("vio_metrics_source must be 'pipeline_v1'.")

    _validate_reason_code(payload["trust_primary_reason_code"])
    _validate_reason_code_list(payload["trust_reason_codes"], "trust_reason_codes")
    _validate_reason_code(payload["mission_primary_reason_code"])
    _validate_reason_code_list(payload["mission_reason_codes"], "mission_reason_codes")
    _validate_reason_code(payload["ew_primary_reason_code"])
    _validate_reason_code_list(payload["ew_reason_codes"], "ew_reason_codes")
    _validate_reason_code(payload["tactical_primary_reason_code"])
    _validate_reason_code_list(payload["tactical_reason_codes"], "tactical_reason_codes")
    _validate_reason_code(payload["tactical_advisory_code"])
    _validate_reason_code(payload["evaluation_primary_reason_code"])

    if not isinstance(payload["mission_transition_count"], int):
        raise ValueError("mission_transition_count must be an integer.")
    if payload["mission_transition_count"] < 0:
        raise ValueError("mission_transition_count must be non-negative.")
    if not isinstance(payload["mission_audit_path"], str) or not payload["mission_audit_path"].strip():
        raise ValueError("mission_audit_path must be a non-empty string.")
    if payload["ew_risk_level"] not in VALID_EW_RISK_LEVELS:
        raise ValueError(f"Unsupported ew_risk_level: {payload['ew_risk_level']}")
    if not isinstance(payload["ew_affected_cell_count"], int):
        raise ValueError("ew_affected_cell_count must be an integer.")
    if payload["ew_affected_cell_count"] < 0:
        raise ValueError("ew_affected_cell_count must be non-negative.")
    if not isinstance(payload["ew_risk_map_path"], str) or not payload["ew_risk_map_path"].strip():
        raise ValueError("ew_risk_map_path must be a non-empty string.")
    if not isinstance(payload["tactical_advisory_text"], str) or not payload["tactical_advisory_text"].strip():
        raise ValueError("tactical_advisory_text must be a non-empty string.")
    if not isinstance(payload["tactical_summary_text"], str) or not payload["tactical_summary_text"].strip():
        raise ValueError("tactical_summary_text must be a non-empty string.")
    if not isinstance(payload["tactical_summary_path"], str) or not payload["tactical_summary_path"].strip():
        raise ValueError("tactical_summary_path must be a non-empty string.")
    if not isinstance(payload["runtime_trace_path"], str) or not payload["runtime_trace_path"].strip():
        raise ValueError("runtime_trace_path must be a non-empty string.")
    if not isinstance(payload["truth_trace_path"], str) or not payload["truth_trace_path"].strip():
        raise ValueError("truth_trace_path must be a non-empty string.")
    if not isinstance(payload["manifest_hash"], str) or not payload["manifest_hash"].strip():
        raise ValueError("manifest_hash must be a non-empty string.")
    if not isinstance(payload["config_hash"], str) or not payload["config_hash"].strip():
        raise ValueError("config_hash must be a non-empty string.")
    if not isinstance(payload["evaluation_profile"], str) or not payload["evaluation_profile"].strip():
        raise ValueError("evaluation_profile must be a non-empty string.")
    if not isinstance(payload["deterministic_replay_passed"], bool):
        raise ValueError("deterministic_replay_passed must be a boolean.")
    if payload["evaluation_verdict"] not in VALID_EVALUATION_VERDICTS:
        raise ValueError(
            f"Unsupported evaluation_verdict: {payload['evaluation_verdict']}"
        )
    if not isinstance(payload["invalid_run"], bool):
        raise ValueError("invalid_run must be a boolean.")

    vio_metrics = payload["vio_metrics"]
    if not isinstance(vio_metrics, dict):
        raise ValueError("vio_metrics must be a mapping.")
    vio_missing = VIO_METRIC_FIELDS.difference(vio_metrics)
    if vio_missing:
        missing_list = ", ".join(sorted(vio_missing))
        raise ValueError(f"vio_metrics missing required fields: {missing_list}")
    _validate_reason_code_list(vio_metrics["reason_codes"], "vio_metrics.reason_codes")

    if payload["schema_version"] != REPORT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported report schema_version: {payload['schema_version']}"
        )


def validate_summary(payload: dict[str, Any]) -> None:
    missing = REQUIRED_SUMMARY_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Summary missing required fields: {missing_list}")

    if payload["schema_version"] != SUMMARY_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported summary schema_version: {payload['schema_version']}"
        )
    scenarios = payload["scenarios"]
    if not isinstance(scenarios, list):
        raise ValueError("summary.scenarios must be a list.")
    evaluation_profiles = payload["evaluation_profiles"]
    if not isinstance(evaluation_profiles, list) or not evaluation_profiles:
        raise ValueError("summary.evaluation_profiles must be a non-empty list.")
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("summary.scenarios entries must be mappings.")
        missing_fields = REQUIRED_SUMMARY_SCENARIO_FIELDS.difference(scenario)
        if missing_fields:
            missing_list = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"summary scenario missing required fields: {missing_list}"
            )
        _validate_reason_code(scenario["trust_primary_reason_code"])
        _validate_reason_code(scenario["mission_primary_reason_code"])
        _validate_reason_code(scenario["ew_primary_reason_code"])
        _validate_reason_code(scenario["tactical_primary_reason_code"])
        _validate_reason_code(scenario["tactical_advisory_code"])
        _validate_reason_code(scenario["evaluation_primary_reason_code"])
        if not isinstance(scenario["tactical_summary_text"], str) or not scenario["tactical_summary_text"].strip():
            raise ValueError("summary tactical_summary_text must be non-empty.")
        if not isinstance(scenario["tactical_summary_path"], str) or not scenario["tactical_summary_path"].strip():
            raise ValueError("summary tactical_summary_path must be non-empty.")
        if scenario["evaluation_verdict"] not in VALID_EVALUATION_VERDICTS:
            raise ValueError(
                f"Unsupported summary evaluation_verdict: {scenario['evaluation_verdict']}"
            )
        if not isinstance(scenario["deterministic_replay_passed"], bool):
            raise ValueError(
                "summary deterministic_replay_passed must be a boolean."
            )
        if not isinstance(scenario["invalid_run"], bool):
            raise ValueError("summary invalid_run must be a boolean.")


def validate_ew_risk_map(payload: dict[str, Any]) -> None:
    missing = REQUIRED_EW_RISK_MAP_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"EW risk map missing required fields: {missing_list}")

    if payload["schema_version"] != EW_RISK_MAP_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported ew risk map schema_version: {payload['schema_version']}"
        )

    origin = payload["origin"]
    if not isinstance(origin, dict):
        raise ValueError("ew_risk_map.origin must be a mapping.")
    if {"x_m", "y_m"}.difference(origin):
        raise ValueError("ew_risk_map.origin requires x_m and y_m.")

    width_cells = payload["width_cells"]
    height_cells = payload["height_cells"]
    if not isinstance(width_cells, int) or width_cells <= 0:
        raise ValueError("ew_risk_map.width_cells must be a positive integer.")
    if not isinstance(height_cells, int) or height_cells <= 0:
        raise ValueError("ew_risk_map.height_cells must be a positive integer.")

    risk_cells = payload["risk_cells"]
    if not isinstance(risk_cells, list):
        raise ValueError("ew_risk_map.risk_cells must be a list.")
    expected_length = width_cells * height_cells
    if len(risk_cells) != expected_length:
        raise ValueError(
            "ew_risk_map.risk_cells length must equal width_cells * height_cells."
        )
    for value in risk_cells:
        if not isinstance(value, (int, float)):
            raise ValueError("ew_risk_map.risk_cells entries must be numeric.")

    _validate_reason_code(payload["primary_reason_code"])
    _validate_reason_code_list(payload["reason_codes"], "ew_risk_map.reason_codes")
    _validate_reason_code_list(payload["evidence_codes"], "ew_risk_map.evidence_codes")

    if not isinstance(payload["affected_cell_count"], int) or payload["affected_cell_count"] < 0:
        raise ValueError("ew_risk_map.affected_cell_count must be a non-negative integer.")
    if not isinstance(payload["risk_cells_hash"], str) or not payload["risk_cells_hash"].strip():
        raise ValueError("ew_risk_map.risk_cells_hash must be a non-empty string.")


def validate_ew_metrics_bundle(payload: dict[str, Any]) -> None:
    missing = REQUIRED_EW_METRICS_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"EW metrics bundle missing required fields: {missing_list}")

    if payload["schema_version"] != EW_METRICS_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported ew metrics schema_version: {payload['schema_version']}"
        )
    if not isinstance(payload["checks_snapshot"], list):
        raise ValueError("ew_metrics.checks_snapshot must be a list.")
    scenarios = payload["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("ew_metrics.scenarios must be a non-empty list.")
    required_scenario_fields = {
        "scenario_id",
        "ew_risk_level",
        "max_risk",
        "affected_cell_count",
        "corridor_cost",
        "primary_reason_code",
        "risk_cells_hash",
        "failed_checks",
    }
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("ew_metrics.scenarios entries must be mappings.")
        missing_fields = required_scenario_fields.difference(scenario)
        if missing_fields:
            missing_list = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"ew_metrics scenario missing required fields: {missing_list}"
            )
        if scenario["ew_risk_level"] not in VALID_EW_RISK_LEVELS:
            raise ValueError(
                f"Unsupported ew_metrics ew_risk_level: {scenario['ew_risk_level']}"
            )
        _validate_reason_code(scenario["primary_reason_code"])
        if not isinstance(scenario["failed_checks"], list):
            raise ValueError("ew_metrics.failed_checks must be a list.")


def validate_tactical_summary(payload: dict[str, Any]) -> None:
    missing = REQUIRED_TACTICAL_SUMMARY_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Tactical summary missing required fields: {missing_list}")

    if payload["schema_version"] != TACTICAL_SUMMARY_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported tactical summary schema_version: {payload['schema_version']}"
        )
    if payload["mission_state"] not in VALID_MISSION_STATES:
        raise ValueError(f"Unsupported tactical mission_state: {payload['mission_state']}")
    if payload["localization_mode"] not in VALID_LOCALIZATION_MODES:
        raise ValueError(
            f"Unsupported tactical localization_mode: {payload['localization_mode']}"
        )
    if payload["ew_risk_level"] not in VALID_EW_RISK_LEVELS:
        raise ValueError(
            f"Unsupported tactical ew_risk_level: {payload['ew_risk_level']}"
        )
    if not isinstance(payload["affected_area_count"], int) or payload["affected_area_count"] < 0:
        raise ValueError("tactical affected_area_count must be a non-negative integer.")
    _validate_reason_code(payload["primary_reason_code"])
    _validate_reason_code_list(payload["reason_codes"], "tactical_summary.reason_codes")
    _validate_reason_code(payload["advisory_code"])
    if not isinstance(payload["advisory_text"], str) or not payload["advisory_text"].strip():
        raise ValueError("tactical_summary.advisory_text must be a non-empty string.")
    if not isinstance(payload["summary_text"], str) or not payload["summary_text"].strip():
        raise ValueError("tactical_summary.summary_text must be a non-empty string.")


def validate_tactical_summary_bundle(payload: dict[str, Any]) -> None:
    missing = REQUIRED_TACTICAL_SUMMARY_BUNDLE_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(
            f"Tactical summary bundle missing required fields: {missing_list}"
        )
    if payload["schema_version"] != TACTICAL_SUMMARY_BUNDLE_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported tactical summary bundle schema_version: "
            f"{payload['schema_version']}"
        )
    if not isinstance(payload["checks_snapshot"], list):
        raise ValueError("tactical_summary_bundle.checks_snapshot must be a list.")
    scenarios = payload["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("tactical_summary_bundle.scenarios must be a non-empty list.")
    required_scenario_fields = {
        "scenario_id",
        "mission_state",
        "tactical_primary_reason_code",
        "tactical_advisory_code",
        "tactical_summary_text",
        "tactical_summary_path",
        "failed_checks",
    }
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise ValueError("tactical summary bundle scenarios must be mappings.")
        missing_fields = required_scenario_fields.difference(scenario)
        if missing_fields:
            missing_list = ", ".join(sorted(missing_fields))
            raise ValueError(
                "tactical summary bundle scenario missing required fields: "
                f"{missing_list}"
            )
        if scenario["mission_state"] not in VALID_MISSION_STATES:
            raise ValueError(
                f"Unsupported tactical bundle mission_state: {scenario['mission_state']}"
            )
        _validate_reason_code(scenario["tactical_primary_reason_code"])
        _validate_reason_code(scenario["tactical_advisory_code"])
        if not isinstance(scenario["tactical_summary_text"], str) or not scenario["tactical_summary_text"].strip():
            raise ValueError(
                "tactical summary bundle tactical_summary_text must be non-empty."
            )
        if not isinstance(scenario["tactical_summary_path"], str) or not scenario["tactical_summary_path"].strip():
            raise ValueError(
                "tactical summary bundle tactical_summary_path must be non-empty."
            )
        if not isinstance(scenario["failed_checks"], list):
            raise ValueError(
                "tactical summary bundle failed_checks must be a list."
            )


def validate_runtime_trace(payload: dict[str, Any]) -> None:
    missing = REQUIRED_RUNTIME_TRACE_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Runtime trace missing required fields: {missing_list}")
    if payload["schema_version"] != RUNTIME_TRACE_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported runtime trace schema_version: {payload['schema_version']}"
        )
    entries = payload["entries"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("runtime_trace.entries must be a non-empty list.")
    for entry in entries:
        _validate_runtime_trace_entry(entry)


def validate_truth_trace(payload: dict[str, Any]) -> None:
    missing = REQUIRED_TRUTH_TRACE_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Truth trace missing required fields: {missing_list}")
    if payload["schema_version"] != TRUTH_TRACE_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported truth trace schema_version: {payload['schema_version']}"
        )
    entries = payload["entries"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("truth_trace.entries must be a non-empty list.")
    for entry in entries:
        _validate_truth_trace_entry(entry)


def validate_replay_results_bundle(payload: dict[str, Any]) -> None:
    missing = REQUIRED_REPLAY_RESULTS_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Replay results missing required fields: {missing_list}")
    if payload["schema_version"] != REPLAY_RESULTS_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported replay_results schema_version: {payload['schema_version']}"
        )
    scenarios = payload["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("replay_results.scenarios must be a non-empty list.")
    for scenario in scenarios:
        required_fields = {"scenario_id", "replay_result", "divergence"}
        missing_fields = required_fields.difference(scenario)
        if missing_fields:
            raise ValueError(
                "replay_results scenario missing required fields: "
                + ", ".join(sorted(missing_fields))
            )
        if scenario["replay_result"] not in {"PASS", "FAIL", "INVALID"}:
            raise ValueError(
                f"Unsupported replay_result: {scenario['replay_result']}"
            )


def validate_evaluation_metrics_bundle(payload: dict[str, Any]) -> None:
    missing = REQUIRED_EVALUATION_METRICS_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(
            f"Evaluation metrics bundle missing required fields: {missing_list}"
        )
    if payload["schema_version"] != EVALUATION_METRICS_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported evaluation_metrics schema_version: "
            f"{payload['schema_version']}"
        )
    scenarios = payload["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("evaluation_metrics.scenarios must be a non-empty list.")
    required_fields = {
        "scenario_id",
        "evaluation_profile",
        "metrics",
        "failed_metrics",
    }
    metric_names = {
        "ATE_RMSE_M",
        "RPE_RMSE_M",
        "DRIFT_PCT",
        "LOCALIZATION_CONTINUITY_PCT",
        "FALLBACK_REACTION_TIME_S",
        "MISSION_SUCCESS",
    }
    for scenario in scenarios:
        missing_fields = required_fields.difference(scenario)
        if missing_fields:
            raise ValueError(
                "evaluation_metrics scenario missing required fields: "
                + ", ".join(sorted(missing_fields))
            )
        if not isinstance(scenario["metrics"], dict):
            raise ValueError("evaluation_metrics.metrics must be a mapping.")
        missing_metrics = metric_names.difference(scenario["metrics"])
        if missing_metrics:
            raise ValueError(
                "evaluation_metrics.metrics missing required metrics: "
                + ", ".join(sorted(missing_metrics))
            )
        if not isinstance(scenario["failed_metrics"], list):
            raise ValueError("evaluation_metrics.failed_metrics must be a list.")


def validate_evaluation_verdicts_bundle(payload: dict[str, Any]) -> None:
    missing = REQUIRED_EVALUATION_VERDICTS_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(
            f"Evaluation verdicts bundle missing required fields: {missing_list}"
        )
    if payload["schema_version"] != EVALUATION_VERDICTS_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported evaluation_verdicts schema_version: "
            f"{payload['schema_version']}"
        )
    scenarios = payload["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("evaluation_verdicts.scenarios must be a non-empty list.")
    required_fields = {
        "scenario_id",
        "evaluation_profile",
        "verdict",
        "primary_reason_code",
        "reason_codes",
        "mission_success",
        "invalid_run",
        "failed_checks",
    }
    for scenario in scenarios:
        missing_fields = required_fields.difference(scenario)
        if missing_fields:
            raise ValueError(
                "evaluation_verdicts scenario missing required fields: "
                + ", ".join(sorted(missing_fields))
            )
        if scenario["verdict"] not in {"PASS", "FAIL", "INVALID"}:
            raise ValueError(
                f"Unsupported evaluation verdict: {scenario['verdict']}"
            )
        _validate_reason_code(scenario["primary_reason_code"])
        _validate_reason_code_list(
            scenario["reason_codes"], "evaluation_verdicts.reason_codes"
        )
        if not isinstance(scenario["mission_success"], bool):
            raise ValueError("evaluation_verdicts.mission_success must be a boolean.")
        if not isinstance(scenario["invalid_run"], bool):
            raise ValueError("evaluation_verdicts.invalid_run must be a boolean.")
        if not isinstance(scenario["failed_checks"], list):
            raise ValueError("evaluation_verdicts.failed_checks must be a list.")


def validate_mission_audit(payload: dict[str, Any]) -> None:
    missing = REQUIRED_MISSION_AUDIT_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Mission audit missing required fields: {missing_list}")

    if payload["schema_version"] != MISSION_AUDIT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported mission audit schema_version: {payload['schema_version']}"
        )

    entries = payload["entries"]
    if not isinstance(entries, list) or not entries:
        raise ValueError("Mission audit entries must be a non-empty list.")

    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Mission audit entries must be mappings.")
        missing_entry_fields = MISSION_AUDIT_ENTRY_FIELDS.difference(entry)
        if missing_entry_fields:
            missing_list = ", ".join(sorted(missing_entry_fields))
            raise ValueError(
                f"Mission audit entry missing required fields: {missing_list}"
            )

        if entry["candidate_state"] not in VALID_MISSION_STATES:
            raise ValueError(
                f"Unsupported mission audit candidate_state: {entry['candidate_state']}"
            )
        if entry["final_state"] not in VALID_MISSION_STATES:
            raise ValueError(
                f"Unsupported mission audit final_state: {entry['final_state']}"
            )

        _validate_reason_code(entry["trust_primary_reason_code"])
        _validate_reason_code(entry["primary_reason_code"])
        _validate_reason_code_list(entry["reason_codes"], "mission_audit.reason_codes")

        if not isinstance(entry["tick_index"], int) or entry["tick_index"] < 0:
            raise ValueError("mission_audit.tick_index must be a non-negative integer.")
        if not isinstance(entry["transition_count"], int) or entry["transition_count"] < 0:
            raise ValueError(
                "mission_audit.transition_count must be a non-negative integer."
            )
        if not isinstance(entry["step_inputs"], dict):
            raise ValueError("mission_audit.step_inputs must be a mapping.")


def _validate_runtime_trace_entry(entry: dict[str, Any]) -> None:
    if not isinstance(entry, dict):
        raise ValueError("runtime_trace entries must be mappings.")
    missing_fields = RUNTIME_TRACE_ENTRY_FIELDS.difference(entry)
    if missing_fields:
        missing_list = ", ".join(sorted(missing_fields))
        raise ValueError(f"runtime_trace entry missing required fields: {missing_list}")
    if not isinstance(entry["tick_index"], int) or entry["tick_index"] < 0:
        raise ValueError("runtime_trace.tick_index must be a non-negative integer.")
    if entry["mission_state"] not in VALID_MISSION_STATES:
        raise ValueError(f"Unsupported runtime_trace mission_state: {entry['mission_state']}")
    if entry["localization_mode"] not in VALID_LOCALIZATION_MODES:
        raise ValueError(
            f"Unsupported runtime_trace localization_mode: {entry['localization_mode']}"
        )
    _validate_reason_code(entry["trust_primary_reason_code"])
    _validate_reason_code(entry["mission_primary_reason_code"])
    if not isinstance(entry["step_inputs"], dict):
        raise ValueError("runtime_trace.step_inputs must be a mapping.")
    _validate_position_mapping(
        entry["estimated_position_m"], "runtime_trace.estimated_position_m"
    )


def _validate_truth_trace_entry(entry: dict[str, Any]) -> None:
    if not isinstance(entry, dict):
        raise ValueError("truth_trace entries must be mappings.")
    missing_fields = TRUTH_TRACE_ENTRY_FIELDS.difference(entry)
    if missing_fields:
        missing_list = ", ".join(sorted(missing_fields))
        raise ValueError(f"truth_trace entry missing required fields: {missing_list}")
    if not isinstance(entry["tick_index"], int) or entry["tick_index"] < 0:
        raise ValueError("truth_trace.tick_index must be a non-negative integer.")
    _validate_position_mapping(entry["position_m"], "truth_trace.position_m")


def _validate_position_mapping(value: Any, field_name: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping.")
    missing = {"x", "y", "z"}.difference(value)
    if missing:
        raise ValueError(
            f"{field_name} missing required coordinates: {', '.join(sorted(missing))}"
        )


def _validate_reason_code(value: Any) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Primary reason code must be a non-empty string.")
    if not SNAKE_CASE_RE.fullmatch(value):
        raise ValueError(f"Reason code must be snake_case: {value!r}")


def _validate_reason_code_list(value: Any, field_name: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} entries must be strings.")
        if not SNAKE_CASE_RE.fullmatch(item):
            raise ValueError(f"{field_name} entries must be snake_case: {item!r}")
