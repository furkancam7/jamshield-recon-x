from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from evaluation.regression_compare import compare_reports
from evaluation.summary_report import generate_summary, write_summary_files


def _make_report(
    scenario_id: str,
    gnss_state: str,
    trust_score: float,
    mission_state: str,
    ate_m: float,
) -> dict:
    return {
        "scenario_id": scenario_id,
        "gnss_state": gnss_state,
        "trust_score": trust_score,
        "mission_state": mission_state,
        "ate_m": ate_m,
    }


class RegressionCompareTests(unittest.TestCase):
    def test_trust_ordering_passes_for_expected_reports(self) -> None:
        reports = {
            "s1_nominal": _make_report("s1_nominal", "nominal", 0.95, "MISSION_NORMAL", 0.5),
            "s2_gnss_degraded_corridor": _make_report(
                "s2_gnss_degraded_corridor", "degraded", 0.55, "MISSION_DEGRADED", 3.0
            ),
            "s3_gnss_denied_zone": _make_report(
                "s3_gnss_denied_zone", "denied", 0.05, "MISSION_FALLBACK", 8.0
            ),
        }

        result = compare_reports(reports, run_id="run_001")

        self.assertEqual(result["overall_result"], "PASS")
        trust_check = next(check for check in result["checks"] if check["name"] == "trust_ordering")
        self.assertTrue(trust_check["passed"])

    def test_mission_state_expectation_fails_for_denied_normal(self) -> None:
        reports = {
            "s1_nominal": _make_report("s1_nominal", "nominal", 0.95, "MISSION_NORMAL", 0.5),
            "s2_gnss_degraded_corridor": _make_report(
                "s2_gnss_degraded_corridor", "degraded", 0.55, "MISSION_DEGRADED", 3.0
            ),
            "s3_gnss_denied_zone": _make_report(
                "s3_gnss_denied_zone", "denied", 0.05, "MISSION_NORMAL", 8.0
            ),
        }

        result = compare_reports(reports, run_id="run_002")

        self.assertEqual(result["overall_result"], "FAIL")
        denied_check = next(check for check in result["checks"] if check["name"] == "denied_not_normal")
        self.assertFalse(denied_check["passed"])

    def test_summary_generation_writes_expected_shape(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            reports = {
                "s1_nominal": _make_report("s1_nominal", "nominal", 0.95, "MISSION_NORMAL", 0.5),
                "s2_gnss_degraded_corridor": _make_report(
                    "s2_gnss_degraded_corridor", "degraded", 0.55, "MISSION_DEGRADED", 3.0
                ),
                "s3_gnss_denied_zone": _make_report(
                    "s3_gnss_denied_zone", "denied", 0.05, "MISSION_FALLBACK", 8.0
                ),
            }
            for scenario_id, report in reports.items():
                (base_path / f"{scenario_id}_report.json").write_text(
                    json.dumps(report),
                    encoding="utf-8",
                )

            regression_result = compare_reports(reports, run_id=base_path.name)
            summary, markdown = generate_summary(base_path, regression_result)
            summary_json_path, summary_md_path = write_summary_files(
                base_path, summary, markdown
            )

            self.assertEqual(summary["overall_regression_result"], "PASS")
            self.assertEqual(len(summary["scenarios"]), 3)
            self.assertTrue(summary_json_path.exists())
            self.assertTrue(summary_md_path.exists())
            self.assertIn("Regression Summary", summary_md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
