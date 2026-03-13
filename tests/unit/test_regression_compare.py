from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest

from _support import make_temp_dir
from common.config import load_app_config
from evaluation.artifact_schema import (
    EW_RISK_MAP_SCHEMA_VERSION,
    MISSION_AUDIT_SCHEMA_VERSION,
    REPORT_SCHEMA_VERSION,
    SUMMARY_SCHEMA_VERSION,
    TACTICAL_SUMMARY_SCHEMA_VERSION,
)
from evaluation.regression_compare import EXPECTED_SCENARIO_IDS, compare_reports
from evaluation.summary_report import generate_summary, write_summary_files
from tactical_summary import TacticalSummaryInputs, TacticalSummaryService


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


def _risk_cells(width_cells: int, height_cells: int, max_risk: float, affected: int) -> list[float]:
    cells = [0.0] * (width_cells * height_cells)
    for index in range(min(affected, len(cells))):
        cells[index] = max_risk
    return cells


def _risk_cells_hash(cells: list[float]) -> str:
    return sha256(",".join(f"{value:.3f}" for value in cells).encode("utf-8")).hexdigest()


def _make_report(scenario_id: str, spec: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "run_id": "run_001",
        "scenario_id": scenario_id,
        "map_name": "test_range",
        "run_seed": 111,
        "gnss_condition": spec["gnss_condition"],
        "gnss_state": spec["gnss_state"],
        "gnss_trust": spec["gnss_trust"],
        "vio_trust": spec["vio_trust"],
        "sync_quality": spec["sync_quality"],
        "mission_confidence": spec["mission_confidence"],
        "trust_primary_reason_code": spec["trust_primary_reason_code"],
        "trust_reason_codes": list(spec["trust_reason_codes"]),
        "mission_state": spec["mission_state"],
        "mission_primary_reason_code": spec["mission_primary_reason_code"],
        "mission_reason_codes": list(spec["mission_reason_codes"]),
        "mission_transition_count": spec["mission_transition_count"],
        "mission_audit_path": f"{scenario_id}_mission_audit.json",
        "ew_risk_level": spec["ew_risk_level"],
        "ew_primary_reason_code": spec["ew_primary_reason_code"],
        "ew_reason_codes": list(spec["ew_reason_codes"]),
        "ew_max_risk": spec["ew_max_risk"],
        "ew_affected_cell_count": spec["ew_affected_cell_count"],
        "ew_corridor_cost": spec["ew_corridor_cost"],
        "ew_risk_map_path": f"{scenario_id}_ew_risk_map.json",
        "tactical_primary_reason_code": "",
        "tactical_reason_codes": [],
        "tactical_advisory_code": "",
        "tactical_advisory_text": "",
        "tactical_summary_text": "",
        "tactical_summary_path": f"{scenario_id}_tactical_summary.json",
        "runtime_trace_path": f"{scenario_id}_runtime_trace.json",
        "truth_trace_path": f"{scenario_id}_truth_trace.json",
        "vio_state": spec["vio_state"],
        "vio_health_score": spec["vio_trust"],
        "effective_vio_state": spec["effective_vio_state"],
        "ate_m": spec["ate_m"],
        "route_length_m": 120.0,
        "ground_truth_usage": "evaluation_only",
        "config_id": "sim-v1",
        "manifest_hash": f"manifest_{scenario_id}",
        "config_hash": "config_hash_v1",
        "evaluation_profile": spec.get(
            "evaluation_profile", "baseline_nominal_profile_v1"
        ),
        "deterministic_replay_passed": True,
        "evaluation_verdict": spec.get("evaluation_verdict", "PASS"),
        "invalid_run": False,
        "evaluation_primary_reason_code": spec.get(
            "evaluation_primary_reason_code", "evaluation_acceptance_passed"
        ),
        "software_revision": "test-revision",
        "timestamp": "2026-03-13T10:00:00Z",
        "scenario_metadata": {
            "title": scenario_id,
            "description": f"Fixture for {scenario_id}",
            "owner": "test-suite",
        },
        "vio_metrics_source": "pipeline_v1",
        "vio_metrics": {
            "timestamp_ns": 1,
            "profile_id": f"{scenario_id}_profile",
            "feature_count": 24,
            "matched_feature_count": 20,
            "track_continuity": 0.9,
            "reprojection_error_px": 0.2,
            "pose_delta_xy_m": 0.3,
            "yaw_delta_rad": 0.08,
            "imu_alignment_error": 0.04,
            "vio_health_score": spec["vio_trust"],
            "vio_state": spec["vio_metrics_state"],
            "effective_vio_state": spec["effective_vio_state"],
            "reason_codes": [] if float(spec["vio_trust"]) >= 0.55 else ["vio_trust_low"],
        },
        "localization_mode": spec["localization_mode"],
        "localization_confidence": spec["localization_confidence"],
        "gnss_weight": 0.6,
        "vio_weight": 0.4,
    }


