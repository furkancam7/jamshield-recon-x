"""Deterministic VIO health scoring and conflict resolution.

Score-to-state mapping and worst-case conflict resolution per
the Phase 4 public contract (docs/roadmap/phase-04-backlog.md).
"""

from __future__ import annotations

from common.config import VioHealthConfig

VIO_STATES = ("good", "weak", "lost")

_SEVERITY = {"good": 0, "weak": 1, "lost": 2}


def score_to_state(score: float, config: VioHealthConfig) -> str:
    """Map a continuous VIO health score to a categorical state.

    Thresholds (from config):
        score >= good_threshold  => "good"
        score >= weak_threshold  => "weak"
        score <  weak_threshold  => "lost"
    """
    if score >= config.good_threshold:
        return "good"
    if score >= config.weak_threshold:
        return "weak"
    return "lost"


def resolve_effective_vio_state(
    vio_state: str, vio_health_score: float, config: VioHealthConfig
) -> str:
    """Apply worst-case conflict resolution between categorical and numeric VIO inputs.

    effective_vio_state = worse(reported_vio_state, score_bucket(vio_health_score))
    Severity ordering: good < weak < lost
    """
    if vio_state not in _SEVERITY:
        raise ValueError(f"Invalid vio_state: {vio_state!r}; expected one of {VIO_STATES}")

    score_state = score_to_state(vio_health_score, config)
    if _SEVERITY[vio_state] >= _SEVERITY[score_state]:
        return vio_state
    return score_state


def derive_vio_healthy(effective_vio_state: str) -> bool:
    """Derive the deprecated boolean vio_healthy from effective_vio_state."""
    return effective_vio_state != "lost"
