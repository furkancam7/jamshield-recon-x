"""Unit tests for VIO health scoring and conflict resolution."""

import unittest

from common.config import VioHealthConfig
from vio_health.scoring import derive_vio_healthy, resolve_effective_vio_state, score_to_state


DEFAULT_VIO_CONFIG = VioHealthConfig(good_threshold=0.75, weak_threshold=0.40)


class ScoreToStateTests(unittest.TestCase):
    def test_high_score_is_good(self) -> None:
        self.assertEqual(score_to_state(0.85, DEFAULT_VIO_CONFIG), "good")

    def test_threshold_score_is_good(self) -> None:
        self.assertEqual(score_to_state(0.75, DEFAULT_VIO_CONFIG), "good")

    def test_mid_score_is_weak(self) -> None:
        self.assertEqual(score_to_state(0.55, DEFAULT_VIO_CONFIG), "weak")

    def test_weak_threshold_is_weak(self) -> None:
        self.assertEqual(score_to_state(0.40, DEFAULT_VIO_CONFIG), "weak")

    def test_low_score_is_lost(self) -> None:
        self.assertEqual(score_to_state(0.20, DEFAULT_VIO_CONFIG), "lost")

    def test_zero_score_is_lost(self) -> None:
        self.assertEqual(score_to_state(0.0, DEFAULT_VIO_CONFIG), "lost")


class ConflictResolutionTests(unittest.TestCase):
    def test_agreement_good(self) -> None:
        result = resolve_effective_vio_state("good", 0.85, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "good")

    def test_agreement_weak(self) -> None:
        result = resolve_effective_vio_state("weak", 0.55, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "weak")

    def test_agreement_lost(self) -> None:
        result = resolve_effective_vio_state("lost", 0.20, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "lost")

    def test_score_dominates_when_worse(self) -> None:
        """vio_state=good but score=0.30 => lost (score bucket dominates)."""
        result = resolve_effective_vio_state("good", 0.30, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "lost")

    def test_state_dominates_when_worse(self) -> None:
        """vio_state=lost but score=0.82 => lost (state dominates)."""
        result = resolve_effective_vio_state("lost", 0.82, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "lost")

    def test_weak_state_with_good_score(self) -> None:
        """vio_state=weak but score=0.90 => weak (state is worse)."""
        result = resolve_effective_vio_state("weak", 0.90, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "weak")

    def test_good_state_with_weak_score(self) -> None:
        """vio_state=good but score=0.50 => weak (score bucket is worse)."""
        result = resolve_effective_vio_state("good", 0.50, DEFAULT_VIO_CONFIG)
        self.assertEqual(result, "weak")

    def test_invalid_vio_state_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_effective_vio_state("invalid", 0.5, DEFAULT_VIO_CONFIG)


class DeriveVioHealthyTests(unittest.TestCase):
    def test_good_is_healthy(self) -> None:
        self.assertTrue(derive_vio_healthy("good"))

    def test_weak_is_healthy(self) -> None:
        self.assertTrue(derive_vio_healthy("weak"))

    def test_lost_is_not_healthy(self) -> None:
        self.assertFalse(derive_vio_healthy("lost"))


if __name__ == "__main__":
    unittest.main()
