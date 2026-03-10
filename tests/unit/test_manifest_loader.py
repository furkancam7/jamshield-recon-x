from pathlib import Path
import unittest

from scenario_orchestrator.manifest_loader import load_manifest


ROOT_DIR = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT_DIR / "scenarios" / "baseline"


class ManifestLoaderTests(unittest.TestCase):
    def test_nominal_manifest_loads(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s1_nominal.yaml")
        self.assertEqual(manifest.scenario_id, "s1_nominal")
        self.assertEqual(manifest.gnss_condition, "nominal")
        self.assertEqual(len(manifest.route_waypoints), 2)

    def test_denied_manifest_loads(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s3_gnss_denied_zone.yaml")
        self.assertEqual(manifest.map_name, "industrial_corridor")
        self.assertEqual(manifest.run_seed, 333)


if __name__ == "__main__":
    unittest.main()

