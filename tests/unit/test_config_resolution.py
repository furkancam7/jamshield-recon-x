from pathlib import Path
import unittest

from _support import make_temp_dir
from common.config import load_app_config, resolve_app_config


BASE_CONFIG = """
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

SCENARIO_OVERRIDE = """
gnss_trust:
  degraded_trust_threshold: 0.6
trust_engine:
  sync_low_threshold: 0.4
mission:
  degraded_confidence_threshold: 0.45
  recovery_dwell_ticks: 3
vio_pipeline:
  match_distance_px: 3.5
"""

CLI_OVERRIDE = """
gnss_trust:
  degraded_trust_threshold: 0.33
trust_engine:
  mode_unstable_penalty: 0.02
vio_trust:
  feature_count_floor: 10
"""

INVALID_OVERRIDE = """
trust_engine:
  future_only_field: 1.0
"""


class ConfigResolutionTests(unittest.TestCase):
    def test_base_only_resolution_matches_base_config(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)

        self.assertEqual(resolve_app_config(base_path), load_app_config(base_path))

    def test_scenario_override_applies_after_base_config(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)
        scenario_override_path = self._write_file(
            str(temp_dir),
            "scenario-override.yaml",
            SCENARIO_OVERRIDE,
        )

        config = resolve_app_config(
            base_path=base_path,
            scenario_override_path=scenario_override_path,
        )

        self.assertEqual(config.gnss_trust.degraded_trust_threshold, 0.6)
        self.assertEqual(config.mission.degraded_confidence_threshold, 0.45)
        self.assertEqual(config.mission.recovery_dwell_ticks, 3)
        self.assertEqual(config.trust_engine.sync_low_threshold, 0.4)
        self.assertEqual(config.trust_engine.mode_unstable_penalty, 0.05)
        self.assertEqual(config.vio_pipeline.match_distance_px, 3.5)

    def test_cli_override_takes_precedence_over_scenario_override(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)
        scenario_override_path = self._write_file(
            str(temp_dir),
            "scenario-override.yaml",
            SCENARIO_OVERRIDE,
        )
        cli_override_path = self._write_file(
            str(temp_dir),
            "cli-override.yaml",
            CLI_OVERRIDE,
        )

        config = resolve_app_config(
            base_path=base_path,
            scenario_override_path=scenario_override_path,
            cli_override_path=cli_override_path,
        )

        self.assertEqual(config.gnss_trust.degraded_trust_threshold, 0.33)
        self.assertEqual(config.trust_engine.mode_unstable_penalty, 0.02)
        self.assertEqual(config.mission.degraded_confidence_threshold, 0.45)
        self.assertEqual(config.vio_trust.feature_count_floor, 10)

    def test_resolution_rejects_unknown_override_fields(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)
        invalid_override_path = self._write_file(
            str(temp_dir),
            "invalid-override.yaml",
            INVALID_OVERRIDE,
        )

        with self.assertRaisesRegex(ValueError, "Unknown config override field"):
            resolve_app_config(
                base_path=base_path,
                scenario_override_path=invalid_override_path,
            )

    def test_resolution_is_deterministic_for_same_inputs(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)
        scenario_override_path = self._write_file(
            str(temp_dir),
            "scenario-override.yaml",
            SCENARIO_OVERRIDE,
        )
        cli_override_path = self._write_file(
            str(temp_dir),
            "cli-override.yaml",
            CLI_OVERRIDE,
        )

        first = resolve_app_config(
            base_path=base_path,
            scenario_override_path=scenario_override_path,
            cli_override_path=cli_override_path,
        )
        second = resolve_app_config(
            base_path=base_path,
            scenario_override_path=scenario_override_path,
            cli_override_path=cli_override_path,
        )

        self.assertEqual(first, second)

    def _write_file(self, directory: str, name: str, contents: str) -> Path:
        path = Path(directory) / name
        path.write_text(contents.lstrip(), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
