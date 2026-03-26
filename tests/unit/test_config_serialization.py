from pathlib import Path
import unittest

from _support import make_temp_dir
from common.config import (
    canonicalize_app_config,
    canonicalize_config_payload,
    load_app_config,
    resolve_app_config_payload,
    serialize_canonical_config,
)


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

REORDERED_BASE_CONFIG = """
schema_version: "2.0"
mission:
  denied_allowed_states:
    - MISSION_FALLBACK
    - MISSION_SAFE_HOLD
    - MISSION_ABORT
  emergency_land_confidence_threshold: 0.2
  degraded_confidence_threshold: 0.5
  max_state_transitions_in_window: 2
  nominal_confidence_threshold: 0.8
  oscillation_window_ticks: 5
  recovery_dwell_ticks: 2
  safe_hold_escalation_ticks: 3
  denied_fallback_confidence_threshold: 0.28
vio_health:
  weak_threshold: 0.40
  good_threshold: 0.75
vio_trust:
  imu_alignment_ceiling: 0.50
  feature_count_floor: 12
  metric_weights:
    imu_alignment: 0.15
    track_continuity: 0.35
    reprojection_error: 0.25
    feature_count: 0.25
  reprojection_error_ceiling_px: 2.00
  track_continuity_floor: 0.50
vio_pipeline:
  imu_gain: 0.85
  continuity_window: 12
  gradient_threshold: 0.15
  match_distance_px: 4.0
  max_features: 24
gnss_trust:
  degraded_trust_threshold: 0.75
  denied_trust_threshold: 0.25
  availability_weight: 0.2
  quality_weight: 0.8
  denied_outage_ratio_threshold: 0.8
trust_engine:
  sync_low_threshold: 0.60
  default_sync_quality: 1.0
  gnss_low_threshold: 0.45
  vio_trust_weight: 0.20
  calibration_high_floor: 0.75
  mode_unstable_penalty: 0.05
  effective_vio_lost_penalty: 0.06
  effective_vio_weak_penalty: 0.04
  calibration_medium_floor: 0.45
  sync_quality_weight: 0.05
  localization_confidence_weight: 0.30
  localization_low_threshold: 0.55
  gnss_trust_weight: 0.45
  vio_low_threshold: 0.55
localization_fusion:
  hysteresis_ticks: 3
  fused_confidence_floor: 0.7
  vio_base_weight: 0.4
  gnss_base_weight: 0.6
ew_risk_map:
  weight_sync_low: 0.20
  weight_localization_unstable: 0.25
  weight_gnss_denied: 0.70
  weight_gnss_degraded: 0.35
  stamp_radius_m: 25.0
  risk_medium_floor: 0.55
  risk_low_floor: 0.25
  grid_padding_m: 20.0
  global_decay_per_tick: 0.15
  corridor_sample_step_m: 10.0
  corridor_band_half_width_m: 15.0
  cell_size_m: 20.0
config_id: sim-v2
"""

CLI_OVERRIDE = """
gnss_trust:
  degraded_trust_threshold: 0.33
trust_engine:
  mode_unstable_penalty: 0.02
mission:
  degraded_confidence_threshold: 0.45
  recovery_dwell_ticks: 3
vio_trust:
  feature_count_floor: 10
"""


