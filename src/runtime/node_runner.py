"""Deterministic node-oriented runtime loop for Phase 12 parity checks."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from common.config import resolve_app_config, serialize_canonical_config
from common.logging import get_logger
from common.runtime_metadata import resolve_software_revision, utc_timestamp
from ew_risk_map import EwRiskMapService, EwRiskTickInput, write_ew_risk_map
from evaluation.artifact_schema import REPORT_SCHEMA_VERSION
from evaluation.mission_audit import write_mission_audit
from evaluation.metrics.ate import compute_ate, reference_estimated_position
from evaluation.report_generator import EvaluationReport, write_report
from health_monitor import (
    HealthMonitorService,
    write_fault_events,
    write_mission_health_timeline,
)
from gnss_trust.trust_service import GnssTrustService
from localization_fusion import LocalizationFusionService
from logging_replay import build_truth_trace_entries, write_runtime_trace, write_truth_trace
from mission_continuity.state_machine import MissionStateMachine
from scenario_orchestrator.manifest_loader import (
    MissionTimelineStep,
    load_manifest,
    serialize_canonical_manifest,
)
from scenario_orchestrator.orchestrator import ScenarioOrchestrator
from tactical_summary import (
    TacticalSummaryInputs,
    TacticalSummaryService,
    write_tactical_summary,
)
from trust_engine import TrustEngineService
from vio import run_vio_pipeline
from vio_health.scoring import resolve_effective_vio_state

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "sim" / "default.yaml"

RUNTIME_TOPIC_FAMILIES = (
    "/sensors/*",
    "/sync/*",
    "/localization/*",
    "/trust/*",
    "/mission/*",
    "/events/*",
    "/tactical/*",
)
FORBIDDEN_RUNTIME_TOPIC_FAMILIES = (
    "/truth/*",
    "/evaluation/*",
)
MISSION_DECISION_AUTHORITY = "mission_continuity_node"


class ScenarioOrchestratorNode:
    """Node wrapper for deterministic scenario snapshots."""

    def __init__(self, orchestrator: ScenarioOrchestrator) -> None:
        self._orchestrator = orchestrator

    def publish_snapshot(self, step: MissionTimelineStep):
        return self._orchestrator.build_snapshot(step)


class VioNode:
    """Node wrapper for the deterministic VIO metric pipeline."""

    def __init__(self, config) -> None:
        self._config = config

    def publish_metrics(self, *, run_seed: int, profile_id: str):
        return run_vio_pipeline(
            run_seed=run_seed,
            profile_id=profile_id,
            pipeline_config=self._config.vio_pipeline,
            trust_config=self._config.vio_trust,
            health_config=self._config.vio_health,
        )


class GnssTrustNode:
    """Node wrapper around GNSS trust service."""

    def __init__(self, config) -> None:
        self._service = GnssTrustService(config.gnss_trust)

    def publish_trust(self, snapshot):
        return self._service.evaluate(snapshot=snapshot)


class FusionNode:
    """Node wrapper around localization fusion service."""

    def __init__(self, config) -> None:
        self._service = LocalizationFusionService(config.localization_fusion)

    def publish_fusion(
        self,
        *,
        gnss_trust: float,
        gnss_state: str,
        vio_health_score: float,
        effective_vio_state: str,
    ):
        return self._service.evaluate(
            gnss_trust=gnss_trust,
            gnss_state=gnss_state,
            vio_health_score=vio_health_score,
            effective_vio_state=effective_vio_state,
        )


class TrustEngineNode:
    """Node wrapper around trust aggregation service."""

    def __init__(self, config) -> None:
        self._service = TrustEngineService(config.trust_engine)

    def publish_trust_decision(
        self,
        *,
        scenario_id: str,
        gnss_trust: float,
        gnss_state: str,
        vio_health_score: float,
        effective_vio_state: str,
        localization_confidence: float,
        mode_stable: bool,
        sync_quality: float,
    ):
        return self._service.evaluate(
            scenario_id=scenario_id,
            gnss_trust=gnss_trust,
            gnss_state=gnss_state,
            vio_health_score=vio_health_score,
            effective_vio_state=effective_vio_state,
            localization_confidence=localization_confidence,
            mode_stable=mode_stable,
            sync_quality=sync_quality,
        )


class MissionContinuityNode:
    """Node wrapper for deterministic mission decision authority."""

    def __init__(self, config) -> None:
        self._state_machine = MissionStateMachine(config=config.mission)

    def publish_mission_decision(
        self,
        *,
        mission_confidence: float,
        gnss_state: str,
        effective_vio_state: str,
    ):
        return self._state_machine.update(
            mission_confidence=mission_confidence,
            gnss_state=gnss_state,
            effective_vio_state=effective_vio_state,
        )


class HealthMonitorNode:
    """Node wrapper for deterministic health/fault publication."""

    def __init__(self, config) -> None:
        self._service = HealthMonitorService(
            sync_low_threshold=config.trust_engine.sync_low_threshold,
            degraded_confidence_threshold=config.mission.degraded_confidence_threshold,
            abort_confidence_threshold=config.mission.emergency_land_confidence_threshold,
        )

    def publish_health(
        self,
        *,
        scenario_id: str,
        tick_index: int,
        timestamp_ns: int,
        sync_quality: float,
        mission_confidence: float,
        gnss_state: str,
        effective_vio_state: str,
        localization_mode: str,
        mission_state: str,
    ):
        return self._service.evaluate(
            scenario_id=scenario_id,
            tick_index=tick_index,
            timestamp_ns=timestamp_ns,
            sync_quality=sync_quality,
            mission_confidence=mission_confidence,
            gnss_state=gnss_state,
            effective_vio_state=effective_vio_state,
            localization_mode=localization_mode,
            mission_state=mission_state,
        )


def validate_runtime_boundaries() -> None:
    runtime_topics = set(RUNTIME_TOPIC_FAMILIES)
    forbidden_topics = set(FORBIDDEN_RUNTIME_TOPIC_FAMILIES)
    overlap = runtime_topics.intersection(forbidden_topics)
    if overlap:
        raise ValueError(
            "Runtime topic boundary violation: forbidden topics present in runtime set "
            + ", ".join(sorted(overlap))
        )
    if MISSION_DECISION_AUTHORITY != "mission_continuity_node":
        raise ValueError("mission_continuity_node must remain the sole decision authority.")


def run_node_scenario(
    scenario_path: str | Path,
    output_dir: str | Path,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    config_override_path: str | Path | None = None,
    run_id: str | None = None,
    vio_state: str | None = None,
    vio_health_score: float | None = None,
) -> dict[str, object]:
    """Runs a scenario through a node-wrapper execution loop.

    This keeps Phase 11 file artifacts as the parity baseline while introducing
    node-oriented execution boundaries for Phase 12 migration.
    """

    validate_runtime_boundaries()
    logger = get_logger("runtime.node_runner")

    manifest = load_manifest(scenario_path)
    config = resolve_app_config(
        base_path=config_path,
        scenario_override_path=manifest.config_override_path,
        cli_override_path=config_override_path,
    )
    orchestrator = ScenarioOrchestrator(manifest)
    scenario_node = ScenarioOrchestratorNode(orchestrator)
    vio_node = VioNode(config)
    gnss_trust_node = GnssTrustNode(config)
    fusion_node = FusionNode(config)
    trust_engine_node = TrustEngineNode(config)
    mission_node = MissionContinuityNode(config)
    health_monitor_node = HealthMonitorNode(config)

    resolved_run_id = run_id or Path(output_dir).name
    software_revision = resolve_software_revision()
    timeline = manifest.resolved_mission_timeline()
    total_ticks = sum(step.repeats for step in timeline.steps)
    manifest_hash = sha256(
        serialize_canonical_manifest(scenario_path).encode("utf-8")
    ).hexdigest()
    config_hash = sha256(
        serialize_canonical_config(
            base_path=config_path,
            scenario_override_path=manifest.config_override_path,
            cli_override_path=config_override_path,
        ).encode("utf-8")
    ).hexdigest()

    audit_entries: list[dict[str, object]] = []
    ew_tick_inputs: list[EwRiskTickInput] = []
    runtime_trace_entries: list[dict[str, object]] = []
    mission_health_entries: list[dict[str, object]] = []
    fault_event_entries: list[dict[str, object]] = []
    truth_trace_entries = build_truth_trace_entries(
        manifest,
        total_ticks=total_ticks,
        tick_period_s=timeline.tick_period_s,
    )

    snapshot = None
    gnss_assessment = None
    fusion_assessment = None
    trust_assessment = None
    mission_decision = None
    vio_metrics = None
    resolved_vio_state = None
    resolved_vio_health_score = None
    effective_vio_state = None
    health_assessment = None

    logger.info(
        "Node runtime inputs scenario_id=%s ticks=%s output_dir=%s config_id=%s",
        manifest.scenario_id,
        total_ticks,
        output_dir,
        config.config_id,
    )

    for step in timeline.steps:
        for _ in range(step.repeats):
            snapshot = scenario_node.publish_snapshot(step)
            vio_metrics = vio_node.publish_metrics(
                run_seed=manifest.run_seed,
                profile_id=step.vio_profile_id,
            )
            resolved_vio_state = (
                vio_state
                or step.vio_reported_state_override
                or vio_metrics.vio_state
            )
            resolved_vio_health_score = (
                vio_health_score
                if vio_health_score is not None
                else (
                    step.vio_health_score_override
                    if step.vio_health_score_override is not None
                    else vio_metrics.vio_health_score
                )
            )
            effective_vio_state = resolve_effective_vio_state(
                vio_state=resolved_vio_state,
                vio_health_score=resolved_vio_health_score,
                config=config.vio_health,
            )
            gnss_assessment = gnss_trust_node.publish_trust(snapshot)
            fusion_assessment = fusion_node.publish_fusion(
                gnss_trust=gnss_assessment.gnss_trust,
                gnss_state=gnss_assessment.gnss_state,
                vio_health_score=resolved_vio_health_score,
                effective_vio_state=effective_vio_state,
            )
            trust_assessment = trust_engine_node.publish_trust_decision(
                scenario_id=manifest.scenario_id,
                gnss_trust=gnss_assessment.gnss_trust,
                gnss_state=gnss_assessment.gnss_state,
                vio_health_score=resolved_vio_health_score,
                effective_vio_state=effective_vio_state,
                localization_confidence=fusion_assessment.localization_confidence,
                mode_stable=fusion_assessment.mode_stable,
                sync_quality=snapshot.sync_quality,
            )
            mission_decision = mission_node.publish_mission_decision(
                mission_confidence=trust_assessment.mission_confidence,
                gnss_state=gnss_assessment.gnss_state,
                effective_vio_state=effective_vio_state,
            )
            truth_entry = truth_trace_entries[mission_decision.tick_index]
            health_assessment = health_monitor_node.publish_health(
                scenario_id=manifest.scenario_id,
                tick_index=mission_decision.tick_index,
                timestamp_ns=int(truth_entry["timestamp_ns"]),
                sync_quality=trust_assessment.sync_quality,
                mission_confidence=trust_assessment.mission_confidence,
                gnss_state=gnss_assessment.gnss_state,
                effective_vio_state=effective_vio_state,
                localization_mode=fusion_assessment.localization_mode.value,
                mission_state=mission_decision.final_state.value,
            )
            mission_health_entries.append(
                {
                    "tick_index": health_assessment.health_status.tick_index,
                    "timestamp_ns": health_assessment.health_status.timestamp_ns,
                    "subsystem": health_assessment.health_status.subsystem,
                    "severity": health_assessment.health_status.severity,
                    "stale_duration_ms": health_assessment.health_status.stale_duration_ms,
                    "primary_reason_code": health_assessment.health_status.primary_reason_code,
                    "reason_codes": list(health_assessment.health_status.reason_codes),
                }
            )
            if health_assessment.fault_event is not None:
                fault_event_entries.append(
                    {
                        "timestamp_ns": health_assessment.fault_event.timestamp_ns,
                        "event_id": health_assessment.fault_event.event_id,
                        "subsystem": health_assessment.fault_event.subsystem,
                        "severity": health_assessment.fault_event.severity,
                        "primary_reason_code": health_assessment.fault_event.primary_reason_code,
                        "reason_codes": list(health_assessment.fault_event.reason_codes),
                        "details": health_assessment.fault_event.details,
                    }
                )
            estimated_position = _estimated_position_from_truth(
                truth_entry["position_m"],
                gnss_assessment.gnss_state,
            )
            audit_entries.append(
                {
                    "tick_index": mission_decision.tick_index,
                    "step_inputs": _serialize_step_inputs(step),
                    "gnss_state": gnss_assessment.gnss_state,
                    "mission_confidence": trust_assessment.mission_confidence,
                    "effective_vio_state": effective_vio_state,
                    "trust_primary_reason_code": trust_assessment.trust_primary_reason_code,
                    "candidate_state": mission_decision.candidate_state.value,
                    "final_state": mission_decision.final_state.value,
                    "primary_reason_code": mission_decision.primary_reason_code,
                    "reason_codes": list(mission_decision.reason_codes),
                    "transition_count": mission_decision.transition_count,
                }
            )
            ew_tick_inputs.append(
                EwRiskTickInput(
                    tick_index=mission_decision.tick_index,
                    gnss_state=gnss_assessment.gnss_state,
                    sync_quality=trust_assessment.sync_quality,
                    localization_mode=fusion_assessment.localization_mode.value,
                    localization_confidence=fusion_assessment.localization_confidence,
                    trust_primary_reason_code=trust_assessment.trust_primary_reason_code,
                    trust_reason_codes=trust_assessment.trust_reason_codes,
                )
            )
            runtime_trace_entries.append(
                {
                    "tick_index": mission_decision.tick_index,
                    "timestamp_ns": truth_entry["timestamp_ns"],
                    "step_inputs": _serialize_step_inputs(step),
                    "gnss_state": gnss_assessment.gnss_state,
                    "gnss_trust": gnss_assessment.gnss_trust,
                    "vio_trust": trust_assessment.vio_trust,
                    "effective_vio_state": effective_vio_state,
                    "sync_quality": trust_assessment.sync_quality,
                    "localization_mode": fusion_assessment.localization_mode.value,
                    "localization_confidence": fusion_assessment.localization_confidence,
                    "mission_confidence": trust_assessment.mission_confidence,
                    "trust_primary_reason_code": trust_assessment.trust_primary_reason_code,
                    "mission_state": mission_decision.final_state.value,
                    "mission_primary_reason_code": mission_decision.primary_reason_code,
                    "estimated_position_m": estimated_position,
                    "route_progress_pct": truth_entry["route_progress_pct"],
                }
            )

    if (
        snapshot is None
        or gnss_assessment is None
        or fusion_assessment is None
        or trust_assessment is None
        or mission_decision is None
        or vio_metrics is None
        or resolved_vio_state is None
        or resolved_vio_health_score is None
        or effective_vio_state is None
        or health_assessment is None
    ):
        raise RuntimeError("Scenario timeline produced no executable ticks.")

    final_truth_position = truth_trace_entries[-1]["position_m"]
    final_estimated_position = runtime_trace_entries[-1]["estimated_position_m"]
    ate_m = compute_ate(
        (
            final_estimated_position["x"],
            final_estimated_position["y"],
            final_estimated_position["z"],
        ),
        (
            final_truth_position["x"],
            final_truth_position["y"],
            final_truth_position["z"],
        ),
    )
    mission_audit_path = write_mission_audit(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        entries=audit_entries,
    )
    runtime_trace_path = write_runtime_trace(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        entries=runtime_trace_entries,
    )
    truth_trace_path = write_truth_trace(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        entries=truth_trace_entries,
    )
    mission_health_path = write_mission_health_timeline(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        entries=mission_health_entries,
    )
    fault_events_path = write_fault_events(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        events=fault_event_entries,
    )
    ew_risk_assessment = EwRiskMapService(config.ew_risk_map).evaluate(
        manifest=manifest,
        tick_period_s=timeline.tick_period_s,
        tick_inputs=ew_tick_inputs,
    )
    ew_risk_map_path = write_ew_risk_map(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        assessment=ew_risk_assessment,
    )
    tactical_summary_assessment = TacticalSummaryService().evaluate(
        TacticalSummaryInputs(
            timestamp_ns=ew_risk_assessment.timestamp_ns,
            mission_state=mission_decision.final_state.value,
            mission_primary_reason_code=mission_decision.primary_reason_code,
            mission_confidence=trust_assessment.mission_confidence,
            localization_mode=fusion_assessment.localization_mode.value,
            effective_vio_state=effective_vio_state,
            trust_primary_reason_code=trust_assessment.trust_primary_reason_code,
            ew_risk_level=ew_risk_assessment.risk_level,
            ew_primary_reason_code=ew_risk_assessment.primary_reason_code,
            ew_corridor_cost=ew_risk_assessment.corridor_cost,
            ew_affected_cell_count=ew_risk_assessment.affected_cell_count,
        )
    )
    tactical_summary_path = write_tactical_summary(
        output_dir,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        assessment=tactical_summary_assessment,
    )
    report = EvaluationReport(
        schema_version=REPORT_SCHEMA_VERSION,
        run_id=resolved_run_id,
        scenario_id=manifest.scenario_id,
        map_name=manifest.map_name,
        run_seed=manifest.run_seed,
        gnss_condition=snapshot.gnss_condition,
        gnss_state=gnss_assessment.gnss_state,
        gnss_trust=gnss_assessment.gnss_trust,
        vio_trust=trust_assessment.vio_trust,
        sync_quality=trust_assessment.sync_quality,
        mission_confidence=trust_assessment.mission_confidence,
        trust_primary_reason_code=trust_assessment.trust_primary_reason_code,
        trust_reason_codes=trust_assessment.trust_reason_codes,
        mission_primary_reason_code=mission_decision.primary_reason_code,
        mission_reason_codes=mission_decision.reason_codes,
        mission_transition_count=mission_decision.transition_count,
        mission_audit_path=str(mission_audit_path),
        ew_risk_level=ew_risk_assessment.risk_level,
        ew_primary_reason_code=ew_risk_assessment.primary_reason_code,
        ew_reason_codes=ew_risk_assessment.reason_codes,
        ew_max_risk=ew_risk_assessment.max_risk,
        ew_affected_cell_count=ew_risk_assessment.affected_cell_count,
        ew_corridor_cost=ew_risk_assessment.corridor_cost,
        ew_risk_map_path=str(ew_risk_map_path),
        tactical_primary_reason_code=tactical_summary_assessment.primary_reason_code,
        tactical_reason_codes=tactical_summary_assessment.reason_codes,
        tactical_advisory_code=tactical_summary_assessment.advisory_code,
        tactical_advisory_text=tactical_summary_assessment.advisory_text,
        tactical_summary_text=tactical_summary_assessment.summary_text,
        tactical_summary_path=str(tactical_summary_path),
        runtime_trace_path=str(runtime_trace_path),
        truth_trace_path=str(truth_trace_path),
        vio_state=resolved_vio_state,
        vio_health_score=resolved_vio_health_score,
        effective_vio_state=effective_vio_state,
        mission_state=mission_decision.final_state.value,
        ate_m=ate_m,
        route_length_m=snapshot.route_length_m,
        ground_truth_usage="evaluation_only",
        config_id=config.config_id,
        manifest_hash=manifest_hash,
        config_hash=config_hash,
        evaluation_profile=manifest.evaluation_profile,
        deterministic_replay_passed=False,
        evaluation_verdict="PENDING",
        invalid_run=False,
        evaluation_primary_reason_code="evaluation_pending",
        software_revision=software_revision,
        timestamp=utc_timestamp(),
        scenario_metadata=manifest.metadata,
        vio_metrics_source="pipeline_v1",
        vio_metrics=vio_metrics,
        localization_mode=fusion_assessment.localization_mode.value,
        localization_confidence=fusion_assessment.localization_confidence,
        gnss_weight=fusion_assessment.gnss_weight,
        vio_weight=fusion_assessment.vio_weight,
    )
    report_path = write_report(output_dir, report)

    summary = {
        "scenario_id": manifest.scenario_id,
        "run_id": resolved_run_id,
        "config_id": config.config_id,
        "manifest_hash": manifest_hash,
        "config_hash": config_hash,
        "evaluation_profile": manifest.evaluation_profile,
        "deterministic_replay_passed": False,
        "evaluation_verdict": "PENDING",
        "invalid_run": False,
        "evaluation_primary_reason_code": "evaluation_pending",
        "software_revision": software_revision,
        "gnss_state": gnss_assessment.gnss_state,
        "gnss_trust": gnss_assessment.gnss_trust,
        "vio_trust": trust_assessment.vio_trust,
        "sync_quality": trust_assessment.sync_quality,
        "mission_confidence": trust_assessment.mission_confidence,
        "trust_primary_reason_code": trust_assessment.trust_primary_reason_code,
        "mission_primary_reason_code": mission_decision.primary_reason_code,
        "mission_transition_count": mission_decision.transition_count,
        "ew_risk_level": ew_risk_assessment.risk_level,
        "ew_primary_reason_code": ew_risk_assessment.primary_reason_code,
        "ew_max_risk": ew_risk_assessment.max_risk,
        "ew_affected_cell_count": ew_risk_assessment.affected_cell_count,
        "ew_corridor_cost": ew_risk_assessment.corridor_cost,
        "ew_risk_map_path": str(ew_risk_map_path),
        "tactical_primary_reason_code": tactical_summary_assessment.primary_reason_code,
        "tactical_advisory_code": tactical_summary_assessment.advisory_code,
        "tactical_summary_text": tactical_summary_assessment.summary_text,
        "tactical_summary_path": str(tactical_summary_path),
        "effective_vio_state": effective_vio_state,
        "vio_profile_id": snapshot.vio_profile_id,
        "mission_state": mission_decision.final_state.value,
        "localization_mode": fusion_assessment.localization_mode.value,
        "localization_confidence": fusion_assessment.localization_confidence,
        "mission_audit_path": str(mission_audit_path),
        "runtime_trace_path": str(runtime_trace_path),
        "truth_trace_path": str(truth_trace_path),
        "mission_health_path": str(mission_health_path),
        "fault_events_path": str(fault_events_path),
        "report_path": str(report_path),
    }
    logger.info(
        "Node runtime outputs scenario_id=%s mission_state=%s mode=%s trust_reason=%s",
        manifest.scenario_id,
        mission_decision.final_state.value,
        fusion_assessment.localization_mode.value,
        trust_assessment.trust_primary_reason_code,
    )
    return summary


def _serialize_step_inputs(step: MissionTimelineStep) -> dict[str, object]:
    vio_payload: dict[str, object] = {"profile_id": step.vio_profile_id}
    if step.vio_reported_state_override is not None:
        vio_payload["reported_state"] = step.vio_reported_state_override
    if step.vio_health_score_override is not None:
        vio_payload["health_score_override"] = step.vio_health_score_override

    return {
        "gnss_condition": step.gnss_condition,
        "runtime_health": {"sync_quality": step.runtime_sync_quality},
        "vio": vio_payload,
    }


def _estimated_position_from_truth(
    truth_position: dict[str, object],
    gnss_state: str,
) -> dict[str, float]:
    dx, dy, dz = reference_estimated_position(gnss_state)
    return {
        "x": round(float(truth_position["x"]) + dx, 3),
        "y": round(float(truth_position["y"]) + dy, 3),
        "z": round(float(truth_position["z"]) + dz, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Phase 12 node-oriented scenario flow."
    )
    parser.add_argument("scenario", help="Path to the scenario YAML file.")
    parser.add_argument(
        "--output-dir",
        default="artifacts",
        help="Directory where node-run artifacts will be written.",
    )
    parser.add_argument(
        "--vio-state",
        choices=["good", "weak", "lost"],
        help="Legacy categorical VIO health override.",
    )
    parser.add_argument(
        "--vio-health-score",
        type=float,
        help="Legacy continuous VIO health override (0.0-1.0).",
    )
    parser.add_argument(
        "--vio-unhealthy",
        action="store_true",
        help="(Deprecated) Sets vio_state=lost and vio_health_score=0.0.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the simulation config file.",
    )
    parser.add_argument(
        "--config-override",
        help="Optional CLI override config applied after any scenario override.",
    )
    parser.add_argument(
        "--run-id",
        help="Optional run identifier written into node artifacts.",
    )
    args = parser.parse_args()

    vio_state = args.vio_state
    vio_health_score = args.vio_health_score
    if args.vio_unhealthy:
        vio_state = "lost"
        vio_health_score = 0.0

    summary = run_node_scenario(
        scenario_path=args.scenario,
        output_dir=args.output_dir,
        config_path=args.config,
        config_override_path=args.config_override,
        run_id=args.run_id,
        vio_state=vio_state,
        vio_health_score=vio_health_score,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
