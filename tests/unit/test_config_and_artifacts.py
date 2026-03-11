from pathlib import Path
import unittest

from common.config import load_app_config
from evaluation.artifact_schema import REPORT_SCHEMA_VERSION, validate_report


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


class ConfigAndArtifactTests(unittest.TestCase):
    def test_app_config_loads_expected_defaults(self) -> None:
        config = load_app_config(CONFIG_PATH)

        self.assertEqual(config.config_id, "sim-v1")
        self.assertEqual(config.schema_version, "1.0")
        self.assertEqual(config.mission.denied_allowed_states[0], "MISSION_FALLBACK")

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


if __name__ == "__main__":
    unittest.main()
