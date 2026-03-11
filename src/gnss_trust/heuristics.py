"""Simple deterministic GNSS trust heuristics."""

from __future__ import annotations

from common.config import TrustConfig


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def compute_trust_score(
    measurement_quality: float, outage_ratio: float, config: TrustConfig
) -> float:
    quality_term = measurement_quality * config.quality_weight
    availability_term = (1.0 - outage_ratio) * config.availability_weight
    score = quality_term + availability_term
    return round(clamp(score), 3)


def compute_mission_confidence(
    trust_score: float, vio_healthy: bool, config: TrustConfig
) -> float:
    confidence = trust_score * config.mission_confidence_weight
    if vio_healthy:
        confidence += config.vio_bonus
    return round(clamp(confidence), 3)
