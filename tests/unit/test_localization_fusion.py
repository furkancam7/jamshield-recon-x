"""Unit tests for localization fusion contracts and hysteresis."""

from __future__ import annotations

import unittest

from common.config import LocalizationFusionConfig
from localization_fusion.contracts import FusionAssessment, LocalizationMode
from localization_fusion.fusion_service import (
    LocalizationFusionService,
    apply_hysteresis,
    compute_localization_confidence,
    compute_source_weights,
    select_localization_mode,
)


def _default_config(**overrides: object) -> LocalizationFusionConfig:
    defaults = {
        "gnss_base_weight": 0.6,
        "vio_base_weight": 0.4,
        "fused_confidence_floor": 0.7,
        "hysteresis_ticks": 3,
    }
    defaults.update(overrides)
    return LocalizationFusionConfig(**defaults)  # type: ignore[arg-type]


class TestSourceWeights(unittest.TestCase):
    def test_nominal_weights_sum_to_one(self) -> None:
        config = _default_config()
        gnss_weight, vio_weight = compute_source_weights(0.95, 0.85, config)
        self.assertAlmostEqual(gnss_weight + vio_weight, 1.0, places=6)

    def test_gnss_dominant_when_trust_high(self) -> None:
        config = _default_config()
        gnss_weight, vio_weight = compute_source_weights(1.0, 0.0, config)
        self.assertEqual(gnss_weight, 1.0)
        self.assertEqual(vio_weight, 0.0)

    def test_vio_dominant_when_trust_zero(self) -> None:
        config = _default_config()
        gnss_weight, vio_weight = compute_source_weights(0.0, 1.0, config)
        self.assertEqual(gnss_weight, 0.0)
        self.assertEqual(vio_weight, 1.0)

    def test_both_zero_returns_equal(self) -> None:
        config = _default_config()
        gnss_weight, vio_weight = compute_source_weights(0.0, 0.0, config)
        self.assertAlmostEqual(gnss_weight, 0.5)
        self.assertAlmostEqual(vio_weight, 0.5)

    def test_base_weights_influence_ratio(self) -> None:
        config = _default_config(gnss_base_weight=0.8, vio_base_weight=0.2)
        gnss_weight, vio_weight = compute_source_weights(1.0, 1.0, config)
        self.assertAlmostEqual(gnss_weight, 0.8)
        self.assertAlmostEqual(vio_weight, 0.2)


class TestLocalizationConfidence(unittest.TestCase):
    def test_perfect_scores(self) -> None:
        confidence = compute_localization_confidence(1.0, 1.0, 0.6, 0.4)
        self.assertAlmostEqual(confidence, 1.0)

    def test_zero_scores(self) -> None:
        confidence = compute_localization_confidence(0.0, 0.0, 0.5, 0.5)
        self.assertAlmostEqual(confidence, 0.0)

    def test_clamped_to_unit_range(self) -> None:
        confidence = compute_localization_confidence(1.5, 1.5, 0.6, 0.4)
        self.assertLessEqual(confidence, 1.0)


class TestSelectLocalizationMode(unittest.TestCase):
    def test_nominal_good_returns_gnss_primary(self) -> None:
        config = _default_config()
        mode = select_localization_mode("nominal", "good", 0.95, config)
        self.assertEqual(mode, LocalizationMode.GNSS_PRIMARY)

    def test_degraded_good_returns_blended(self) -> None:
        config = _default_config()
        mode = select_localization_mode("degraded", "good", 0.55, config)
        self.assertEqual(mode, LocalizationMode.BLENDED)

    def test_denied_good_returns_vio_primary(self) -> None:
        config = _default_config()
        mode = select_localization_mode("denied", "good", 0.3, config)
        self.assertEqual(mode, LocalizationMode.VIO_PRIMARY)

    def test_denied_weak_returns_vio_primary(self) -> None:
        config = _default_config()
        mode = select_localization_mode("denied", "weak", 0.2, config)
        self.assertEqual(mode, LocalizationMode.VIO_PRIMARY)

    def test_denied_lost_returns_hold_last_safe(self) -> None:
        config = _default_config()
        mode = select_localization_mode("denied", "lost", 0.05, config)
        self.assertEqual(mode, LocalizationMode.HOLD_LAST_SAFE)

    def test_nominal_low_confidence_returns_blended(self) -> None:
        config = _default_config()
        mode = select_localization_mode("nominal", "good", 0.5, config)
        self.assertEqual(mode, LocalizationMode.BLENDED)