class ConfigSerializationTests(unittest.TestCase):
    def test_same_effective_config_yields_same_canonical_serialization(self) -> None:
        temp_dir = make_temp_dir(self)
        first_path = self._write_file(str(temp_dir), "first.yaml", BASE_CONFIG)
        second_path = self._write_file(
            str(temp_dir),
            "second.yaml",
            REORDERED_BASE_CONFIG,
        )

        first = serialize_canonical_config(first_path)
        second = serialize_canonical_config(second_path)

        self.assertEqual(first, second)

    def test_canonical_serialization_is_repeatable(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)
        override_path = self._write_file(str(temp_dir), "cli.yaml", CLI_OVERRIDE)

        first = serialize_canonical_config(
            base_path=base_path,
            cli_override_path=override_path,
        )
        second = serialize_canonical_config(
            base_path=base_path,
            cli_override_path=override_path,
        )

        self.assertEqual(first, second)

    def test_canonical_serialization_uses_stable_key_order(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)

        serialized = serialize_canonical_config(base_path)

        self.assertEqual(
            serialized,
            (
                    '{"ew_risk_map":{"cell_size_m":20.0,'
                    '"corridor_band_half_width_m":15.0,'
                    '"corridor_sample_step_m":10.0,'
                    '"global_decay_per_tick":0.15,'
                    '"grid_padding_m":20.0,'
                    '"risk_low_floor":0.25,'
                    '"risk_medium_floor":0.55,'
                    '"stamp_radius_m":25.0,'
                    '"weight_gnss_degraded":0.35,'
                    '"weight_gnss_denied":0.7,'
                    '"weight_localization_unstable":0.25,'
                    '"weight_sync_low":0.2},'
                    '"gnss_trust":{"availability_weight":0.2,'
                    '"degraded_trust_threshold":0.75,'
                    '"denied_outage_ratio_threshold":0.8,'
                    '"denied_trust_threshold":0.25,'
                    '"quality_weight":0.8},'
                    '"localization_fusion":{"fused_confidence_floor":0.7,'
                    '"gnss_base_weight":0.6,'
                    '"hysteresis_ticks":3,'
                    '"vio_base_weight":0.4},'
                    '"mission":{"degraded_confidence_threshold":0.5,'
                    '"denied_allowed_states":["MISSION_FALLBACK","MISSION_SAFE_HOLD","MISSION_ABORT"],'
                    '"denied_fallback_confidence_threshold":0.28,'
                    '"emergency_land_confidence_threshold":0.2,'
                    '"max_state_transitions_in_window":2,'
                    '"nominal_confidence_threshold":0.8,'
                    '"oscillation_window_ticks":5,'
                    '"recovery_dwell_ticks":2,'
                    '"safe_hold_escalation_ticks":3},'
                    '"schema_version":"2.0",'
                    '"trust_engine":{"calibration_high_floor":0.75,'
                    '"calibration_medium_floor":0.45,'
                    '"default_sync_quality":1.0,'
                    '"effective_vio_lost_penalty":0.06,'
                    '"effective_vio_weak_penalty":0.04,'
                    '"gnss_low_threshold":0.45,'
                    '"gnss_trust_weight":0.45,'
                    '"localization_confidence_weight":0.3,'
                    '"localization_low_threshold":0.55,'
                    '"mode_unstable_penalty":0.05,'
                    '"sync_low_threshold":0.6,'
                    '"sync_quality_weight":0.05,'
                    '"vio_low_threshold":0.55,'
                    '"vio_trust_weight":0.2},'
                    '"vio_health":{"good_threshold":0.75,'
                    '"weak_threshold":0.4},'
                    '"vio_pipeline":{"continuity_window":12,'
                    '"gradient_threshold":0.15,'
                    '"imu_gain":0.85,'
                    '"match_distance_px":4.0,'
                    '"max_features":24},'
                    '"vio_trust":{"feature_count_floor":12,'
                    '"imu_alignment_ceiling":0.5,'
                    '"metric_weights":{"feature_count":0.25,'
                    '"imu_alignment":0.15,'
                    '"reprojection_error":0.25,'
                    '"track_continuity":0.35},'
                    '"reprojection_error_ceiling_px":2.0,'
                    '"track_continuity_floor":0.5}}'
            ),
        )

    def test_payload_and_dataclass_canonicalization_match(self) -> None:
        temp_dir = make_temp_dir(self)
        base_path = self._write_file(str(temp_dir), "base.yaml", BASE_CONFIG)
        payload = resolve_app_config_payload(base_path)
        config = load_app_config(base_path)

        self.assertEqual(
            canonicalize_config_payload(payload),
            canonicalize_app_config(config),
        )

    def _write_file(self, directory: str, name: str, contents: str) -> Path:
        path = Path(directory) / name
        path.write_text(contents.lstrip(), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
