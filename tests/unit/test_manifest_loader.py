from pathlib import Path
from tempfile import TemporaryDirectory
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
        self.assertEqual(manifest.metadata["owner"], "autonomy-sim")

    def test_denied_manifest_loads(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s3_gnss_denied_zone.yaml")
        self.assertEqual(manifest.map_name, "industrial_corridor")
        self.assertEqual(manifest.run_seed, 333)
        self.assertIn("description", manifest.metadata)

    def test_manifest_requires_complete_metadata(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "bad.yaml"
            manifest_path.write_text(
                "\n".join(
                    [
                        "scenario_id: bad_case",
                        "map_name: test_map",
                        'vehicle_spawn: {"x": 0.0, "y": 0.0, "z": 10.0}',
                        "route_waypoints:",
                        '  - {"x": 1.0, "y": 1.0, "z": 10.0}',
                        "gnss_condition: nominal",
                        "run_seed: 1",
                        "metadata:",
                        "  title: Missing Owner",
                        "  description: Incomplete metadata manifest",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_manifest(manifest_path)

    def test_manifest_resolves_relative_config_override_path(self) -> None:
        with TemporaryDirectory() as temp_dir:
            overrides_dir = Path(temp_dir) / "overrides"
            overrides_dir.mkdir()
            manifest_path = Path(temp_dir) / "manifest.yaml"
            manifest_path.write_text(
                "\n".join(
                    [
                        "scenario_id: override_case",
                        "map_name: test_map",
                        'vehicle_spawn: {"x": 0.0, "y": 0.0, "z": 10.0}',
                        "route_waypoints:",
                        '  - {"x": 1.0, "y": 1.0, "z": 10.0}',
                        "gnss_condition: nominal",
                        "run_seed: 1",
                        "config_override: overrides/scenario.yaml",
                        "metadata:",
                        "  title: Override Manifest",
                        "  description: Manifest with config override path.",
                        "  owner: test-suite",
                    ]
                ),
                encoding="utf-8",
            )

            manifest = load_manifest(manifest_path)

            self.assertEqual(
                manifest.config_override_path,
                overrides_dir / "scenario.yaml",
            )


if __name__ == "__main__":
    unittest.main()