class TestHysteresis(unittest.TestCase):
    def test_more_severe_candidate_applies_immediately(self) -> None:
        config = _default_config(hysteresis_ticks=5)
        result = apply_hysteresis(
            LocalizationMode.HOLD_LAST_SAFE,
            LocalizationMode.GNSS_PRIMARY,
            ticks_in_current_mode=1,
            config=config,
        )
        self.assertEqual(result, LocalizationMode.HOLD_LAST_SAFE)

    def test_upgrade_blocked_by_hysteresis(self) -> None:
        config = _default_config(hysteresis_ticks=3)
        result = apply_hysteresis(
            LocalizationMode.GNSS_PRIMARY,
            LocalizationMode.BLENDED,
            ticks_in_current_mode=1,
            config=config,
        )
        self.assertEqual(result, LocalizationMode.BLENDED)

    def test_upgrade_allowed_after_hysteresis(self) -> None:
        config = _default_config(hysteresis_ticks=3)
        result = apply_hysteresis(
            LocalizationMode.GNSS_PRIMARY,
            LocalizationMode.BLENDED,
            ticks_in_current_mode=3,
            config=config,
        )
        self.assertEqual(result, LocalizationMode.GNSS_PRIMARY)

    def test_same_mode_no_change(self) -> None:
        config = _default_config(hysteresis_ticks=3)
        result = apply_hysteresis(
            LocalizationMode.BLENDED,
            LocalizationMode.BLENDED,
            ticks_in_current_mode=1,
            config=config,
        )
        self.assertEqual(result, LocalizationMode.BLENDED)


class TestFusionService(unittest.TestCase):
    def test_nominal_scenario(self) -> None:
        config = _default_config()
        service = LocalizationFusionService(config)
        result = service.evaluate(
            gnss_trust=0.95,
            gnss_state="nominal",
            vio_health_score=0.85,
            effective_vio_state="good",
        )
        self.assertEqual(result.localization_mode, LocalizationMode.GNSS_PRIMARY)
        self.assertGreater(result.localization_confidence, 0.7)
        self.assertAlmostEqual(result.gnss_weight + result.vio_weight, 1.0)
        self.assertTrue(result.mode_stable)

    def test_denied_lost_scenario(self) -> None:
        config = _default_config()
        service = LocalizationFusionService(config)
        result = service.evaluate(
            gnss_trust=0.05,
            gnss_state="denied",
            vio_health_score=0.1,
            effective_vio_state="lost",
        )
        self.assertEqual(result.localization_mode, LocalizationMode.HOLD_LAST_SAFE)
        self.assertLess(result.localization_confidence, 0.3)

    def test_mode_stability_tracking(self) -> None:
        config = _default_config()
        service = LocalizationFusionService(config)
        r1 = service.evaluate(0.05, "denied", 0.1, "lost")
        self.assertFalse(r1.mode_stable)
        r2 = service.evaluate(0.05, "denied", 0.1, "lost")
        self.assertTrue(r2.mode_stable)

    def test_hysteresis_prevents_oscillation(self) -> None:
        config = _default_config(hysteresis_ticks=5)
        service = LocalizationFusionService(config)
        service.evaluate(0.55, "degraded", 0.85, "good")
        service.evaluate(0.55, "degraded", 0.85, "good")
        result = service.evaluate(0.95, "nominal", 0.85, "good")
        self.assertEqual(result.localization_mode, LocalizationMode.BLENDED)

    def test_hysteresis_allows_after_dwell(self) -> None:
        config = _default_config(hysteresis_ticks=2)
        service = LocalizationFusionService(config)
        service.evaluate(0.95, "nominal", 0.85, "good")
        service.evaluate(0.95, "nominal", 0.85, "good")
        result = service.evaluate(0.55, "degraded", 0.85, "good")
        self.assertEqual(result.localization_mode, LocalizationMode.BLENDED)

    def test_assessment_dataclass_fields(self) -> None:
        config = _default_config()
        service = LocalizationFusionService(config)
        result = service.evaluate(0.95, "nominal", 0.85, "good")
        self.assertIsInstance(result, FusionAssessment)
        self.assertIsInstance(result.localization_mode, LocalizationMode)
        self.assertIsInstance(result.localization_confidence, float)
        self.assertIsInstance(result.gnss_weight, float)
        self.assertIsInstance(result.vio_weight, float)
        self.assertIsInstance(result.mode_stable, bool)


if __name__ == "__main__":
    unittest.main()
