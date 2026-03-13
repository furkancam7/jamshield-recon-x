from __future__ import annotations

import json
from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.artifact_schema import (
    EVALUATION_METRICS_SCHEMA_VERSION,
    EVALUATION_VERDICTS_SCHEMA_VERSION,
    REPLAY_RESULTS_SCHEMA_VERSION,
    RUNTIME_TRACE_SCHEMA_VERSION,
    TRUTH_TRACE_SCHEMA_VERSION,
    validate_evaluation_metrics_bundle,
    validate_evaluation_verdicts_bundle,
    validate_replay_results_bundle,
    validate_runtime_trace,
    validate_truth_trace,
)
from evaluation.profiles import DEFAULT_EVAL_CONFIG_PATH, load_evaluation_profiles
from logging_replay.replay import compare_replay_run


class ReplayEvaluationTests(unittest.TestCase):
    def test_load_evaluation_profiles_reads_named_profiles(self) -> None:
        profiles = load_evaluation_profiles(DEFAULT_EVAL_CONFIG_PATH)
        self.assertIn("baseline_nominal_profile_v1", profiles)
        self.assertTrue(profiles["denial_corridor_profile_v1"].require_mission_success)

    def test_trace_and_bundle_validators_accept_minimal_valid_payloads(self) -> None:
        runtime_trace = {
            "schema_version": RUNTIME_TRACE_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenario_id": "s1_nominal",
            "entries": [
                {
                    "tick_index": 0,
                    "timestamp_ns": 0,
                    "step_inputs": {"gnss_condition": "nominal"},
                    "gnss_state": "nominal",
                    "gnss_trust": 0.95,
                    "vio_trust": 0.94,
                    "effective_vio_state": "good",
                    "sync_quality": 1.0,
                    "localization_mode": "GNSS_PRIMARY",
                    "localization_confidence": 0.95,
                    "mission_confidence": 0.96,
                    "trust_primary_reason_code": "trust_inputs_nominal",
                    "mission_state": "MISSION_EXECUTE",
                    "mission_primary_reason_code": "mission_execute_nominal",
                    "estimated_position_m": {"x": 0.5, "y": 0.0, "z": 30.0},
                    "route_progress_pct": 0.0,
                }
            ],
        }
        truth_trace = {
            "schema_version": TRUTH_TRACE_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenario_id": "s1_nominal",
            "entries": [
                {
                    "tick_index": 0,
                    "timestamp_ns": 0,
                    "position_m": {"x": 0.0, "y": 0.0, "z": 30.0},
                    "route_progress_pct": 0.0,
                }
            ],
        }
        replay_bundle = {
            "schema_version": REPLAY_RESULTS_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenarios": [
                {"scenario_id": "s1_nominal", "replay_result": "PASS", "divergence": None}
            ],
        }
        metrics_bundle = {
            "schema_version": EVALUATION_METRICS_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "evaluation_profile": "baseline_nominal_profile_v1",
                    "metrics": {
                        "ATE_RMSE_M": 0.5,
                        "RPE_RMSE_M": 0.1,
                        "DRIFT_PCT": 0.4,
                        "LOCALIZATION_CONTINUITY_PCT": 100.0,
                        "FALLBACK_REACTION_TIME_S": 0.0,
                        "MISSION_SUCCESS": True,
                    },
                    "failed_metrics": [],
                }
            ],
        }
        verdicts_bundle = {
            "schema_version": EVALUATION_VERDICTS_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "evaluation_profile": "baseline_nominal_profile_v1",
                    "verdict": "PASS",
                    "primary_reason_code": "evaluation_acceptance_passed",
                    "reason_codes": ["evaluation_acceptance_passed"],
                    "mission_success": True,
                    "invalid_run": False,
                    "failed_checks": [],
                }
            ],
        }

        validate_runtime_trace(runtime_trace)
        validate_truth_trace(truth_trace)
        validate_replay_results_bundle(replay_bundle)
        validate_evaluation_metrics_bundle(metrics_bundle)
        validate_evaluation_verdicts_bundle(verdicts_bundle)

    def test_compare_replay_run_returns_fail_on_first_divergence(self) -> None:
        original_dir = make_temp_dir(self)
        replay_dir = make_temp_dir(self)
        scenario_id = "s1_nominal"
        self._write_replay_fixture(original_dir, scenario_id, mission_state="MISSION_EXECUTE")
        self._write_replay_fixture(replay_dir, scenario_id, mission_state="MISSION_ABORT")

        result = compare_replay_run(
            scenario_id=scenario_id,
            original_run_dir=original_dir,
            replay_run_dir=replay_dir,
        )

        self.assertEqual(result["replay_result"], "FAIL")
        self.assertIn("runtime_trace", result["divergence"]["field_name"])

    def _write_replay_fixture(
        self,
        directory: Path,
        scenario_id: str,
        *,
        mission_state: str,
    ) -> None:
        runtime_trace = {
            "schema_version": "1.0",
            "run_id": "run_001",
            "scenario_id": scenario_id,
            "entries": [
                {
                    "tick_index": 0,
                    "timestamp_ns": 0,
                    "step_inputs": {"gnss_condition": "nominal"},
                    "gnss_state": "nominal",
                    "gnss_trust": 0.95,
                    "vio_trust": 0.94,
                    "effective_vio_state": "good",
                    "sync_quality": 1.0,
                    "localization_mode": "GNSS_PRIMARY",
                    "localization_confidence": 0.95,
                    "mission_confidence": 0.96,
                    "trust_primary_reason_code": "trust_inputs_nominal",
                    "mission_state": mission_state,
                    "mission_primary_reason_code": "mission_execute_nominal",
                    "estimated_position_m": {"x": 0.5, "y": 0.0, "z": 30.0},
                    "route_progress_pct": 0.0,
                }
            ],
        }
        audit = {
            "schema_version": "1.0",
            "run_id": "run_001",
            "scenario_id": scenario_id,
            "entries": [
                {
                    "tick_index": 0,
                    "step_inputs": {"gnss_condition": "nominal"},
                    "gnss_state": "nominal",
                    "mission_confidence": 0.96,
                    "effective_vio_state": "good",
                    "trust_primary_reason_code": "trust_inputs_nominal",
                    "candidate_state": mission_state,
                    "final_state": mission_state,
                    "primary_reason_code": "mission_execute_nominal",
                    "reason_codes": ["mission_execute_nominal"],
                    "transition_count": 0,
                }
            ],
        }
        report = {
            "schema_version": "2.4",
            "run_id": "run_001",
            "scenario_id": scenario_id,
            "map_name": "open_field",
            "run_seed": 111,
            "gnss_condition": "nominal",
            "gnss_state": "nominal",
            "gnss_trust": 0.95,
            "vio_trust": 0.94,
            "sync_quality": 1.0,
            "mission_confidence": 0.96,
            "trust_primary_reason_code": "trust_inputs_nominal",
            "trust_reason_codes": [],
            "mission_state": mission_state,
            "mission_primary_reason_code": "mission_execute_nominal",
            "mission_reason_codes": ["mission_execute_nominal"],
            "mission_transition_count": 0,
            "mission_audit_path": str(directory / f"{scenario_id}_mission_audit.json"),
            "ew_risk_level": "none",
            "ew_primary_reason_code": "ew_risk_nominal",
            "ew_reason_codes": [],
            "ew_max_risk": 0.0,
            "ew_affected_cell_count": 0,
            "ew_corridor_cost": 0.0,
            "ew_risk_map_path": str(directory / f"{scenario_id}_ew_risk_map.json"),
            "tactical_primary_reason_code": "tactical_nominal_overview",
            "tactical_reason_codes": ["tactical_nominal_overview"],
            "tactical_advisory_code": "operator_continue_nominal",
            "tactical_advisory_text": "Continue mission on the current route.",
            "tactical_summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
            "tactical_summary_path": str(directory / f"{scenario_id}_tactical_summary.json"),
            "runtime_trace_path": str(directory / f"{scenario_id}_runtime_trace.json"),
            "truth_trace_path": str(directory / f"{scenario_id}_truth_trace.json"),
            "vio_state": "good",
            "vio_health_score": 0.94,
            "effective_vio_state": "good",
            "ate_m": 0.5,
            "route_length_m": 120.0,
            "ground_truth_usage": "evaluation_only",
            "config_id": "sim-v1",
            "manifest_hash": "abc123",
            "config_hash": "def456",
            "evaluation_profile": "baseline_nominal_profile_v1",
            "deterministic_replay_passed": False,
            "evaluation_verdict": "PENDING",
            "invalid_run": False,
            "evaluation_primary_reason_code": "evaluation_pending",
            "software_revision": "rev",
            "timestamp": "2026-03-13T10:00:00Z",
            "scenario_metadata": {
                "title": "Nominal",
                "description": "Fixture",
                "owner": "test-suite",
            },
            "vio_metrics_source": "pipeline_v1",
            "vio_metrics": {
                "timestamp_ns": 0,
                "profile_id": "nominal_v1",
                "feature_count": 24,
                "matched_feature_count": 22,
                "track_continuity": 0.9,
                "reprojection_error_px": 0.1,
                "pose_delta_xy_m": 0.2,
                "yaw_delta_rad": 0.1,
                "imu_alignment_error": 0.02,
                "vio_health_score": 0.94,
                "vio_state": "good",
                "effective_vio_state": "good",
                "reason_codes": [],
            },
            "localization_mode": "GNSS_PRIMARY",
            "localization_confidence": 0.95,
            "gnss_weight": 0.6,
            "vio_weight": 0.4,
        }
        ew_map = {
            "schema_version": "1.0",
            "run_id": "run_001",
            "scenario_id": scenario_id,
            "timestamp_ns": 0,
            "frame_id": "map",
            "cell_size_m": 20.0,
            "width_cells": 1,
            "height_cells": 1,
            "origin": {"x_m": 0.0, "y_m": 0.0},
            "risk_cells": [0.0],
            "evidence_codes": [],
            "primary_reason_code": "ew_risk_nominal",
            "reason_codes": [],
            "max_risk": 0.0,
            "affected_cell_count": 0,
            "corridor_cost": 0.0,
            "risk_cells_hash": "hash",
        }
        tactical = {
            "schema_version": "1.0",
            "run_id": "run_001",
            "scenario_id": scenario_id,
            "timestamp_ns": 0,
            "mission_state": mission_state,
            "mission_confidence": 0.96,
            "localization_mode": "GNSS_PRIMARY",
            "ew_risk_level": "none",
            "affected_area_count": 0,
            "ew_corridor_cost": 0.0,
            "primary_reason_code": "tactical_nominal_overview",
            "reason_codes": ["tactical_nominal_overview"],
            "advisory_code": "operator_continue_nominal",
            "advisory_text": "Continue mission on the current route.",
            "summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
        }
        truth_trace = {
            "schema_version": "1.0",
            "run_id": "run_001",
            "scenario_id": scenario_id,
            "entries": [
                {
                    "tick_index": 0,
                    "timestamp_ns": 0,
                    "position_m": {"x": 0.0, "y": 0.0, "z": 30.0},
                    "route_progress_pct": 0.0,
                }
            ],
        }
        for stem, payload in (
            ("runtime_trace", runtime_trace),
            ("mission_audit", audit),
            ("report", report),
            ("ew_risk_map", ew_map),
            ("tactical_summary", tactical),
            ("truth_trace", truth_trace),
        ):
            (directory / f"{scenario_id}_{stem}.json").write_text(
                json.dumps(payload, indent=2, sort_keys=True),
                encoding="utf-8",
            )


if __name__ == "__main__":
    unittest.main()
