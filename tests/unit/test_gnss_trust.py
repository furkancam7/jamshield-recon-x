from pathlib import Path
import unittest

from common.config import load_app_config
from gnss_trust.trust_service import GnssTrustService
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator


ROOT_DIR = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT_DIR / "scenarios" / "baseline"
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


class GnssTrustTests(unittest.TestCase):
    def _evaluate(self, scenario_name: str):
        manifest = load_manifest(SCENARIO_DIR / scenario_name)
        snapshot = ScenarioOrchestrator(manifest).build_snapshot()
        config = load_app_config(CONFIG_PATH)
        return GnssTrustService(config.gnss_trust).evaluate(snapshot)

    def test_nominal_has_highest_trust(self) -> None:
        nominal = self._evaluate("s1_nominal.yaml")
        degraded = self._evaluate("s2_gnss_degraded_corridor.yaml")
        denied = self._evaluate("s3_gnss_denied_zone.yaml")

        self.assertEqual(nominal.gnss_state, "nominal")
        self.assertEqual(degraded.gnss_state, "degraded")
        self.assertEqual(denied.gnss_state, "denied")
        self.assertGreater(nominal.gnss_trust, degraded.gnss_trust)
        self.assertGreater(degraded.gnss_trust, denied.gnss_trust)

    def test_assessment_no_longer_exposes_mission_confidence(self) -> None:
        nominal = self._evaluate("s1_nominal.yaml")
        self.assertFalse(hasattr(nominal, "mission_confidence"))


if __name__ == "__main__":
    unittest.main()
