"""Tactical summary artifact serialization."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.artifact_schema import (
    TACTICAL_SUMMARY_SCHEMA_VERSION,
    validate_tactical_summary,
)

from .service import TacticalSummaryAssessment


def write_tactical_summary(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    assessment: TacticalSummaryAssessment,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": TACTICAL_SUMMARY_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "timestamp_ns": assessment.timestamp_ns,
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
    validate_tactical_summary(payload)

    artifact_path = output_path / f"{scenario_id}_tactical_summary.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path
