"""EW risk-map artifact serialization."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.artifact_schema import EW_RISK_MAP_SCHEMA_VERSION, validate_ew_risk_map

from .service import EwRiskMapAssessment


def write_ew_risk_map(
    output_dir: str | Path,
    *,
    run_id: str,
    scenario_id: str,
    assessment: EwRiskMapAssessment,
) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": EW_RISK_MAP_SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_id": scenario_id,
        "timestamp_ns": assessment.timestamp_ns,
        "frame_id": assessment.frame_id,
        "cell_size_m": assessment.cell_size_m,
        "width_cells": assessment.width_cells,
        "height_cells": assessment.height_cells,
        "origin": {
            "x_m": assessment.origin.x_m,
            "y_m": assessment.origin.y_m,
        },
        "risk_cells": list(assessment.risk_cells),
        "evidence_codes": list(assessment.evidence_codes),
        "primary_reason_code": assessment.primary_reason_code,
        "reason_codes": list(assessment.reason_codes),
        "max_risk": assessment.max_risk,
        "affected_cell_count": assessment.affected_cell_count,
        "corridor_cost": assessment.corridor_cost,
        "risk_cells_hash": assessment.risk_cells_hash,
    }
    validate_ew_risk_map(payload)

    artifact_path = output_path / f"{scenario_id}_ew_risk_map.json"
    artifact_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return artifact_path
