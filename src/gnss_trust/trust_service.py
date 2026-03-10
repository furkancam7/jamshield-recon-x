"""Service wrapper around deterministic GNSS trust heuristics."""

from __future__ import annotations

from dataclasses import dataclass

from gnss_trust.heuristics import compute_mission_confidence, compute_trust_score
from gnss_trust.state_classifier import classify_gnss_state
from scenario_orchestrator.orchestrator import GnssConditionSnapshot


@dataclass(frozen=True)
class TrustAssessment:
    scenario_id: str
    trust_score: float
    gnss_state: str
    mission_confidence: float
    vio_healthy: bool


class TrustService:
    """Computes GNSS trust outputs for the minimal slice."""

    def evaluate(
        self, snapshot: GnssConditionSnapshot, vio_healthy: bool = True
    ) -> TrustAssessment:
        trust_score = compute_trust_score(
            measurement_quality=snapshot.measurement_quality,
            outage_ratio=snapshot.outage_ratio,
        )
        gnss_state = classify_gnss_state(
            trust_score=trust_score,
            outage_ratio=snapshot.outage_ratio,
        )
        mission_confidence = compute_mission_confidence(
            trust_score=trust_score,
            vio_healthy=vio_healthy,
        )

        return TrustAssessment(
            scenario_id=snapshot.scenario_id,
            trust_score=trust_score,
            gnss_state=gnss_state,
            mission_confidence=mission_confidence,
            vio_healthy=vio_healthy,
        )

