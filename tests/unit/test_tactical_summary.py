from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.artifact_schema import (
    TACTICAL_SUMMARY_BUNDLE_SCHEMA_VERSION,
    TACTICAL_SUMMARY_SCHEMA_VERSION,
    validate_tactical_summary,
    validate_tactical_summary_bundle,
)
from evaluation.tactical_summary_bundle import (
    generate_tactical_summary_bundle,
    write_tactical_summary_bundle_files,
)
from tactical_summary import TacticalSummaryInputs, TacticalSummaryService


class TacticalSummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = TacticalSummaryService()

    def test_abort_precedence_overrides_other_signals(self) -> None:
        assessment = self.service.evaluate(
            TacticalSummaryInputs(
                timestamp_ns=10,
                mission_state="MISSION_ABORT",
                mission_primary_reason_code="mission_abort_vio_lost",
                mission_confidence=0.08,
                localization_mode="HOLD_LAST_SAFE",
                effective_vio_state="lost",
                trust_primary_reason_code="sync_quality_low",
                ew_risk_level="high",
                ew_primary_reason_code="ew_gnss_denial_hotspot",
                ew_corridor_cost=0.5,
                ew_affected_cell_count=7,
            )
        )

        self.assertEqual(assessment.primary_reason_code, "tactical_abort_active")
        self.assertEqual(assessment.advisory_code, "operator_abort_and_retask")
        self.assertIn("tactical_ew_hotspot_detected", assessment.reason_codes)

    def test_sync_caution_is_deterministic_for_execute_state(self) -> None:
        assessment = self.service.evaluate(
            TacticalSummaryInputs(
                timestamp_ns=10,
                mission_state="MISSION_EXECUTE",
                mission_primary_reason_code="mission_execute_nominal",
                mission_confidence=0.88,
                localization_mode="GNSS_PRIMARY",
                effective_vio_state="good",
                trust_primary_reason_code="sync_quality_low",
                ew_risk_level="low",
                ew_primary_reason_code="ew_sync_instability_corridor",
                ew_corridor_cost=0.05,
                ew_affected_cell_count=0,
            )
        )

        self.assertEqual(assessment.primary_reason_code, "tactical_sync_risk_observed")
        self.assertEqual(assessment.advisory_code, "operator_continue_with_caution")
        self.assertEqual(assessment.summary_text.count("."), 2)

    def test_tactical_summary_schema_accepts_valid_payload(self) -> None:
        payload = {
            "schema_version": TACTICAL_SUMMARY_SCHEMA_VERSION,
            "run_id": "run_001",
            "scenario_id": "s1_nominal",
            "timestamp_ns": 1,
            "mission_state": "MISSION_EXECUTE",
            "mission_confidence": 0.95,
            "localization_mode": "GNSS_PRIMARY",
            "ew_risk_level": "none",
            "affected_area_count": 0,
            "ew_corridor_cost": 0.0,
            "primary_reason_code": "tactical_nominal_overview",
            "reason_codes": ["tactical_nominal_overview"],
            "advisory_code": "operator_continue_nominal",
            "advisory_text": "Continue mission on the current route.",
            "summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
        }

        validate_tactical_summary(payload)

    def test_bundle_generation_writes_expected_shape(self) -> None:
        reports = {
            "s1_nominal": {
                "mission_state": "MISSION_EXECUTE",
                "tactical_primary_reason_code": "tactical_nominal_overview",
                "tactical_advisory_code": "operator_continue_nominal",
                "tactical_summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
                "tactical_summary_path": "s1_nominal_tactical_summary.json",
            }
        }
        tactical_summaries = {
            "s1_nominal": {
                "schema_version": TACTICAL_SUMMARY_SCHEMA_VERSION,
                "run_id": "run_001",
                "scenario_id": "s1_nominal",
                "timestamp_ns": 1,
                "mission_state": "MISSION_EXECUTE",
                "mission_confidence": 0.95,
                "localization_mode": "GNSS_PRIMARY",
                "ew_risk_level": "none",
                "affected_area_count": 0,
                "ew_corridor_cost": 0.0,
                "primary_reason_code": "tactical_nominal_overview",
                "reason_codes": ["tactical_nominal_overview"],
                "advisory_code": "operator_continue_nominal",
                "advisory_text": "Continue mission on the current route.",
                "summary_text": "Mission is executing with GNSS-primary localization; EW risk is none. Continue mission on the current route.",
            }
        }
        regression_result = {"run_id": "run_001", "checks": [], "overall_result": "PASS"}

        bundle = generate_tactical_summary_bundle(
            reports=reports,
            tactical_summaries=tactical_summaries,
            regression_result=regression_result,
        )
        validate_tactical_summary_bundle(bundle)
        self.assertEqual(bundle["schema_version"], TACTICAL_SUMMARY_BUNDLE_SCHEMA_VERSION)

        output_dir = make_temp_dir(self)
        json_path, md_path, csv_path = write_tactical_summary_bundle_files(
            output_dir,
            bundle,
        )
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        self.assertTrue(csv_path.exists())


if __name__ == "__main__":
    unittest.main()
