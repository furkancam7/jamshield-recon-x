"""Service wrapper around deterministic GNSS trust heuristics."""

from __future__ import annotations

from dataclasses import dataclass

from common.config import GnssTrustConfig
from gnss_trust.heuristics import compute_gnss_trust
from gnss_trust.state_classifier import classify_gnss_state
from scenario_orchestrator.orchestrator import GnssConditionSnapshot


@dataclass(frozen=True)
class GnssTrustAssessment:
    scenario_id: str
    gnss_trust: float
    gnss_state: str


class GnssTrustService:
    """Computes GNSS trust outputs for the minimal slice."""

    def __init__(self, config: GnssTrustConfig) -> None:
        self._config = config

    def evaluate(
        self,
        snapshot: GnssConditionSnapshot,
    ) -> GnssTrustAssessment:
        gnss_trust = compute_gnss_trust(
            measurement_quality=snapshot.measurement_quality,
            outage_ratio=snapshot.outage_ratio,
            config=self._config,
        )
        gnss_state = classify_gnss_state(
            trust_score=gnss_trust,
            outage_ratio=snapshot.outage_ratio,
            config=self._config,
        )

        return GnssTrustAssessment(
            scenario_id=snapshot.scenario_id,
            gnss_trust=gnss_trust,
            gnss_state=gnss_state,
        )
