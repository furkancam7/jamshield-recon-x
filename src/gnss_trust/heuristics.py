"""Simple deterministic GNSS trust heuristics."""

from __future__ import annotations

from common.config import GnssTrustConfig


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def compute_gnss_trust(
    measurement_quality: float, outage_ratio: float, config: GnssTrustConfig
) -> float:
    quality_term = measurement_quality * config.quality_weight
    availability_term = (1.0 - outage_ratio) * config.availability_weight
    score = quality_term + availability_term
    return round(clamp(score), 3)
