"""Simple deterministic GNSS trust heuristics."""

from __future__ import annotations


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def compute_trust_score(measurement_quality: float, outage_ratio: float) -> float:
    quality_term = measurement_quality * 0.80
    availability_term = (1.0 - outage_ratio) * 0.20
    score = quality_term + availability_term
    return round(clamp(score), 3)


def compute_mission_confidence(trust_score: float, vio_healthy: bool) -> float:
    confidence = trust_score * 0.75
    if vio_healthy:
        confidence += 0.25
    return round(clamp(confidence), 3)

