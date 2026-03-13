from pathlib import Path
import unittest

from common.config import load_app_config
from vio import run_vio_pipeline


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


class VioPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_app_config(CONFIG_PATH)

    def _run(self, seed: int, profile_id: str):
        return run_vio_pipeline(
            run_seed=seed,
            profile_id=profile_id,
            pipeline_config=self.config.vio_pipeline,
            trust_config=self.config.vio_trust,
            health_config=self.config.vio_health,
        )

    def test_pipeline_is_deterministic_for_same_seed(self) -> None:
        first = self._run(111, "nominal_v1")
        second = self._run(111, "nominal_v1")
        self.assertEqual(first, second)

    def test_profiles_preserve_feature_and_continuity_ordering(self) -> None:
        nominal = self._run(111, "nominal_v1")
        weak = self._run(555, "weak_texture_v1")
        lost = self._run(666, "lost_tracking_v1")

        self.assertGreater(nominal.feature_count, weak.feature_count)
        self.assertGreater(weak.feature_count, lost.feature_count)
        self.assertGreater(nominal.track_continuity, weak.track_continuity)
        self.assertGreater(weak.track_continuity, lost.track_continuity)

    def test_degraded_profiles_raise_reprojection_error(self) -> None:
        nominal = self._run(111, "nominal_v1")
        weak = self._run(555, "weak_texture_v1")
        lost = self._run(666, "lost_tracking_v1")

        self.assertLess(nominal.reprojection_error_px, weak.reprojection_error_px)
        self.assertLess(weak.reprojection_error_px, lost.reprojection_error_px)

    def test_profile_states_match_expected_health_buckets(self) -> None:
        nominal = self._run(111, "nominal_v1")
        weak = self._run(555, "weak_texture_v1")
        lost = self._run(666, "lost_tracking_v1")

        self.assertEqual(nominal.effective_vio_state, "good")
        self.assertEqual(weak.effective_vio_state, "weak")
        self.assertEqual(lost.effective_vio_state, "lost")

    def test_imu_stub_is_repeatable(self) -> None:
        first = self._run(333, "weak_texture_v1")
        second = self._run(333, "weak_texture_v1")

        self.assertEqual(first.yaw_delta_rad, second.yaw_delta_rad)
        self.assertEqual(first.imu_alignment_error, second.imu_alignment_error)


if __name__ == "__main__":
    unittest.main()
