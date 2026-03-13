import unittest

from common.config import TrustEngineConfig
from trust_engine import TrustEngineService


DEFAULT_CONFIG = TrustEngineConfig(
    gnss_trust_weight=0.45,
    localization_confidence_weight=0.30,
    vio_trust_weight=0.20,
    sync_quality_weight=0.05,
    gnss_low_threshold=0.45,
    localization_low_threshold=0.55,
    vio_low_threshold=0.55,
    sync_low_threshold=0.60,
    default_sync_quality=1.0,
    mode_unstable_penalty=0.05,
    calibration_high_floor=0.75,
    calibration_medium_floor=0.45,
)


class TrustEngineTests(unittest.TestCase):
    def test_weighted_aggregation_uses_adjusted_localization_and_default_sync(self) -> None:
        assessment = TrustEngineService(DEFAULT_CONFIG).evaluate(
            scenario_id="s1_nominal",
            gnss_trust=0.80,
            gnss_state="nominal",
            vio_health_score=0.50,
            localization_confidence=0.90,
            mode_stable=False,
            sync_quality=None,
        )

        self.assertEqual(assessment.vio_trust, 0.5)
        self.assertEqual(assessment.sync_quality, 1.0)
        self.assertEqual(assessment.localization_confidence, 0.85)
        self.assertEqual(assessment.mission_confidence, 0.765)

    def test_primary_reason_uses_deficit_order_tie_break(self) -> None:
        assessment = TrustEngineService(DEFAULT_CONFIG).evaluate(
            scenario_id="s2_tie_break",
            gnss_trust=0.40,
            gnss_state="denied",
            vio_health_score=0.40,
            localization_confidence=0.45,
            mode_stable=True,
            sync_quality=0.40,
        )

        self.assertEqual(assessment.trust_primary_reason_code, "sync_quality_low")
        self.assertEqual(
            assessment.trust_reason_codes,
            (
                "sync_quality_low",
                "gnss_denial_suspected",
                "vio_trust_low",
                "localization_confidence_low",
            ),
        )

    def test_primary_reason_prefers_sync_on_equal_threshold_deficit(self) -> None:
        assessment = TrustEngineService(DEFAULT_CONFIG).evaluate(
            scenario_id="s2_sync_tie_break",
            gnss_trust=0.05,
            gnss_state="denied",
            vio_health_score=0.90,
            localization_confidence=0.90,
            mode_stable=True,
            sync_quality=0.20,
        )

        self.assertEqual(assessment.trust_primary_reason_code, "sync_quality_low")

    def test_nominal_inputs_emit_nominal_reason_and_no_supporting_codes(self) -> None:
        assessment = TrustEngineService(DEFAULT_CONFIG).evaluate(
            scenario_id="s3_nominal",
            gnss_trust=0.90,
            gnss_state="nominal",
            vio_health_score=0.90,
            localization_confidence=0.90,
            mode_stable=True,
            sync_quality=0.95,
        )

        self.assertEqual(assessment.trust_primary_reason_code, "trust_inputs_nominal")
        self.assertEqual(assessment.trust_reason_codes, ())


if __name__ == "__main__":
    unittest.main()
