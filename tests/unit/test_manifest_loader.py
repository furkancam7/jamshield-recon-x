from pathlib import Path
import unittest

from _support import make_temp_dir
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
        self.assertEqual(manifest.vio_profile_id, "nominal_v1")
        self.assertEqual(manifest.runtime_sync_quality, 1.0)
        self.assertEqual(manifest.evaluation_profile, "baseline_nominal_profile_v1")
        self.assertEqual(len(manifest.resolved_mission_timeline().steps), 1)

    def test_denied_manifest_loads(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s3_gnss_denied_zone.yaml")
        self.assertEqual(manifest.map_name, "industrial_corridor")
        self.assertEqual(manifest.run_seed, 333)
        self.assertIn("description", manifest.metadata)
        self.assertEqual(manifest.vio_profile_id, "nominal_v1")

    def test_sync_low_manifest_loads_runtime_health_override(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s13_sync_low_nominal.yaml")
        self.assertEqual(manifest.runtime_sync_quality, 0.2)

    def test_conflict_manifest_loads_vio_override(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s7_conflict_score_dominates.yaml")
        self.assertEqual(manifest.vio_profile_id, "lost_tracking_v1")
        self.assertEqual(manifest.vio_reported_state_override, "good")

    def test_timeline_manifest_inherits_defaults_and_applies_step_overrides(self) -> None:
        manifest = load_manifest(SCENARIO_DIR / "s18_abort_terminal.yaml")

        self.assertIsNotNone(manifest.mission_timeline)
        timeline = manifest.resolved_mission_timeline()
        self.assertEqual(timeline.tick_period_s, 1.0)
        self.assertEqual(len(timeline.steps), 2)
        self.assertEqual(timeline.steps[0].vio_profile_id, "lost_tracking_v1")
        self.assertEqual(timeline.steps[1].gnss_condition, "nominal")
        self.assertEqual(timeline.steps[1].vio_profile_id, "nominal_v1")

    def test_manifest_requires_complete_metadata(self) -> None:
        temp_dir = make_temp_dir(self)
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
                    "evaluation_profile: baseline_nominal_profile_v1",
                    "metadata:",
                    "  title: Missing Owner",
                    "  description: Incomplete metadata manifest",
                ]
            ),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_manifest(manifest_path)

    def test_manifest_rejects_invalid_runtime_sync_quality(self) -> None:
        temp_dir = make_temp_dir(self)
        manifest_path = Path(temp_dir) / "bad-sync.yaml"
        manifest_path.write_text(
            "\n".join(
                [
                    "scenario_id: bad_sync_case",
                    "map_name: test_map",
                    'vehicle_spawn: {"x": 0.0, "y": 0.0, "z": 10.0}',
                    "route_waypoints:",
                    '  - {"x": 1.0, "y": 1.0, "z": 10.0}',
                    "gnss_condition: nominal",
                    "run_seed: 1",
                    "evaluation_profile: baseline_nominal_profile_v1",
                    "runtime_health:",
                    "  sync_quality: 1.5",
                    "metadata:",
                    "  title: Bad Sync",
                    "  description: Out of range sync quality.",
                    "  owner: test-suite",
                ]
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "sync_quality"):
            load_manifest(manifest_path)

    def test_manifest_resolves_relative_config_override_path(self) -> None:
        temp_dir = make_temp_dir(self)
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
                    "evaluation_profile: baseline_nominal_profile_v1",
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

    def test_manifest_rejects_invalid_timeline_repeat_count(self) -> None:
        temp_dir = make_temp_dir(self)
        manifest_path = Path(temp_dir) / "bad-timeline.yaml"
        manifest_path.write_text(
            "\n".join(
                [
                    "scenario_id: bad_timeline_case",
                    "map_name: test_map",
                    'vehicle_spawn: {"x": 0.0, "y": 0.0, "z": 10.0}',
                    "route_waypoints:",
                    '  - {"x": 1.0, "y": 1.0, "z": 10.0}',
                    "gnss_condition: nominal",
                    "run_seed: 1",
                    "evaluation_profile: baseline_nominal_profile_v1",
                    "mission_timeline:",
                    "  tick_period_s: 1.0",
                    "  steps:",
                    '    - {"repeats": 0}',
                    "metadata:",
                    "  title: Bad Timeline",
                    "  description: Invalid repeats.",
                    "  owner: test-suite",
                ]
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "repeats"):
            load_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
