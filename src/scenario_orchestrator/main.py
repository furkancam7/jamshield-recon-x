"""End-to-end entry point for the first working vertical slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.logging import get_logger
from evaluation.metrics.ate import compute_ate, reference_estimated_position
from evaluation.report_generator import EvaluationReport, write_report
from gnss_trust.trust_service import TrustService
from mission_continuity.state_machine import MissionStateMachine
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the JamShield Recon-X Sim vertical-slice scenario flow."
    )
    parser.add_argument("scenario", help="Path to the scenario YAML file.")
    parser.add_argument(
        "--output-dir",
        default="artifacts",
        help="Directory where the JSON evaluation report will be written.",
    )
    parser.add_argument(
        "--vio-unhealthy",
        action="store_true",
        help="Force the simplified VIO health input to false.",
    )
    args = parser.parse_args()

    logger = get_logger("scenario_orchestrator.main")

    manifest = load_manifest(args.scenario)
    snapshot = ScenarioOrchestrator(manifest).build_snapshot()
    trust_assessment = TrustService().evaluate(
        snapshot=snapshot,
        vio_healthy=not args.vio_unhealthy,
    )
    mission_state = MissionStateMachine().update(
        mission_confidence=trust_assessment.mission_confidence,
        gnss_state=trust_assessment.gnss_state,
        vio_healthy=trust_assessment.vio_healthy,
    )

    estimated_position = reference_estimated_position(trust_assessment.gnss_state)
    ate_m = compute_ate(estimated_position, (0.0, 0.0, 0.0))

    report = EvaluationReport(
        scenario_id=manifest.scenario_id,
        map_name=manifest.map_name,
        run_seed=manifest.run_seed,
        gnss_condition=manifest.gnss_condition,
        gnss_state=trust_assessment.gnss_state,
        trust_score=trust_assessment.trust_score,
        mission_confidence=trust_assessment.mission_confidence,
        vio_healthy=trust_assessment.vio_healthy,
        mission_state=mission_state.value,
        ate_m=ate_m,
        route_length_m=snapshot.route_length_m,
        ground_truth_usage="evaluation_only",
    )
    report_path = write_report(args.output_dir, report)

    summary = {
        "scenario_id": manifest.scenario_id,
        "gnss_state": trust_assessment.gnss_state,
        "trust_score": trust_assessment.trust_score,
        "mission_confidence": trust_assessment.mission_confidence,
        "mission_state": mission_state.value,
        "report_path": str(report_path),
    }
    logger.info("Vertical slice completed for scenario %s", manifest.scenario_id)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

