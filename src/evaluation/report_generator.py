"""JSON report generation for observer-side evaluation artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from evaluation.artifact_schema import REPORT_SCHEMA_VERSION, validate_report
from vio.contracts import VioMetricReport
from vio.pipeline import serialize_metric_report


@dataclass(frozen=True)
class EvaluationReport:
    schema_version: str
    run_id: str
    scenario_id: str
    map_name: str
    run_seed: int
    gnss_condition: str
    gnss_state: str
    gnss_trust: float
    vio_trust: float
    sync_quality: float
    mission_confidence: float
    trust_primary_reason_code: str
    trust_reason_codes: tuple[str, ...]
    mission_primary_reason_code: str
    mission_reason_codes: tuple[str, ...]
    mission_transition_count: int
    mission_audit_path: str
    ew_risk_level: str
    ew_primary_reason_code: str
    ew_reason_codes: tuple[str, ...]
    ew_max_risk: float
    ew_affected_cell_count: int
    ew_corridor_cost: float
    ew_risk_map_path: str
    tactical_primary_reason_code: str
    tactical_reason_codes: tuple[str, ...]
    tactical_advisory_code: str
    tactical_advisory_text: str
    tactical_summary_text: str
    tactical_summary_path: str
    runtime_trace_path: str
    truth_trace_path: str
    vio_state: str
    vio_health_score: float
    effective_vio_state: str
    mission_state: str
    ate_m: float
    route_length_m: float
    ground_truth_usage: str
    config_id: str
    manifest_hash: str
    config_hash: str
    evaluation_profile: str
    deterministic_replay_passed: bool
    evaluation_verdict: str
    invalid_run: bool
    evaluation_primary_reason_code: str
    software_revision: str
    timestamp: str
    scenario_metadata: dict[str, str]
    vio_metrics_source: str
    vio_metrics: VioMetricReport
    localization_mode: str
    localization_confidence: float
    gnss_weight: float
    vio_weight: float


def write_report(output_dir: str | Path, report: EvaluationReport) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    payload = asdict(report)
    payload["vio_metrics"] = serialize_metric_report(report.vio_metrics)
    payload["trust_reason_codes"] = list(report.trust_reason_codes)
    payload["mission_reason_codes"] = list(report.mission_reason_codes)
    payload["ew_reason_codes"] = list(report.ew_reason_codes)
    payload["tactical_reason_codes"] = list(report.tactical_reason_codes)
    validate_report(payload)
    report_path = output_path / f"{report.scenario_id}_report.json"
    report_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return report_path
