from pathlib import Path
import unittest

from _support import make_temp_dir
from common.config import (
    AppConfig,
    GnssTrustConfig,
    MissionConfig,
    TrustEngineConfig,
    VioHealthConfig,
    VioPipelineConfig,
    VioTrustConfig,
    load_app_config,
)
from evaluation.artifact_schema import (
    REPORT_SCHEMA_VERSION,
    SUMMARY_SCHEMA_VERSION,
    validate_report,
    validate_summary,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"

VALID_CONFIG = """
config_id: sim-v1
schema_version: "2.0"
gnss_trust:
  quality_weight: 0.8
  availability_weight: 0.2
  denied_outage_ratio_threshold: 0.8
  denied_trust_threshold: 0.25
  degraded_trust_threshold: 0.75
trust_engine:
  gnss_trust_weight: 0.45
  localization_confidence_weight: 0.30
  vio_trust_weight: 0.20
  sync_quality_weight: 0.05
  gnss_low_threshold: 0.45
  localization_low_threshold: 0.55
  vio_low_threshold: 0.55
  sync_low_threshold: 0.60
  default_sync_quality: 1.0
  mode_unstable_penalty: 0.05
  effective_vio_weak_penalty: 0.04
  effective_vio_lost_penalty: 0.06
  calibration_high_floor: 0.75
  calibration_medium_floor: 0.45
mission:
  nominal_confidence_threshold: 0.8
  degraded_confidence_threshold: 0.5
  denied_fallback_confidence_threshold: 0.28
  emergency_land_confidence_threshold: 0.2
  denied_allowed_states:
    - MISSION_FALLBACK
    - MISSION_SAFE_HOLD
    - MISSION_ABORT
  recovery_dwell_ticks: 2
  safe_hold_escalation_ticks: 3
  oscillation_window_ticks: 5
  max_state_transitions_in_window: 2
vio_health:
  good_threshold: 0.75
  weak_threshold: 0.40
vio_pipeline:
  max_features: 24
  gradient_threshold: 0.15
  match_distance_px: 4.0
  continuity_window: 12
  imu_gain: 0.85
vio_trust:
  feature_count_floor: 12
  track_continuity_floor: 0.50
  reprojection_error_ceiling_px: 2.00
  imu_alignment_ceiling: 0.50
  metric_weights:
    feature_count: 0.25
    track_continuity: 0.35
    reprojection_error: 0.25
    imu_alignment: 0.15
localization_fusion:
  gnss_base_weight: 0.6
  vio_base_weight: 0.4
  fused_confidence_floor: 0.7
  hysteresis_ticks: 3
ew_risk_map:
  cell_size_m: 20.0
  grid_padding_m: 20.0
  stamp_radius_m: 25.0
  global_decay_per_tick: 0.15
  corridor_sample_step_m: 10.0
  corridor_band_half_width_m: 15.0
  risk_low_floor: 0.25
  risk_medium_floor: 0.55
  weight_gnss_denied: 0.70
  weight_gnss_degraded: 0.35
  weight_sync_low: 0.20
  weight_localization_unstable: 0.25
"""


class ConfigAndArtifactTests(unittest.TestCase):
    def test_app_config_loads_expected_defaults(self) -> None:
        config = load_app_config(CONFIG_PATH)

        self.assertIsInstance(config, AppConfig)
        self.assertIsInstance(config.gnss_trust, GnssTrustConfig)
        self.assertIsInstance(config.trust_engine, TrustEngineConfig)
        self.assertIsInstance(config.mission, MissionConfig)
        self.assertIsInstance(config.vio_health, VioHealthConfig)
        self.assertIsInstance(config.vio_pipeline, VioPipelineConfig)
        self.assertIsInstance(config.vio_trust, VioTrustConfig)
        self.assertEqual(config.config_id, "sim-v1")
        self.assertEqual(config.schema_version, "2.0")
        self.assertEqual(config.trust_engine.gnss_trust_weight, 0.45)
        self.assertEqual(config.trust_engine.sync_low_threshold, 0.60)
        self.assertEqual(config.mission.denied_allowed_states[-1], "MISSION_ABORT")
        self.assertEqual(config.mission.recovery_dwell_ticks, 2)
        self.assertEqual(config.ew_risk_map.cell_size_m, 20.0)

    def test_invalid_config_missing_required_field_fails_validation(self) -> None:
        config_path = self._write_config(
            """
config_id: sim-v1
schema_version: "2.0"
gnss_trust:
  quality_weight: 0.8
  availability_weight: 0.2
  denied_outage_ratio_threshold: 0.8
  denied_trust_threshold: 0.25
  degraded_trust_threshold: 0.75
"""
        )

        with self.assertRaisesRegex(ValueError, "required fields"):
            load_app_config(config_path)

    def test_invalid_config_rejects_blank_identifiers(self) -> None:
        config_path = self._write_config(
            VALID_CONFIG.replace('config_id: sim-v1', 'config_id: "  "')
        )

        with self.assertRaisesRegex(ValueError, "non-empty string"):
            load_app_config(config_path)

    def test_invalid_config_rejects_non_numeric_thresholds(self) -> None:
        config_path = self._write_config(
            VALID_CONFIG.replace("gnss_trust_weight: 0.45", "gnss_trust_weight: nope")
        )

        with self.assertRaisesRegex(ValueError, "must be numeric"):
            load_app_config(config_path)

    def test_invalid_config_rejects_invalid_denied_allowed_states(self) -> None:
        config_path = self._write_config(
            VALID_CONFIG.replace("- MISSION_ABORT", '- ""')
        )

        with self.assertRaisesRegex(ValueError, "non-empty strings"):
            load_app_config(config_path)

    def test_report_validation_rejects_legacy_values_and_uppercase_reason_codes(self) -> None:
        payload = self._valid_report_payload()

        for field_name, invalid_value in (
            ("mission_state", "MISSION_NORMAL"),
            ("localization_mode", "FUSED"),
            ("trust_primary_reason_code", "SYNC_QUALITY_LOW"),
            ("mission_primary_reason_code", "MISSION_ABORT_VIO_LOST"),
        ):
            with self.subTest(field_name=field_name, invalid_value=invalid_value):
                invalid_payload = dict(payload)
                invalid_payload[field_name] = invalid_value
                with self.assertRaises(ValueError):
                    validate_report(invalid_payload)

        invalid_reason_list_payload = dict(payload)
        invalid_reason_list_payload["trust_reason_codes"] = ["SYNC_QUALITY_LOW"]
        with self.assertRaises(ValueError):
            validate_report(invalid_reason_list_payload)

        invalid_mission_reason_list_payload = dict(payload)
        invalid_mission_reason_list_payload["mission_reason_codes"] = [
            "MISSION_ABORT_VIO_LOST"
        ]
        with self.assertRaises(ValueError):
            validate_report(invalid_mission_reason_list_payload)

        invalid_vio_reason_payload = dict(payload)
        invalid_vio_reason_payload["vio_metrics"] = dict(payload["vio_metrics"])
        invalid_vio_reason_payload["vio_metrics"]["reason_codes"] = ["TRACK_LOST"]
        with self.assertRaises(ValueError):
            validate_report(invalid_vio_reason_payload)

    def test_summary_schema_version_is_2_4(self) -> None:
        summary = {
            "schema_version": SUMMARY_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenario_ids": ["s1_nominal"],
            "scenarios": [
                {
                    "scenario_id": "s1_nominal",
                    "gnss_state": "nominal",
                    "gnss_trust": 0.96,
                    "vio_trust": 0.94,
                    "sync_quality": 1.0,
                    "mission_confidence": 0.97,
                    "trust_primary_reason_code": "trust_inputs_nominal",
                    "mission_primary_reason_code": "mission_execute_nominal",
                    "mission_transition_count": 0,
                    "ew_risk_level": "none",
                    "ew_primary_reason_code": "ew_risk_nominal",
                    "ew_max_risk": 0.0,
                    "ew_affected_cell_count": 0,
                    "ew_corridor_cost": 0.0,
                    "ew_risk_map_path": "artifacts/runs/run_001/s1_nominal_ew_risk_map.json",
                    "tactical_primary_reason_code": "tactical_nominal_overview",
                    "tactical_advisory_code": "operator_continue_nominal",
                    "tactical_summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
                    "tactical_summary_path": "artifacts/runs/run_001/s1_nominal_tactical_summary.json",
                    "manifest_hash": "abc123",
                    "config_hash": "def456",
                    "evaluation_profile": "baseline_nominal_profile_v1",
                    "deterministic_replay_passed": True,
                    "evaluation_verdict": "PASS",
                    "invalid_run": False,
                    "evaluation_primary_reason_code": "evaluation_acceptance_passed",
                    "mission_state": "MISSION_EXECUTE",
                    "effective_vio_state": "good",
                    "vio_profile_id": "nominal_v1",
                    "localization_mode": "GNSS_PRIMARY",
                    "localization_confidence": 0.95,
                    "ate_rmse": 0.5,
                    "mission_audit_path": "artifacts/runs/run_001/s1_nominal_mission_audit.json",
                    "timestamp": "2026-03-13T10:00:00Z",
                }
            ],
            "checks": [],
            "overall_regression_result": "PASS",
            "config_id": "sim-v1",
            "evaluation_profiles": ["baseline_nominal_profile_v1"],
            "software_revision": "test-revision",
            "generated_at": "2026-03-13T10:00:00Z",
        }

        validate_summary(summary)
        self.assertEqual(REPORT_SCHEMA_VERSION, "2.4")
        self.assertEqual(SUMMARY_SCHEMA_VERSION, "2.4")

    def _valid_report_payload(self) -> dict:
        return {
            "schema_version": REPORT_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenario_id": "s1_nominal",
            "map_name": "open_field",
            "run_seed": 111,
            "gnss_condition": "nominal",
            "gnss_state": "nominal",
            "gnss_trust": 0.96,
            "vio_trust": 0.94,
            "sync_quality": 1.0,
            "mission_confidence": 0.97,
            "trust_primary_reason_code": "trust_inputs_nominal",
            "trust_reason_codes": [],
            "mission_primary_reason_code": "mission_execute_nominal",
            "mission_reason_codes": ["mission_execute_nominal"],
            "mission_transition_count": 0,
            "mission_audit_path": "artifacts/runs/run_001/s1_nominal_mission_audit.json",
            "ew_risk_level": "none",
            "ew_primary_reason_code": "ew_risk_nominal",
            "ew_reason_codes": [],
            "ew_max_risk": 0.0,
            "ew_affected_cell_count": 0,
            "ew_corridor_cost": 0.0,
            "ew_risk_map_path": "artifacts/runs/run_001/s1_nominal_ew_risk_map.json",
            "tactical_primary_reason_code": "tactical_nominal_overview",
            "tactical_reason_codes": ["tactical_nominal_overview"],
            "tactical_advisory_code": "operator_continue_nominal",
            "tactical_advisory_text": "Continue mission on the current route.",
            "tactical_summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
            "tactical_summary_path": "artifacts/runs/run_001/s1_nominal_tactical_summary.json",
            "runtime_trace_path": "artifacts/runs/run_001/s1_nominal_runtime_trace.json",
            "truth_trace_path": "artifacts/runs/run_001/s1_nominal_truth_trace.json",
            "vio_state": "good",
            "vio_health_score": 0.94,
            "effective_vio_state": "good",
            "mission_state": "MISSION_EXECUTE",
            "ate_m": 0.5,
            "route_length_m": 123.246,
            "ground_truth_usage": "evaluation_only",
            "config_id": "sim-v1",
            "manifest_hash": "abc123",
            "config_hash": "def456",
            "evaluation_profile": "baseline_nominal_profile_v1",
            "deterministic_replay_passed": False,
            "evaluation_verdict": "PENDING",
            "invalid_run": False,
            "evaluation_primary_reason_code": "evaluation_pending",
            "software_revision": "test-revision",
            "timestamp": "2026-03-13T10:00:00Z",
            "scenario_metadata": {
                "title": "Nominal",
                "description": "Baseline test",
                "owner": "test-suite",
            },
            "localization_mode": "GNSS_PRIMARY",
            "localization_confidence": 0.95,
            "gnss_weight": 0.6,
            "vio_weight": 0.4,
            "vio_metrics_source": "pipeline_v1",
            "vio_metrics": {
                "timestamp_ns": 1,
                "profile_id": "nominal_v1",
                "feature_count": 24,
                "matched_feature_count": 22,
                "track_continuity": 0.917,
                "reprojection_error_px": 0.15,
                "pose_delta_xy_m": 0.34,
                "yaw_delta_rad": 0.08,
                "imu_alignment_error": 0.03,
                "vio_health_score": 0.94,
                "vio_state": "good",
                "effective_vio_state": "good",
                "reason_codes": [],
            },
        }

    def _write_config(self, contents: str) -> Path:
        temp_dir = make_temp_dir(self)
        path = temp_dir / "config.yaml"
        path.write_text(contents.lstrip(), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
