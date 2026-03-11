from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from common.config import AppConfig, MissionConfig, TrustConfig, load_app_config
from evaluation.artifact_schema import REPORT_SCHEMA_VERSION, validate_report


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


class ConfigAndArtifactTests(unittest.TestCase):
    def test_app_config_loads_expected_defaults(self) -> None:
        config = load_app_config(CONFIG_PATH)

        self.assertIsInstance(config, AppConfig)
        self.assertIsInstance(config.trust, TrustConfig)
        self.assertIsInstance(config.mission, MissionConfig)
        self.assertEqual(config.config_id, "sim-v1")
        self.assertEqual(config.schema_version, "1.0")
        self.assertEqual(config.mission.denied_allowed_states[0], "MISSION_FALLBACK")

    def test_invalid_config_missing_required_field_fails_validation(self) -> None:
        config_path = self._write_config(
            """
config_id: sim-v1
schema_version: "1.0"
trust:
  quality_weight: 0.8
  availability_weight: 0.2
  mission_confidence_weight: 0.75
  vio_bonus: 0.25
  denied_outage_ratio_threshold: 0.8
  denied_trust_threshold: 0.25
  degraded_trust_threshold: 0.75
"""
        )

        with self.assertRaisesRegex(ValueError, "required fields"):
            load_app_config(config_path)

    def test_invalid_config_rejects_blank_identifiers(self) -> None:
        config_path = self._write_config(
            """
config_id: "  "
schema_version: "1.0"
trust:
  quality_weight: 0.8
  availability_weight: 0.2
  mission_confidence_weight: 0.75
  vio_bonus: 0.25
  denied_outage_ratio_threshold: 0.8
  denied_trust_threshold: 0.25
  degraded_trust_threshold: 0.75
mission:
  nominal_confidence_threshold: 0.8
  degraded_confidence_threshold: 0.5
  denied_fallback_confidence_threshold: 0.3
  emergency_land_confidence_threshold: 0.2
  denied_allowed_states:
    - MISSION_FALLBACK
"""
        )

        with self.assertRaisesRegex(ValueError, "non-empty string"):
            load_app_config(config_path)

    def test_invalid_config_rejects_non_numeric_thresholds(self) -> None:
        config_path = self._write_config(
            """
config_id: sim-v1
schema_version: "1.0"
trust:
  quality_weight: nope
  availability_weight: 0.2
  mission_confidence_weight: 0.75
  vio_bonus: 0.25
  denied_outage_ratio_threshold: 0.8
  denied_trust_threshold: 0.25
  degraded_trust_threshold: 0.75
mission:
  nominal_confidence_threshold: 0.8
  degraded_confidence_threshold: 0.5
  denied_fallback_confidence_threshold: 0.3
  emergency_land_confidence_threshold: 0.2
  denied_allowed_states:
    - MISSION_FALLBACK
"""
        )

        with self.assertRaisesRegex(ValueError, "must be numeric"):
            load_app_config(config_path)

    def test_invalid_config_rejects_invalid_denied_allowed_states(self) -> None:
        config_path = self._write_config(
            """
config_id: sim-v1
schema_version: "1.0"
trust:
  quality_weight: 0.8
  availability_weight: 0.2
  mission_confidence_weight: 0.75
  vio_bonus: 0.25
  denied_outage_ratio_threshold: 0.8
  denied_trust_threshold: 0.25
  degraded_trust_threshold: 0.75
mission:
  nominal_confidence_threshold: 0.8
  degraded_confidence_threshold: 0.5
  denied_fallback_confidence_threshold: 0.3
  emergency_land_confidence_threshold: 0.2
  denied_allowed_states:
    - ""
"""
        )

        with self.assertRaisesRegex(ValueError, "non-empty strings"):
            load_app_config(config_path)

    def test_report_validation_rejects_missing_required_field(self) -> None:
        payload = {
            "schema_version": REPORT_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenario_id": "s1_nominal",
            "map_name": "open_field",
            "run_seed": 111,
            "gnss_condition": "nominal",
            "gnss_state": "nominal",
            "trust_score": 0.96,
            "mission_confidence": 0.97,
            "vio_healthy": True,
            "vio_state": "healthy",
            "mission_state": "MISSION_NORMAL",
            "ate_m": 0.5,
            "route_length_m": 123.246,
            "ground_truth_usage": "evaluation_only",
            "config_id": "sim-v1",
            "software_revision": "test-revision",
            "scenario_metadata": {
                "title": "Nominal",
                "description": "Baseline test",
                "owner": "test-suite",
            },
        }

        with self.assertRaises(ValueError):
            validate_report(payload)

    def _write_config(self, contents: str) -> Path:
        temp_dir = TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "config.yaml"
        path.write_text(contents.lstrip(), encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()
