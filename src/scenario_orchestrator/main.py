"""End-to-end entry point for the first working vertical slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.config import load_app_config
from common.logging import get_logger
from common.runtime_metadata import resolve_software_revision, utc_timestamp
from evaluation.artifact_schema import REPORT_SCHEMA_VERSION
from evaluation.metrics.ate import compute_ate, reference_estimated_position
from evaluation.report_generator import EvaluationReport, write_report
from gnss_trust.trust_service import TrustService
from mission_continuity.state_machine import MissionStateMachine
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "sim" / "default.yaml"


def run_scenario(
    scenario_path: str | Path,
    output_dir: str | Path,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    run_id: str | None = None,
    vio_healthy: bool = True,
) -> dict[str, object]:
    logger = get_logger("scenario_orchestrator.main")
    config = load_app_config(config_path)
    manifest = load_manifest(scenario_path)
    snapshot = ScenarioOrchestrator(manifest).build_snapshot()
    resolved_run_id = run_id or Path(output_dir).name
    software_revision = resolve_software_revision()

    logger.info(
        "Resolved inputs scenario_id=%s gnss_condition=%s vio_healthy=%s output_dir=%s config_id=%s",
        manifest.scenario_id,
        manifest.gnss_condition,
        vio_healthy,
        output_dir,
        config.config_id,
    )
    trust_assessment = TrustService(config.trust).evaluate(
        snapshot=snapshot,
        vio_healthy=vio_healthy,
    )
    mission_state = MissionStateMachine(config=config.mission).update(
        mission_confidence=trust_assessment.mission_confidence,
        gnss_state=trust_assessment.gnss_state,
        vio_healthy=trust_assessment.vio_healthy,
    )

    estimated_position = reference_estimated_position(trust_assessment.gnss_state)
    ate_m = compute_ate(estimated_position, (0.0, 0.0, 0.0))
    report = EvaluationReport(
        schema_version=REPORT_SCHEMA_VERSION,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        map_name=manifest.map_name,
        run_seed=manifest.run_seed,
        gnss_condition=manifest.gnss_condition,
        gnss_state=trust_assessment.gnss_state,
        trust_score=trust_assessment.trust_score,
        mission_confidence=trust_assessment.mission_confidence,
        vio_healthy=trust_assessment.vio_healthy,
        vio_state="healthy" if trust_assessment.vio_healthy else "lost",
        mission_state=mission_state.value,
        ate_m=ate_m,
        route_length_m=snapshot.route_length_m,
        ground_truth_usage="evaluation_only",
        config_id=config.config_id,
        software_revision=software_revision,
        timestamp=utc_timestamp(),
        scenario_metadata=manifest.metadata,
    )
    report_path = write_report(output_dir, report)

    summary = {
        "scenario_id": manifest.scenario_id,
        "run_id": resolved_run_id,
        "config_id": config.config_id,
        "software_revision": software_revision,
        "gnss_state": trust_assessment.gnss_state,
        "trust_score": trust_assessment.trust_score,
        "mission_confidence": trust_assessment.mission_confidence,
        "mission_state": mission_state.value,
        "report_path": str(report_path),
    }
    logger.info(
        "Computed outputs scenario_id=%s gnss_state=%s trust_score=%.3f mission_confidence=%.3f mission_state=%s",
        manifest.scenario_id,
        trust_assessment.gnss_state,
        trust_assessment.trust_score,
        trust_assessment.mission_confidence,
        mission_state.value,
    )
    logger.info("Vertical slice completed for scenario %s", manifest.scenario_id)
    return summary


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
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the simulation config file.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run identifier written into the evaluation artifacts.",
    )
    args = parser.parse_args()

    summary = run_scenario(
        scenario_path=args.scenario,
        output_dir=args.output_dir,
        config_path=args.config,
        run_id=args.run_id,
        vio_healthy=not args.vio_unhealthy,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