def _make_tactical_summary(report: dict[str, object], service: TacticalSummaryService) -> dict[str, object]:
    assessment = service.evaluate(
        TacticalSummaryInputs(
            timestamp_ns=1,
            mission_state=str(report["mission_state"]),
            mission_primary_reason_code=str(report["mission_primary_reason_code"]),
            mission_confidence=float(report["mission_confidence"]),
            localization_mode=str(report["localization_mode"]),
            effective_vio_state=str(report["effective_vio_state"]),
            trust_primary_reason_code=str(report["trust_primary_reason_code"]),
            ew_risk_level=str(report["ew_risk_level"]),
            ew_primary_reason_code=str(report["ew_primary_reason_code"]),
            ew_corridor_cost=float(report["ew_corridor_cost"]),
            ew_affected_cell_count=int(report["ew_affected_cell_count"]),
        )
    )
    return {
        "schema_version": TACTICAL_SUMMARY_SCHEMA_VERSION,
        "run_id": str(report["run_id"]),
        "scenario_id": str(report["scenario_id"]),
        "timestamp_ns": 1,
        "mission_state": assessment.mission_state,
        "mission_confidence": assessment.mission_confidence,
        "localization_mode": assessment.localization_mode,
        "ew_risk_level": assessment.ew_risk_level,
        "affected_area_count": assessment.affected_area_count,
        "ew_corridor_cost": assessment.ew_corridor_cost,
        "primary_reason_code": assessment.primary_reason_code,
        "reason_codes": list(assessment.reason_codes),
        "advisory_code": assessment.advisory_code,
        "advisory_text": assessment.advisory_text,
        "summary_text": assessment.summary_text,
    }


def _make_ew_map(report: dict[str, object]) -> dict[str, object]:
    width_cells = 10
    height_cells = 10
    cells = _risk_cells(width_cells, height_cells, float(report["ew_max_risk"]), int(report["ew_affected_cell_count"]))
    return {
        "schema_version": EW_RISK_MAP_SCHEMA_VERSION,
        "run_id": str(report["run_id"]),
        "scenario_id": str(report["scenario_id"]),
        "timestamp_ns": 1,
        "frame_id": "map",
        "cell_size_m": 20.0,
        "width_cells": width_cells,
        "height_cells": height_cells,
        "origin": {"x_m": -20.0, "y_m": -20.0},
        "risk_cells": cells,
        "evidence_codes": list(report["ew_reason_codes"]),
        "primary_reason_code": str(report["ew_primary_reason_code"]),
        "reason_codes": list(report["ew_reason_codes"]),
        "max_risk": float(report["ew_max_risk"]),
        "affected_cell_count": int(report["ew_affected_cell_count"]),
        "corridor_cost": float(report["ew_corridor_cost"]),
        "risk_cells_hash": _risk_cells_hash(cells),
    }


def _entry(
    tick_index: int,
    candidate_state: str,
    final_state: str,
    primary_reason_code: str,
    transition_count: int,
    trust_primary_reason_code: str,
    mission_confidence: float,
    effective_vio_state: str,
) -> dict[str, object]:
    return {
        "tick_index": tick_index,
        "step_inputs": {"tick_index": tick_index},
        "gnss_state": "nominal",
        "mission_confidence": mission_confidence,
        "effective_vio_state": effective_vio_state,
        "trust_primary_reason_code": trust_primary_reason_code,
        "candidate_state": candidate_state,
        "final_state": final_state,
        "primary_reason_code": primary_reason_code,
        "reason_codes": [primary_reason_code],
        "transition_count": transition_count,
    }


