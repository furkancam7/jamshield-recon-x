from pathlib import Path
import unittest

from common.config import load_app_config
from gnss_trust.trust_service import TrustService
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
        return TrustService(config.trust).evaluate(snapshot, vio_healthy=True)

    def test_nominal_has_highest_trust(self) -> None:
        nominal = self._evaluate("s1_nominal.yaml")
        degraded = self._evaluate("s2_gnss_degraded_corridor.yaml")
        denied = self._evaluate("s3_gnss_denied_zone.yaml")

        self.assertEqual(nominal.gnss_state, "nominal")
        self.assertEqual(degraded.gnss_state, "degraded")
        self.assertEqual(denied.gnss_state, "denied")
        self.assertGreater(nominal.trust_score, degraded.trust_score)
        self.assertGreater(degraded.trust_score, denied.trust_score)


if __name__ == "__main__":
    unittest.main()
