"""Regression comparison for baseline scenario artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from common.config import EwRiskMapConfig, MissionConfig, load_app_config
from evaluation.artifact_schema import (
    validate_ew_risk_map,
    validate_mission_audit,
    validate_report,
    validate_tactical_summary,
)

EXPECTED_SCENARIO_IDS = [
    "s1_nominal",
    "s2_gnss_degraded_corridor",
    "s3_gnss_denied_zone",
    "s4_denied_vio_good",
    "s5_denied_vio_weak",
    "s6_denied_vio_lost",
    "s7_conflict_score_dominates",
    "s8_conflict_state_dominates",
    "s9_fusion_gnss_primary",
    "s10_fusion_degraded_fused",
    "s11_fusion_denied_vio_only",
    "s12_fusion_dead_reckoning",
    "s13_sync_low_nominal",
    "s14_sync_low_denied_good",
    "s15_safe_hold_timeout_abort",
    "s16_recovery_dwell_delays_resume",
    "s17_state_oscillation_safe_hold",
    "s18_abort_terminal",
    "s19_ew_mid_route_denial_hotspot",
    "s20_ew_decay_after_recovery",
]


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


def load_reports(run_dir: str | Path) -> dict[str, dict[str, Any]]:
    base_path = Path(run_dir)
    reports: dict[str, dict[str, Any]] = {}

    for scenario_id in EXPECTED_SCENARIO_IDS:
        report_path = base_path / f"{scenario_id}_report.json"
        if not report_path.exists():
            raise FileNotFoundError(f"Missing report artifact: {report_path}")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        validate_report(report)
        reports[scenario_id] = report

    return reports


def load_mission_audits(
    run_dir: str | Path,
    reports: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    base_path = Path(run_dir)
    resolved_reports = reports if reports is not None else load_reports(base_path)
    audits: dict[str, dict[str, Any]] = {}

    for scenario_id in EXPECTED_SCENARIO_IDS:
        report = resolved_reports[scenario_id]
        audit_path = Path(report["mission_audit_path"])
        if not audit_path.is_absolute():
            audit_path = base_path / audit_path
        if not audit_path.exists():
            raise FileNotFoundError(f"Missing mission audit artifact: {audit_path}")
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        validate_mission_audit(audit)
        audits[scenario_id] = audit

    return audits


def load_ew_risk_maps(
    run_dir: str | Path,
    reports: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    base_path = Path(run_dir)
    resolved_reports = reports if reports is not None else load_reports(base_path)
    ew_maps: dict[str, dict[str, Any]] = {}

    for scenario_id in EXPECTED_SCENARIO_IDS:
        report = resolved_reports[scenario_id]
        map_path = Path(report["ew_risk_map_path"])
        if not map_path.is_absolute():
            map_path = base_path / map_path
        if not map_path.exists():
            raise FileNotFoundError(f"Missing EW risk-map artifact: {map_path}")
        ew_map = json.loads(map_path.read_text(encoding="utf-8"))
        validate_ew_risk_map(ew_map)
        ew_maps[scenario_id] = ew_map

    return ew_maps


def load_tactical_summaries(
    run_dir: str | Path,
    reports: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    base_path = Path(run_dir)
    resolved_reports = reports if reports is not None else load_reports(base_path)
    tactical_summaries: dict[str, dict[str, Any]] = {}

    for scenario_id in EXPECTED_SCENARIO_IDS:
        report = resolved_reports[scenario_id]
        summary_path = Path(report["tactical_summary_path"])
        if not summary_path.is_absolute():
            summary_path = base_path / summary_path
        if not summary_path.exists():
            raise FileNotFoundError(
                f"Missing tactical summary artifact: {summary_path}"
            )
        tactical_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        validate_tactical_summary(tactical_summary)
        tactical_summaries[scenario_id] = tactical_summary

    return tactical_summaries


def compare_reports(
    reports: dict[str, dict[str, Any]],
    run_id: str,
    *,
    mission_audits: dict[str, dict[str, Any]] | None = None,
    ew_risk_maps: dict[str, dict[str, Any]] | None = None,
    tactical_summaries: dict[str, dict[str, Any]] | None = None,
    mission_config: MissionConfig | None = None,
    ew_risk_config: EwRiskMapConfig | None = None,
    nominal_minimum_trust: float = 0.90,
) -> dict[str, Any]:
    audits = mission_audits or {}
    ew_maps = ew_risk_maps or {}
    tactical = tactical_summaries or {}
    nominal = reports["s1_nominal"]
    degraded = reports["s2_gnss_degraded_corridor"]
    denied = reports["s3_gnss_denied_zone"]
    denied_good = reports["s4_denied_vio_good"]
    denied_weak = reports["s5_denied_vio_weak"]
    denied_lost = reports["s6_denied_vio_lost"]
    conflict_score = reports["s7_conflict_score_dominates"]
    conflict_state = reports["s8_conflict_state_dominates"]
    fusion_primary = reports["s9_fusion_gnss_primary"]
    fusion_blended = reports["s10_fusion_degraded_fused"]
    fusion_vio_primary = reports["s11_fusion_denied_vio_only"]
    fusion_hold_last_safe = reports["s12_fusion_dead_reckoning"]
    sync_low_nominal = reports["s13_sync_low_nominal"]
    sync_low_denied_good = reports["s14_sync_low_denied_good"]
    safe_hold_timeout = reports["s15_safe_hold_timeout_abort"]
    recovery_dwell = reports["s16_recovery_dwell_delays_resume"]
    oscillation = reports["s17_state_oscillation_safe_hold"]
    abort_terminal = reports["s18_abort_terminal"]
    ew_hotspot = reports["s19_ew_mid_route_denial_hotspot"]
    ew_decay = reports["s20_ew_decay_after_recovery"]
    denied_allowed_states = (
        set(mission_config.denied_allowed_states)
        if mission_config
        else {"MISSION_FALLBACK", "MISSION_SAFE_HOLD", "MISSION_ABORT"}
    )
    risk_low_floor = ew_risk_config.risk_low_floor if ew_risk_config else 0.25
    risk_medium_floor = ew_risk_config.risk_medium_floor if ew_risk_config else 0.55
    legacy_mission_states = {"MISSION_NORMAL", "MISSION_RTL", "MISSION_EMERGENCY_LAND"}
    legacy_localization_modes = {"FUSED", "VIO_ONLY", "DEAD_RECKONING"}

    checks = [
        CheckResult(
            name="gnss_trust_ordering",
            passed=(
                nominal["gnss_trust"] > degraded["gnss_trust"] > denied["gnss_trust"]
            ),
            detail=(
                "Expected nominal gnss_trust > degraded gnss_trust > denied gnss_trust."
            ),
        ),
        CheckResult(
            name="denied_not_execute",
            passed=denied["mission_state"] != "MISSION_EXECUTE",
            detail="Denied scenario must not end in MISSION_EXECUTE.",
        ),
        CheckResult(
            name="degraded_not_denied",
            passed=degraded["gnss_state"] != "denied",
            detail="Degraded scenario must not be classified as denied.",
        ),
        CheckResult(
            name="nominal_not_abort",
            passed=nominal["mission_state"] != "MISSION_ABORT",
            detail="Nominal scenario must not collapse to MISSION_ABORT.",
        ),
        CheckResult(
            name="nominal_minimum_gnss_trust_threshold",
            passed=nominal["gnss_trust"] >= nominal_minimum_trust,
            detail=(
                f"Nominal scenario gnss_trust must remain at or above {nominal_minimum_trust:.2f}."
            ),
        ),
        CheckResult(
            name="denied_allowed_mission_states",
            passed=denied["mission_state"] in denied_allowed_states,
            detail="Denied scenario must end in the allowed denied-state set.",
        ),
        CheckResult(
            name="p4_vio_good_fallback",
            passed=(
                denied_good["effective_vio_state"] == "good"
                and denied_good["mission_state"] == "MISSION_FALLBACK"
            ),
            detail="Denied + nominal VIO pipeline must stay in fallback-capable state.",
        ),
        CheckResult(
            name="p4_vio_weak_safe_hold",
            passed=(
                denied_weak["effective_vio_state"] == "weak"
                and denied_weak["mission_state"] == "MISSION_SAFE_HOLD"
            ),
            detail="Denied + weak-texture VIO pipeline must produce weak VIO and safe hold.",
        ),
        CheckResult(
            name="p4_vio_lost_emergency",
            passed=(
                denied_lost["effective_vio_state"] == "lost"
                and denied_lost["mission_state"] == "MISSION_ABORT"
            ),
            detail="Denied + lost-tracking VIO pipeline must force abort path.",
        ),
        CheckResult(
            name="p4_conflict_score_dominates",
            passed=(
                conflict_score["vio_metrics"]["vio_state"] == "lost"
                and conflict_score["vio_state"] == "good"
                and conflict_score["effective_vio_state"] == "lost"
            ),
            detail="Conflict case with reported good state and lost pipeline score must resolve to lost.",
        ),
        CheckResult(
            name="p4_conflict_state_dominates",
            passed=(
                conflict_state["vio_metrics"]["vio_state"] == "good"
                and conflict_state["vio_state"] == "lost"
                and conflict_state["effective_vio_state"] == "lost"
            ),
            detail="Conflict case with lost reported state must preserve lost effective state.",
        ),
        CheckResult(
            name="vio_metrics_source_pipeline_v1",
            passed=all(
                reports[scenario_id]["vio_metrics_source"] == "pipeline_v1"
                for scenario_id in EXPECTED_SCENARIO_IDS
            ),
            detail="All regression artifacts must record pipeline_v1 VIO metrics.",
        ),
        CheckResult(
            name="p6_fusion_gnss_primary",
            passed=fusion_primary["localization_mode"] == "GNSS_PRIMARY",
            detail="Nominal GNSS + good VIO must produce GNSS_PRIMARY localization mode.",
        ),
        CheckResult(
            name="p6_fusion_degraded_blended",
            passed=fusion_blended["localization_mode"] == "BLENDED",
            detail="Degraded GNSS + good VIO must produce BLENDED localization mode.",
        ),
        CheckResult(
            name="p6_fusion_denied_vio_primary",
            passed=fusion_vio_primary["localization_mode"] == "VIO_PRIMARY",
            detail="Denied GNSS + good VIO must produce VIO_PRIMARY localization mode.",
        ),
        CheckResult(
            name="p6_fusion_hold_last_safe",
            passed=fusion_hold_last_safe["localization_mode"] == "HOLD_LAST_SAFE",
            detail="Denied GNSS + lost VIO must produce HOLD_LAST_SAFE localization mode.",
        ),
        CheckResult(
            name="p6_fusion_confidence_ordering",
            passed=(
                fusion_primary["localization_confidence"]
                > fusion_blended["localization_confidence"]
                > fusion_hold_last_safe["localization_confidence"]
            ),
            detail="Localization confidence must decrease: GNSS_PRIMARY > BLENDED > HOLD_LAST_SAFE.",
        ),
        CheckResult(
            name="p6_fusion_fields_present",
            passed=all(
                "localization_mode" in reports[sid]
                and "localization_confidence" in reports[sid]
                and "gnss_weight" in reports[sid]
                and "vio_weight" in reports[sid]
                for sid in EXPECTED_SCENARIO_IDS
            ),
            detail="All reports must include fusion fields: localization_mode, localization_confidence, gnss_weight, vio_weight.",
        ),
        CheckResult(
            name="vio_trust_ordering",
            passed=(
                denied_good["vio_trust"]
                > denied_weak["vio_trust"]
                > denied_lost["vio_trust"]
            ),
            detail="VIO trust must decrease across good > weak > lost scenarios.",
        ),
        CheckResult(
            name="mission_confidence_ordering",
            passed=(
                nominal["mission_confidence"]
                > degraded["mission_confidence"]
                > denied_good["mission_confidence"]
                > denied_lost["mission_confidence"]
            ),
            detail="Mission confidence must monotonically degrade across nominal > degraded > denied-good > denied-lost.",
        ),
        CheckResult(
            name="sync_quality_response",
            passed=(
                sync_low_nominal["sync_quality"] < nominal["sync_quality"]
                and sync_low_denied_good["trust_primary_reason_code"]
                == "sync_quality_low"
            ),
            detail="Low-sync scenarios must surface reduced sync_quality and sync_quality_low reasoning.",
        ),
        CheckResult(
            name="reason_code_coverage",
            passed=all(
                report["trust_primary_reason_code"]
                and report["trust_primary_reason_code"].lower()
                == report["trust_primary_reason_code"]
                and report["mission_primary_reason_code"]
                and report["mission_primary_reason_code"].lower()
                == report["mission_primary_reason_code"]
                and all(code.lower() == code for code in report["trust_reason_codes"])
                and all(code.lower() == code for code in report["mission_reason_codes"])
                for report in reports.values()
            ),
            detail="Trust and mission reason codes must be present and snake_case across all reports.",
        ),
        CheckResult(
            name="no_legacy_enum_values",
            passed=all(
                report["mission_state"] not in legacy_mission_states
                and report["localization_mode"] not in legacy_localization_modes
                for report in reports.values()
            ),
            detail="Reports must not contain legacy mission-state or localization-mode values.",
        ),
        CheckResult(
            name="mission_recovery_dwell_respected",
            passed=(
                recovery_dwell["mission_state"] == "MISSION_EXECUTE"
                and _audit_has_reason(audits.get("s16_recovery_dwell_delays_resume"), "mission_recovery_dwell_active")
                and _audit_has_deferred_recovery(audits.get("s16_recovery_dwell_delays_resume"))
            ),
            detail="Recovery from a degraded state must honor recovery_dwell_ticks before resuming safer mission states.",
        ),
        CheckResult(
            name="mission_safe_hold_timeout_abort",
            passed=(
                safe_hold_timeout["mission_state"] == "MISSION_ABORT"
                and _audit_has_reason(audits.get("s15_safe_hold_timeout_abort"), "mission_abort_safe_hold_timeout")
            ),
            detail="Persistent safe hold must escalate to mission abort after the configured timeout.",
        ),
        CheckResult(
            name="mission_oscillation_detection",
            passed=(
                oscillation["mission_state"] == "MISSION_SAFE_HOLD"
                and _audit_has_reason(audits.get("s17_state_oscillation_safe_hold"), "mission_state_oscillation_detected")
            ),
            detail="State flapping beyond the sliding-window threshold must force MISSION_SAFE_HOLD.",
        ),
        CheckResult(
            name="mission_abort_terminal",
            passed=(
                abort_terminal["mission_state"] == "MISSION_ABORT"
                and _audit_has_reason(audits.get("s18_abort_terminal"), "mission_abort_terminal_latched")
            ),
            detail="Once mission abort is entered, later ticks must remain terminal within the same scenario run.",
        ),
        CheckResult(
            name="mission_audit_present",
            passed=all(
                scenario_id in audits
                and bool(reports[scenario_id]["mission_audit_path"])
                and _audit_matches_report(audits[scenario_id], reports[scenario_id])
                for scenario_id in EXPECTED_SCENARIO_IDS
            ),
            detail="Every scenario must emit a mission audit artifact aligned with the final report state.",
        ),
        CheckResult(
            name="ew_map_artifact_present",
            passed=all(
                scenario_id in ew_maps
                and bool(reports[scenario_id]["ew_risk_map_path"])
                and _ew_map_matches_report(ew_maps[scenario_id], reports[scenario_id])
                for scenario_id in EXPECTED_SCENARIO_IDS
            ),
            detail="Every scenario must emit an EW risk-map artifact aligned with the final report values.",
        ),
        CheckResult(
            name="ew_nominal_false_marking_ceiling",
            passed=(
                nominal["ew_max_risk"] < risk_low_floor
                and nominal["ew_affected_cell_count"] == 0
            ),
            detail="Nominal scenario must remain below the configured EW false-marking floor.",
        ),
        CheckResult(
            name="ew_corridor_cost_ordering",
            passed=(
                nominal["ew_corridor_cost"]
                < degraded["ew_corridor_cost"]
                < denied["ew_corridor_cost"]
            ),
            detail="EW corridor cost must increase from nominal to degraded to denied scenarios.",
        ),
        CheckResult(
            name="ew_denial_hotspot_localized",
            passed=(
                ew_hotspot["ew_primary_reason_code"] == "ew_gnss_denial_hotspot"
                and ew_hotspot["ew_max_risk"] >= risk_medium_floor
                and 0
                < ew_hotspot["ew_affected_cell_count"]
                < _half_grid_area(ew_maps.get("s19_ew_mid_route_denial_hotspot"))
            ),
            detail="Mid-route denial scenario must produce a high-risk but localized EW hotspot.",
        ),
        CheckResult(
            name="ew_temporal_decay_observed",
            passed=(
                ew_decay["ew_max_risk"] < ew_hotspot["ew_max_risk"]
                and ew_decay["ew_corridor_cost"] < ew_hotspot["ew_corridor_cost"]
                and ew_decay["ew_affected_cell_count"] <= ew_hotspot["ew_affected_cell_count"]
            ),
            detail="Recovery scenario must show EW risk decay after the denial interval ends.",
        ),
        CheckResult(
            name="ew_reason_code_coverage",
            passed=all(
                report["ew_primary_reason_code"]
                and report["ew_primary_reason_code"].lower()
                == report["ew_primary_reason_code"]
                and all(code.lower() == code for code in report["ew_reason_codes"])
                and scenario_id in ew_maps
                and ew_maps[scenario_id]["primary_reason_code"].lower()
                == ew_maps[scenario_id]["primary_reason_code"]
                and all(
                    code.lower() == code
                    for code in ew_maps[scenario_id]["reason_codes"]
                )
                and all(
                    code.lower() == code
                    for code in ew_maps[scenario_id]["evidence_codes"]
                )
                for scenario_id, report in reports.items()
            ),
            detail="EW report, reason, and evidence codes must be present and snake_case across all scenarios.",
        ),
        CheckResult(
            name="tactical_summary_artifact_present",
            passed=all(
                scenario_id in tactical
                and bool(reports[scenario_id]["tactical_summary_path"])
                and _tactical_summary_matches_report(
                    tactical[scenario_id], reports[scenario_id]
                )
                for scenario_id in EXPECTED_SCENARIO_IDS
            ),
            detail="Every scenario must emit a tactical summary artifact aligned with the final report values.",
        ),
        CheckResult(
            name="tactical_summary_runtime_consistency",
            passed=all(
                scenario_id in tactical
                and tactical[scenario_id]["mission_state"] == reports[scenario_id]["mission_state"]
                and tactical[scenario_id]["localization_mode"] == reports[scenario_id]["localization_mode"]
                and tactical[scenario_id]["ew_risk_level"] == reports[scenario_id]["ew_risk_level"]
                and tactical[scenario_id]["affected_area_count"] == reports[scenario_id]["ew_affected_cell_count"]
                and round(float(tactical[scenario_id]["ew_corridor_cost"]), 3)
                == round(float(reports[scenario_id]["ew_corridor_cost"]), 3)
                for scenario_id in EXPECTED_SCENARIO_IDS
            ),
            detail="Tactical summary artifacts must stay consistent with report mission and EW fields.",
        ),
        CheckResult(
            name="tactical_advisory_coverage",
            passed=(
                reports["s1_nominal"]["tactical_advisory_code"] == "operator_continue_nominal"
                and reports["s2_gnss_degraded_corridor"]["tactical_advisory_code"] == "operator_continue_with_caution"
                and reports["s3_gnss_denied_zone"]["tactical_advisory_code"] == "operator_avoid_high_risk_corridor"
                and reports["s5_denied_vio_weak"]["tactical_advisory_code"] == "operator_hold_position_and_investigate"
                and reports["s6_denied_vio_lost"]["tactical_advisory_code"] == "operator_abort_and_retask"
                and reports["s13_sync_low_nominal"]["tactical_advisory_code"] == "operator_continue_with_caution"
                and reports["s19_ew_mid_route_denial_hotspot"]["tactical_advisory_code"] == "operator_avoid_high_risk_corridor"
                and all(report["tactical_advisory_text"] for report in reports.values())
            ),
            detail="Key baseline scenarios must map to the expected operator advisory codes and texts.",
        ),
        CheckResult(
            name="tactical_text_determinism",
            passed=all(
                scenario_id in tactical
                and _tactical_text_is_deterministic(tactical[scenario_id])
                for scenario_id in EXPECTED_SCENARIO_IDS
            ),
            detail="Tactical summary text must remain deterministic and constrained to the fixed two-sentence template.",
        ),
        CheckResult(
            name="no_legacy_tactical_reason_codes",
            passed=all(
                report["tactical_primary_reason_code"]
                and report["tactical_primary_reason_code"].lower()
                == report["tactical_primary_reason_code"]
                and report["tactical_advisory_code"]
                and report["tactical_advisory_code"].lower()
                == report["tactical_advisory_code"]
                and all(code.lower() == code for code in report["tactical_reason_codes"])
                for report in reports.values()
            ),
            detail="Tactical reason and advisory codes must be present and snake_case across all scenarios.",
        ),
    ]

    overall_passed = all(check.passed for check in checks)

    return {
        "run_id": run_id,
        "scenario_ids": EXPECTED_SCENARIO_IDS,
        "checks": [asdict(check) for check in checks],
        "overall_result": "PASS" if overall_passed else "FAIL",
    }


def write_regression_result(output_path: str | Path, result: dict[str, Any]) -> Path:
    target_path = Path(output_path)
    target_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return target_path


def _audit_has_reason(audit: dict[str, Any] | None, reason_code: str) -> bool:
    if not audit:
        return False
    return any(
        entry["primary_reason_code"] == reason_code for entry in audit.get("entries", [])
    )


def _audit_has_deferred_recovery(audit: dict[str, Any] | None) -> bool:
    if not audit:
        return False
    return any(
        entry["primary_reason_code"] == "mission_recovery_dwell_active"
        and entry["candidate_state"] != entry["final_state"]
        for entry in audit.get("entries", [])
    )


def _audit_matches_report(audit: dict[str, Any], report: dict[str, Any]) -> bool:
    if audit.get("scenario_id") != report["scenario_id"]:
        return False
    entries = audit.get("entries", [])
    if not entries:
        return False
    final_entry = entries[-1]
    return (
        final_entry["final_state"] == report["mission_state"]
        and final_entry["primary_reason_code"] == report["mission_primary_reason_code"]
        and final_entry["transition_count"] == report["mission_transition_count"]
    )


def _ew_map_matches_report(ew_map: dict[str, Any], report: dict[str, Any]) -> bool:
    if ew_map.get("scenario_id") != report["scenario_id"]:
        return False
    return (
        ew_map["primary_reason_code"] == report["ew_primary_reason_code"]
        and round(float(ew_map["max_risk"]), 3) == round(float(report["ew_max_risk"]), 3)
        and ew_map["affected_cell_count"] == report["ew_affected_cell_count"]
        and round(float(ew_map["corridor_cost"]), 3)
        == round(float(report["ew_corridor_cost"]), 3)
    )


def _half_grid_area(ew_map: dict[str, Any] | None) -> int:
    if not ew_map:
        return 0
    return max(1, (ew_map["width_cells"] * ew_map["height_cells"]) // 2)


def _tactical_summary_matches_report(
    tactical_summary: dict[str, Any],
    report: dict[str, Any],
) -> bool:
    if tactical_summary.get("scenario_id") != report["scenario_id"]:
        return False
    return (
        tactical_summary["mission_state"] == report["mission_state"]
        and round(float(tactical_summary["mission_confidence"]), 3)
        == round(float(report["mission_confidence"]), 3)
        and tactical_summary["localization_mode"] == report["localization_mode"]
        and tactical_summary["ew_risk_level"] == report["ew_risk_level"]
        and tactical_summary["affected_area_count"] == report["ew_affected_cell_count"]
        and round(float(tactical_summary["ew_corridor_cost"]), 3)
        == round(float(report["ew_corridor_cost"]), 3)
        and tactical_summary["primary_reason_code"]
        == report["tactical_primary_reason_code"]
        and tactical_summary["reason_codes"] == report["tactical_reason_codes"]
        and tactical_summary["advisory_code"] == report["tactical_advisory_code"]
        and tactical_summary["advisory_text"] == report["tactical_advisory_text"]
        and tactical_summary["summary_text"] == report["tactical_summary_text"]
    )


def _tactical_text_is_deterministic(tactical_summary: dict[str, Any]) -> bool:
    summary_text = tactical_summary["summary_text"]
    advisory_text = tactical_summary["advisory_text"]
    return (
        isinstance(summary_text, str)
        and summary_text.endswith(".")
        and summary_text.count(".") == 2
        and summary_text.endswith(advisory_text)
        and advisory_text.endswith(".")
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare baseline scenario artifacts.")
    parser.add_argument("run_dir", help="Directory containing scenario report artifacts.")
    parser.add_argument(
        "--output",
        help="Optional path for regression_result.json.",
    )
    parser.add_argument(
        "--config",
        help="Optional path to the simulation config file.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    reports = load_reports(run_dir)
    mission_audits = load_mission_audits(run_dir, reports)
    ew_risk_maps = load_ew_risk_maps(run_dir, reports)
    tactical_summaries = load_tactical_summaries(run_dir, reports)
    config = load_app_config(args.config) if args.config else None
    result = compare_reports(
        reports,
        run_id=run_dir.name,
        mission_audits=mission_audits,
        ew_risk_maps=ew_risk_maps,
        tactical_summaries=tactical_summaries,
        mission_config=config.mission if config else None,
        ew_risk_config=config.ew_risk_map if config else None,
    )

    if args.output:
        write_regression_result(args.output, result)

    print(json.dumps(result, indent=2))
    return 0 if result["overall_result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
