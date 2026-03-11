from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from common.config import (
    canonicalize_app_config,
    canonicalize_config_payload,
    load_app_config,
    resolve_app_config_payload,
    serialize_canonical_config,
)


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

REORDERED_BASE_CONFIG = """
schema_version: "1.0"
mission:
  denied_allowed_states:
    - MISSION_FALLBACK
    - MISSION_SAFE_HOLD
  emergency_land_confidence_threshold: 0.2
  degraded_confidence_threshold: 0.5
  nominal_confidence_threshold: 0.8
  denied_fallback_confidence_threshold: 0.3
trust:
  degraded_trust_threshold: 0.75
  denied_trust_threshold: 0.25
  availability_weight: 0.2
  quality_weight: 0.8
  denied_outage_ratio_threshold: 0.8
  vio_bonus: 0.25
  mission_confidence_weight: 0.75
config_id: sim-v2
"""

CLI_OVERRIDE = """
trust:
  degraded_trust_threshold: 0.33
  vio_bonus: 0.4
mission:
  degraded_confidence_threshold: 0.45
"""


class ConfigSerializationTests(unittest.TestCase):
    def test_same_effective_config_yields_same_canonical_serialization(self) -> None:
        with TemporaryDirectory() as temp_dir:
            first_path = self._write_file(temp_dir, "first.yaml", BASE_CONFIG)
            second_path = self._write_file(
                temp_dir,
                "second.yaml",
                REORDERED_BASE_CONFIG,
            )

            first = serialize_canonical_config(first_path)
            second = serialize_canonical_config(second_path)

            self.assertEqual(first, second)

    def test_canonical_serialization_is_repeatable(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)
            override_path = self._write_file(temp_dir, "cli.yaml", CLI_OVERRIDE)

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
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)

            serialized = serialize_canonical_config(base_path)

            self.assertEqual(
                serialized,
                (
                    '{"mission":{"degraded_confidence_threshold":0.5,'
                    '"denied_allowed_states":["MISSION_FALLBACK","MISSION_SAFE_HOLD"],'
                    '"denied_fallback_confidence_threshold":0.3,'
                    '"emergency_land_confidence_threshold":0.2,'
                    '"nominal_confidence_threshold":0.8},'
                    '"schema_version":"1.0",'
                    '"trust":{"availability_weight":0.2,'
                    '"degraded_trust_threshold":0.75,'
                    '"denied_outage_ratio_threshold":0.8,'
                    '"denied_trust_threshold":0.25,'
                    '"mission_confidence_weight":0.75,'
                    '"quality_weight":0.8,'
                    '"vio_bonus":0.25}}'
                ),
            )

    def test_payload_and_dataclass_canonicalization_match(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = self._write_file(temp_dir, "base.yaml", BASE_CONFIG)
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
