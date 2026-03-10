"""JSON report generation for observer-side evaluation artifacts."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvaluationReport:
    scenario_id: str
    map_name: str
    run_seed: int
    gnss_condition: str
    gnss_state: str
    trust_score: float
    mission_confidence: float
    vio_healthy: bool
    mission_state: str
    ate_m: float
    route_length_m: float
    ground_truth_usage: str


def write_report(output_dir: str | Path, report: EvaluationReport) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_path = output_path / f"{report.scenario_id}_report.json"
    report_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return report_path