def _make_audit(report: dict[str, object]) -> dict[str, object]:
    scenario_id = str(report["scenario_id"])
    final_state = str(report["mission_state"])
    primary_reason_code = str(report["mission_primary_reason_code"])
    transition_count = int(report["mission_transition_count"])
    trust_primary_reason_code = str(report["trust_primary_reason_code"])
    mission_confidence = float(report["mission_confidence"])
    effective_vio_state = str(report["effective_vio_state"])
    entries = [
        _entry(
            0,
            final_state,
            final_state,
            primary_reason_code,
            transition_count,
            trust_primary_reason_code,
            mission_confidence,
            effective_vio_state,
        )
    ]
    if scenario_id == "s15_safe_hold_timeout_abort":
        entries = [
            _entry(0, "MISSION_SAFE_HOLD", "MISSION_SAFE_HOLD", "mission_safe_hold_vio_weak", 1, trust_primary_reason_code, 0.24, "weak"),
            _entry(1, "MISSION_SAFE_HOLD", "MISSION_SAFE_HOLD", "mission_safe_hold_vio_weak", 1, trust_primary_reason_code, 0.22, "weak"),
            _entry(2, final_state, final_state, primary_reason_code, transition_count, trust_primary_reason_code, mission_confidence, effective_vio_state),
        ]
    if scenario_id == "s16_recovery_dwell_delays_resume":
        entries = [
            _entry(0, "MISSION_FALLBACK", "MISSION_FALLBACK", "mission_fallback_vio_primary", 1, trust_primary_reason_code, 0.36, "good"),
            _entry(1, "MISSION_EXECUTE", "MISSION_FALLBACK", "mission_recovery_dwell_active", 1, trust_primary_reason_code, 0.92, "good"),
            _entry(2, final_state, final_state, primary_reason_code, transition_count, trust_primary_reason_code, mission_confidence, effective_vio_state),
        ]
    if scenario_id == "s17_state_oscillation_safe_hold":
        entries = [
            _entry(0, "MISSION_DEGRADED", "MISSION_DEGRADED", "mission_degraded_gnss_reduced", 1, trust_primary_reason_code, 0.62, "good"),
            _entry(1, "MISSION_EXECUTE", "MISSION_DEGRADED", "mission_recovery_dwell_active", 1, trust_primary_reason_code, 0.92, "good"),
            _entry(2, final_state, final_state, primary_reason_code, transition_count, trust_primary_reason_code, mission_confidence, effective_vio_state),
        ]
    return {
        "schema_version": MISSION_AUDIT_SCHEMA_VERSION,
        "run_id": str(report["run_id"]),
        "scenario_id": scenario_id,
        "entries": entries,
    }


class RegressionCompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_app_config(CONFIG_PATH)
        cls.tactical_service = TacticalSummaryService()

    def test_compare_reports_passes_for_aligned_fixture_set(self) -> None:
        reports, mission_audits, ew_maps, tactical_summaries = self._build_fixture_set()
        result = compare_reports(
            reports,
            run_id="run_001",
            mission_audits=mission_audits,
            ew_risk_maps=ew_maps,
            tactical_summaries=tactical_summaries,
            mission_config=self.config.mission,
            ew_risk_config=self.config.ew_risk_map,
        )
        self.assertEqual(result["overall_result"], "PASS")
        self.assertTrue(all(check["passed"] for check in result["checks"]))

    def test_summary_generation_includes_tactical_columns(self) -> None:
        run_dir = make_temp_dir(self)
        reports, mission_audits, ew_maps, tactical_summaries = self._build_fixture_set()
        for scenario_id in EXPECTED_SCENARIO_IDS:
            (run_dir / f"{scenario_id}_report.json").write_text(json.dumps(reports[scenario_id], indent=2, sort_keys=True), encoding="utf-8")
            (run_dir / f"{scenario_id}_mission_audit.json").write_text(json.dumps(mission_audits[scenario_id], indent=2, sort_keys=True), encoding="utf-8")
            (run_dir / f"{scenario_id}_ew_risk_map.json").write_text(json.dumps(ew_maps[scenario_id], indent=2, sort_keys=True), encoding="utf-8")
            (run_dir / f"{scenario_id}_tactical_summary.json").write_text(json.dumps(tactical_summaries[scenario_id], indent=2, sort_keys=True), encoding="utf-8")

        regression_result = compare_reports(
            reports,
            run_id=run_dir.name,
            mission_audits=mission_audits,
            ew_risk_maps=ew_maps,
            tactical_summaries=tactical_summaries,
            mission_config=self.config.mission,
            ew_risk_config=self.config.ew_risk_map,
        )
        summary, markdown = generate_summary(run_dir, regression_result)
        summary_json_path, summary_md_path = write_summary_files(run_dir, summary, markdown)

        self.assertEqual(summary["schema_version"], SUMMARY_SCHEMA_VERSION)
        self.assertIn("baseline_nominal_profile_v1", summary["evaluation_profiles"])
        self.assertIn("urban_canyon_profile_v1", summary["evaluation_profiles"])
        self.assertIn("tactical_primary_reason_code", summary["scenarios"][0])
        self.assertIn("Eval Verdict", markdown)
        self.assertTrue(summary_json_path.exists())
        self.assertTrue(summary_md_path.exists())

    def _build_fixture_set(self) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]], dict[str, dict[str, object]], dict[str, dict[str, object]]]:
        specs = {
            "s1_nominal": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.96, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.94, sync_quality=1.0, mission_confidence=0.96, trust_primary_reason_code="trust_inputs_nominal", trust_reason_codes=[], mission_state="MISSION_EXECUTE", mission_primary_reason_code="mission_execute_nominal", mission_reason_codes=["mission_execute_nominal"], mission_transition_count=0, ew_risk_level="none", ew_primary_reason_code="ew_risk_nominal", ew_reason_codes=[], ew_max_risk=0.0, ew_affected_cell_count=0, ew_corridor_cost=0.0, localization_mode="GNSS_PRIMARY", localization_confidence=0.95, ate_m=0.5, evaluation_profile="baseline_nominal_profile_v1"),
            "s2_gnss_degraded_corridor": dict(gnss_condition="degraded", gnss_state="degraded", gnss_trust=0.66, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.91, sync_quality=1.0, mission_confidence=0.62, trust_primary_reason_code="gnss_measurement_quality_low", trust_reason_codes=["gnss_measurement_quality_low"], mission_state="MISSION_DEGRADED", mission_primary_reason_code="mission_degraded_gnss_reduced", mission_reason_codes=["mission_degraded_gnss_reduced"], mission_transition_count=1, ew_risk_level="medium", ew_primary_reason_code="ew_gnss_degraded_corridor", ew_reason_codes=["gnss_measurement_quality_low"], ew_max_risk=0.58, ew_affected_cell_count=12, ew_corridor_cost=0.35, localization_mode="BLENDED", localization_confidence=0.72, ate_m=0.7, evaluation_profile="urban_canyon_profile_v1"),
            "s3_gnss_denied_zone": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.90, sync_quality=1.0, mission_confidence=0.34, trust_primary_reason_code="gnss_denial_suspected", trust_reason_codes=["gnss_denial_suspected"], mission_state="MISSION_FALLBACK", mission_primary_reason_code="mission_fallback_vio_primary", mission_reason_codes=["mission_fallback_vio_primary"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_gnss_denial_hotspot", ew_reason_codes=["gnss_denial_suspected", "vio_primary_active"], ew_max_risk=0.88, ew_affected_cell_count=18, ew_corridor_cost=0.65, localization_mode="VIO_PRIMARY", localization_confidence=0.58, ate_m=1.1),
            "s4_denied_vio_good": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.93, sync_quality=1.0, mission_confidence=0.35, trust_primary_reason_code="gnss_denial_suspected", trust_reason_codes=["gnss_denial_suspected"], mission_state="MISSION_FALLBACK", mission_primary_reason_code="mission_fallback_vio_primary", mission_reason_codes=["mission_fallback_vio_primary"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_gnss_denial_hotspot", ew_reason_codes=["gnss_denial_suspected", "vio_primary_active"], ew_max_risk=0.80, ew_affected_cell_count=16, ew_corridor_cost=0.60, localization_mode="VIO_PRIMARY", localization_confidence=0.60, ate_m=1.0),
            "s5_denied_vio_weak": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="weak", effective_vio_state="weak", vio_metrics_state="weak", vio_trust=0.45, sync_quality=1.0, mission_confidence=0.24, trust_primary_reason_code="vio_trust_low", trust_reason_codes=["vio_trust_low"], mission_state="MISSION_SAFE_HOLD", mission_primary_reason_code="mission_safe_hold_vio_weak", mission_reason_codes=["mission_safe_hold_vio_weak"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_localization_instability", ew_reason_codes=["localization_confidence_low", "hold_last_safe_active"], ew_max_risk=0.82, ew_affected_cell_count=20, ew_corridor_cost=0.70, localization_mode="HOLD_LAST_SAFE", localization_confidence=0.31, ate_m=1.8),
            "s6_denied_vio_lost": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="lost", effective_vio_state="lost", vio_metrics_state="lost", vio_trust=0.0, sync_quality=1.0, mission_confidence=0.07, trust_primary_reason_code="vio_trust_low", trust_reason_codes=["vio_trust_low"], mission_state="MISSION_ABORT", mission_primary_reason_code="mission_abort_vio_lost", mission_reason_codes=["mission_abort_vio_lost"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_localization_instability", ew_reason_codes=["localization_confidence_low", "hold_last_safe_active"], ew_max_risk=0.90, ew_affected_cell_count=25, ew_corridor_cost=0.75, localization_mode="HOLD_LAST_SAFE", localization_confidence=0.18, ate_m=2.2),
            "s7_conflict_score_dominates": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="good", effective_vio_state="lost", vio_metrics_state="lost", vio_trust=0.10, sync_quality=1.0, mission_confidence=0.10, trust_primary_reason_code="vio_trust_low", trust_reason_codes=["vio_trust_low"], mission_state="MISSION_ABORT", mission_primary_reason_code="mission_abort_vio_lost", mission_reason_codes=["mission_abort_vio_lost"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_localization_instability", ew_reason_codes=["localization_confidence_low", "hold_last_safe_active"], ew_max_risk=0.78, ew_affected_cell_count=14, ew_corridor_cost=0.68, localization_mode="HOLD_LAST_SAFE", localization_confidence=0.20, ate_m=2.0),
            "s8_conflict_state_dominates": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="lost", effective_vio_state="lost", vio_metrics_state="good", vio_trust=0.12, sync_quality=1.0, mission_confidence=0.11, trust_primary_reason_code="vio_trust_low", trust_reason_codes=["vio_trust_low"], mission_state="MISSION_ABORT", mission_primary_reason_code="mission_abort_vio_lost", mission_reason_codes=["mission_abort_vio_lost"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_localization_instability", ew_reason_codes=["localization_confidence_low", "hold_last_safe_active"], ew_max_risk=0.79, ew_affected_cell_count=15, ew_corridor_cost=0.69, localization_mode="HOLD_LAST_SAFE", localization_confidence=0.21, ate_m=2.0),
            "s9_fusion_gnss_primary": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.95, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.93, sync_quality=1.0, mission_confidence=0.95, trust_primary_reason_code="trust_inputs_nominal", trust_reason_codes=[], mission_state="MISSION_EXECUTE", mission_primary_reason_code="mission_execute_nominal", mission_reason_codes=["mission_execute_nominal"], mission_transition_count=0, ew_risk_level="none", ew_primary_reason_code="ew_risk_nominal", ew_reason_codes=[], ew_max_risk=0.0, ew_affected_cell_count=0, ew_corridor_cost=0.0, localization_mode="GNSS_PRIMARY", localization_confidence=0.92, ate_m=0.4),
            "s10_fusion_degraded_fused": dict(gnss_condition="degraded", gnss_state="degraded", gnss_trust=0.64, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.90, sync_quality=1.0, mission_confidence=0.63, trust_primary_reason_code="gnss_measurement_quality_low", trust_reason_codes=["gnss_measurement_quality_low"], mission_state="MISSION_DEGRADED", mission_primary_reason_code="mission_degraded_gnss_reduced", mission_reason_codes=["mission_degraded_gnss_reduced"], mission_transition_count=1, ew_risk_level="medium", ew_primary_reason_code="ew_gnss_degraded_corridor", ew_reason_codes=["gnss_measurement_quality_low"], ew_max_risk=0.57, ew_affected_cell_count=11, ew_corridor_cost=0.36, localization_mode="BLENDED", localization_confidence=0.65, ate_m=0.8),
            "s11_fusion_denied_vio_only": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.89, sync_quality=1.0, mission_confidence=0.36, trust_primary_reason_code="gnss_denial_suspected", trust_reason_codes=["gnss_denial_suspected"], mission_state="MISSION_FALLBACK", mission_primary_reason_code="mission_fallback_vio_primary", mission_reason_codes=["mission_fallback_vio_primary"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_gnss_denial_hotspot", ew_reason_codes=["gnss_denial_suspected", "vio_primary_active"], ew_max_risk=0.83, ew_affected_cell_count=17, ew_corridor_cost=0.62, localization_mode="VIO_PRIMARY", localization_confidence=0.55, ate_m=1.2),
            "s12_fusion_dead_reckoning": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="lost", effective_vio_state="lost", vio_metrics_state="lost", vio_trust=0.12, sync_quality=1.0, mission_confidence=0.18, trust_primary_reason_code="localization_confidence_low", trust_reason_codes=["localization_confidence_low", "vio_trust_low"], mission_state="MISSION_SAFE_HOLD", mission_primary_reason_code="mission_safe_hold_localization_unstable", mission_reason_codes=["mission_safe_hold_localization_unstable"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_localization_instability", ew_reason_codes=["localization_confidence_low", "hold_last_safe_active"], ew_max_risk=0.76, ew_affected_cell_count=17, ew_corridor_cost=0.66, localization_mode="HOLD_LAST_SAFE", localization_confidence=0.22, ate_m=2.0),
            "s13_sync_low_nominal": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.95, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.94, sync_quality=0.45, mission_confidence=0.92, trust_primary_reason_code="sync_quality_low", trust_reason_codes=["sync_quality_low"], mission_state="MISSION_EXECUTE", mission_primary_reason_code="mission_execute_nominal", mission_reason_codes=["mission_execute_nominal"], mission_transition_count=0, ew_risk_level="low", ew_primary_reason_code="ew_sync_instability_corridor", ew_reason_codes=["sync_quality_low"], ew_max_risk=0.28, ew_affected_cell_count=4, ew_corridor_cost=0.08, localization_mode="GNSS_PRIMARY", localization_confidence=0.93, ate_m=0.6),
            "s14_sync_low_denied_good": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.89, sync_quality=0.45, mission_confidence=0.30, trust_primary_reason_code="sync_quality_low", trust_reason_codes=["sync_quality_low", "gnss_denial_suspected"], mission_state="MISSION_FALLBACK", mission_primary_reason_code="mission_fallback_vio_primary", mission_reason_codes=["mission_fallback_vio_primary"], mission_transition_count=1, ew_risk_level="high", ew_primary_reason_code="ew_sync_instability_corridor", ew_reason_codes=["sync_quality_low", "gnss_denial_suspected"], ew_max_risk=0.84, ew_affected_cell_count=19, ew_corridor_cost=0.69, localization_mode="VIO_PRIMARY", localization_confidence=0.50, ate_m=1.3),
            "s15_safe_hold_timeout_abort": dict(gnss_condition="denied", gnss_state="denied", gnss_trust=0.05, vio_state="weak", effective_vio_state="weak", vio_metrics_state="weak", vio_trust=0.40, sync_quality=1.0, mission_confidence=0.19, trust_primary_reason_code="vio_trust_low", trust_reason_codes=["vio_trust_low"], mission_state="MISSION_ABORT", mission_primary_reason_code="mission_abort_safe_hold_timeout", mission_reason_codes=["mission_abort_safe_hold_timeout"], mission_transition_count=2, ew_risk_level="high", ew_primary_reason_code="ew_localization_instability", ew_reason_codes=["localization_confidence_low"], ew_max_risk=0.74, ew_affected_cell_count=13, ew_corridor_cost=0.67, localization_mode="HOLD_LAST_SAFE", localization_confidence=0.28, ate_m=1.9),
            "s16_recovery_dwell_delays_resume": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.95, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.92, sync_quality=1.0, mission_confidence=0.94, trust_primary_reason_code="trust_inputs_nominal", trust_reason_codes=[], mission_state="MISSION_EXECUTE", mission_primary_reason_code="mission_execute_nominal", mission_reason_codes=["mission_execute_nominal"], mission_transition_count=2, ew_risk_level="none", ew_primary_reason_code="ew_risk_nominal", ew_reason_codes=[], ew_max_risk=0.0, ew_affected_cell_count=0, ew_corridor_cost=0.0, localization_mode="GNSS_PRIMARY", localization_confidence=0.92, ate_m=0.5),
            "s17_state_oscillation_safe_hold": dict(gnss_condition="degraded", gnss_state="degraded", gnss_trust=0.60, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.88, sync_quality=1.0, mission_confidence=0.58, trust_primary_reason_code="gnss_measurement_quality_low", trust_reason_codes=["gnss_measurement_quality_low"], mission_state="MISSION_SAFE_HOLD", mission_primary_reason_code="mission_state_oscillation_detected", mission_reason_codes=["mission_state_oscillation_detected"], mission_transition_count=3, ew_risk_level="medium", ew_primary_reason_code="ew_gnss_degraded_corridor", ew_reason_codes=["gnss_measurement_quality_low"], ew_max_risk=0.56, ew_affected_cell_count=9, ew_corridor_cost=0.37, localization_mode="BLENDED", localization_confidence=0.68, ate_m=0.9),
            "s18_abort_terminal": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.95, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.91, sync_quality=1.0, mission_confidence=0.90, trust_primary_reason_code="trust_inputs_nominal", trust_reason_codes=[], mission_state="MISSION_ABORT", mission_primary_reason_code="mission_abort_terminal_latched", mission_reason_codes=["mission_abort_terminal_latched"], mission_transition_count=1, ew_risk_level="none", ew_primary_reason_code="ew_risk_nominal", ew_reason_codes=[], ew_max_risk=0.0, ew_affected_cell_count=0, ew_corridor_cost=0.0, localization_mode="GNSS_PRIMARY", localization_confidence=0.94, ate_m=0.6),
            "s19_ew_mid_route_denial_hotspot": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.94, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.93, sync_quality=1.0, mission_confidence=0.93, trust_primary_reason_code="trust_inputs_nominal", trust_reason_codes=[], mission_state="MISSION_EXECUTE", mission_primary_reason_code="mission_execute_nominal", mission_reason_codes=["mission_execute_nominal"], mission_transition_count=0, ew_risk_level="high", ew_primary_reason_code="ew_gnss_denial_hotspot", ew_reason_codes=["gnss_denial_suspected"], ew_max_risk=0.92, ew_affected_cell_count=20, ew_corridor_cost=0.80, localization_mode="GNSS_PRIMARY", localization_confidence=0.93, ate_m=0.6),
            "s20_ew_decay_after_recovery": dict(gnss_condition="nominal", gnss_state="nominal", gnss_trust=0.94, vio_state="good", effective_vio_state="good", vio_metrics_state="good", vio_trust=0.93, sync_quality=1.0, mission_confidence=0.93, trust_primary_reason_code="trust_inputs_nominal", trust_reason_codes=[], mission_state="MISSION_EXECUTE", mission_primary_reason_code="mission_execute_nominal", mission_reason_codes=["mission_execute_nominal"], mission_transition_count=0, ew_risk_level="low", ew_primary_reason_code="ew_gnss_degraded_corridor", ew_reason_codes=["gnss_measurement_quality_low"], ew_max_risk=0.40, ew_affected_cell_count=8, ew_corridor_cost=0.30, localization_mode="GNSS_PRIMARY", localization_confidence=0.93, ate_m=0.6),
        }

        reports = {scenario_id: _make_report(scenario_id, specs[scenario_id]) for scenario_id in EXPECTED_SCENARIO_IDS}
        tactical_summaries: dict[str, dict[str, object]] = {}
        mission_audits: dict[str, dict[str, object]] = {}
        ew_maps: dict[str, dict[str, object]] = {}

        for scenario_id, report in reports.items():
            tactical_summary = _make_tactical_summary(report, self.tactical_service)
            report["tactical_primary_reason_code"] = tactical_summary["primary_reason_code"]
            report["tactical_reason_codes"] = tactical_summary["reason_codes"]
            report["tactical_advisory_code"] = tactical_summary["advisory_code"]
            report["tactical_advisory_text"] = tactical_summary["advisory_text"]
            report["tactical_summary_text"] = tactical_summary["summary_text"]
            tactical_summaries[scenario_id] = tactical_summary
            mission_audits[scenario_id] = _make_audit(report)
            ew_maps[scenario_id] = _make_ew_map(report)

        return reports, mission_audits, ew_maps, tactical_summaries


if __name__ == "__main__":
    unittest.main()
