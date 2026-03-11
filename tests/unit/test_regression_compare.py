from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from common.config import load_app_config
from evaluation.artifact_schema import REPORT_SCHEMA_VERSION, SUMMARY_SCHEMA_VERSION
from evaluation.regression_compare import compare_reports
from evaluation.summary_report import generate_summary, write_summary_files


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


def _make_report(
    scenario_id: str,
    gnss_state: str,
    trust_score: float,
    mission_state: str,
    ate_m: float,
) -> dict:
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "run_id": "run_001",
        "scenario_id": scenario_id,
        "map_name": "test_map",
        "run_seed": 1,
        "gnss_condition": gnss_state,
        "gnss_state": gnss_state,
        "trust_score": trust_score,
        "mission_confidence": 0.9,
        "vio_healthy": True,
        "vio_state": "healthy",
        "mission_state": mission_state,
        "ate_m": ate_m,
        "route_length_m": 100.0,
        "ground_truth_usage": "evaluation_only",
        "config_id": "sim-v1",
        "software_revision": "test-revision",
        "timestamp": "2026-03-11T10:00:00Z",
        "scenario_metadata": {
            "title": scenario_id,
            "description": "test scenario",
            "owner": "test-suite",
        },
    }


class RegressionCompareTests(unittest.TestCase):
    def test_trust_ordering_passes_for_expected_reports(self) -> None:
        config = load_app_config(CONFIG_PATH)
        reports = {
            "s1_nominal": _make_report("s1_nominal", "nominal", 0.95, "MISSION_NORMAL", 0.5),
            "s2_gnss_degraded_corridor": _make_report(
                "s2_gnss_degraded_corridor", "degraded", 0.55, "MISSION_DEGRADED", 3.0
            ),
            "s3_gnss_denied_zone": _make_report(
                "s3_gnss_denied_zone", "denied", 0.05, "MISSION_FALLBACK", 8.0
            ),
        }

        result = compare_reports(reports, run_id="run_001", mission_config=config.mission)

        self.assertEqual(result["overall_result"], "PASS")
        trust_check = next(check for check in result["checks"] if check["name"] == "trust_ordering")
        self.assertTrue(trust_check["passed"])

    def test_mission_state_expectation_fails_for_denied_normal(self) -> None:
        config = load_app_config(CONFIG_PATH)
        reports = {
            "s1_nominal": _make_report("s1_nominal", "nominal", 0.95, "MISSION_NORMAL", 0.5),
            "s2_gnss_degraded_corridor": _make_report(
                "s2_gnss_degraded_corridor", "degraded", 0.55, "MISSION_DEGRADED", 3.0
            ),
            "s3_gnss_denied_zone": _make_report(
                "s3_gnss_denied_zone", "denied", 0.05, "MISSION_NORMAL", 8.0
            ),
        }

        result = compare_reports(reports, run_id="run_002", mission_config=config.mission)

        self.assertEqual(result["overall_result"], "FAIL")
        denied_check = next(check for check in result["checks"] if check["name"] == "denied_not_normal")
        self.assertFalse(denied_check["passed"])

    def test_summary_generation_writes_expected_shape(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_path = Path(temp_dir)
            config = load_app_config(CONFIG_PATH)
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

            regression_result = compare_reports(
                reports, run_id=base_path.name, mission_config=config.mission
            )
            summary, markdown = generate_summary(base_path, regression_result)
            summary_json_path, summary_md_path = write_summary_files(
                base_path, summary, markdown
            )

            self.assertEqual(summary["overall_regression_result"], "PASS")
            self.assertEqual(summary["schema_version"], SUMMARY_SCHEMA_VERSION)
            self.assertEqual(len(summary["scenarios"]), 3)
            self.assertTrue(summary_json_path.exists())
            self.assertTrue(summary_md_path.exists())
            self.assertIn("Regression Summary", summary_md_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
