from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from common.config import load_app_config, resolve_app_config


BASE_CONFIG = """
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
    - MISSION_FALLBACK
    - MISSION_SAFE_HOLD
"""

SCENARIO_OVERRIDE = """
trust:
  degraded_trust_threshold: 0.6
mission:
  degraded_confidence_threshold: 0.45
"""

CLI_OVERRIDE = """
trust:
  degraded_trust_threshold: 0.33
  vio_bonus: 0.4
"""

INVALID_OVERRIDE = """
trust:
  future_only_field: 1.0
"""


class ConfigResolutionTests(unittest.TestCase):
    def test_base_only_resolution_matches_base_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)

            self.assertEqual(resolve_app_config(base_path), load_app_config(base_path))

    def test_scenario_override_applies_after_base_config(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)
            scenario_override_path = self._write_file(
                temp_dir,
                "scenario-override.yaml",
                SCENARIO_OVERRIDE,
            )

            config = resolve_app_config(
                base_path=base_path,
                scenario_override_path=scenario_override_path,
            )

            self.assertEqual(config.trust.degraded_trust_threshold, 0.6)
            self.assertEqual(config.mission.degraded_confidence_threshold, 0.45)
            self.assertEqual(config.trust.vio_bonus, 0.25)

    def test_cli_override_takes_precedence_over_scenario_override(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)
            scenario_override_path = self._write_file(
                temp_dir,
                "scenario-override.yaml",
                SCENARIO_OVERRIDE,
            )
            cli_override_path = self._write_file(
                temp_dir,
                "cli-override.yaml",
                CLI_OVERRIDE,
            )

            config = resolve_app_config(
                base_path=base_path,
                scenario_override_path=scenario_override_path,
                cli_override_path=cli_override_path,
            )

            self.assertEqual(config.trust.degraded_trust_threshold, 0.33)
            self.assertEqual(config.trust.vio_bonus, 0.4)
            self.assertEqual(config.mission.degraded_confidence_threshold, 0.45)

    def test_resolution_rejects_unknown_override_fields(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)
            invalid_override_path = self._write_file(
                temp_dir,
                "invalid-override.yaml",
                INVALID_OVERRIDE,
            )

            with self.assertRaisesRegex(ValueError, "Unknown config override field"):
                resolve_app_config(
                    base_path=base_path,
                    scenario_override_path=invalid_override_path,
                )

    def test_resolution_is_deterministic_for_same_inputs(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)
            scenario_override_path = self._write_file(
                temp_dir,
                "scenario-override.yaml",
                SCENARIO_OVERRIDE,
            )
            cli_override_path = self._write_file(
                temp_dir,
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
