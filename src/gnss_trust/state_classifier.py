"""GNSS state classification for the vertical slice."""

from __future__ import annotations

from common.config import TrustConfig


def classify_gnss_state(
    trust_score: float, outage_ratio: float, config: TrustConfig
) -> str:
    if (
        outage_ratio >= config.denied_outage_ratio_threshold
        or trust_score < config.denied_trust_threshold
    ):
        return "denied"
    if trust_score < config.degraded_trust_threshold:
        return "degraded"
    return "nominal"
