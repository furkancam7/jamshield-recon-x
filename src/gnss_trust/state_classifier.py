"""GNSS state classification for the vertical slice."""

from __future__ import annotations


def classify_gnss_state(trust_score: float, outage_ratio: float) -> str:
    if outage_ratio >= 0.80 or trust_score < 0.25:
        return "denied"
    if trust_score < 0.75:
        return "degraded"
    return "nominal"

