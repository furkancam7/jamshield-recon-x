"""Localization fusion service: confidence-weighted GNSS/VIO blending with hysteresis."""

from __future__ import annotations

from common.config import LocalizationFusionConfig
from localization_fusion.contracts import (
    LOCALIZATION_MODE_SEVERITY,
    FusionAssessment,
    LocalizationMode,
)


def compute_source_weights(
    gnss_trust: float,
    vio_health_score: float,
    config: LocalizationFusionConfig,
) -> tuple[float, float]:
    """Compute normalized GNSS/VIO weights from raw confidence scores.

    Each source contributes proportional to its confidence multiplied by
    a configurable base weight.  The pair is then normalized so that
    gnss_weight + vio_weight == 1.0.
    """
    raw_gnss = gnss_trust * config.gnss_base_weight
    raw_vio = vio_health_score * config.vio_base_weight
    total = raw_gnss + raw_vio
    if total <= 0.0:
        return 0.5, 0.5
    return raw_gnss / total, raw_vio / total


def compute_localization_confidence(
    gnss_trust: float,
    vio_health_score: float,
    gnss_weight: float,
    vio_weight: float,
) -> float:
    """Weighted blend of source confidences."""
    confidence = gnss_weight * gnss_trust + vio_weight * vio_health_score
    return max(0.0, min(1.0, confidence))


def select_localization_mode(
    gnss_state: str,
    effective_vio_state: str,
    localization_confidence: float,
    config: LocalizationFusionConfig,
) -> LocalizationMode:
    """Determine localization mode from source states and fused confidence."""
    if gnss_state == "nominal" and localization_confidence >= config.fused_confidence_floor:
        return LocalizationMode.GNSS_PRIMARY

    if gnss_state in ("nominal", "degraded") and effective_vio_state in ("good", "weak"):
        return LocalizationMode.BLENDED

    if gnss_state == "denied" and effective_vio_state == "good":
        return LocalizationMode.VIO_PRIMARY

    if gnss_state == "denied" and effective_vio_state == "weak":
        return LocalizationMode.VIO_PRIMARY

    return LocalizationMode.HOLD_LAST_SAFE


def apply_hysteresis(
    candidate_mode: LocalizationMode,
    previous_mode: LocalizationMode,
    ticks_in_current_mode: int,
    config: LocalizationFusionConfig,
) -> LocalizationMode:
    """Prevent rapid mode oscillation via minimum-dwell hysteresis.

    A mode change is suppressed if the previous mode has not been held for
    at least ``hysteresis_ticks`` consecutive ticks, unless the candidate
    mode is strictly *more severe* (higher severity index) than the
    previous mode.  Upgrades toward safety are never delayed.
    """
    candidate_severity = LOCALIZATION_MODE_SEVERITY[candidate_mode]
    previous_severity = LOCALIZATION_MODE_SEVERITY[previous_mode]

    if candidate_severity > previous_severity:
        return candidate_mode

    if ticks_in_current_mode < config.hysteresis_ticks:
        return previous_mode

    return candidate_mode


class LocalizationFusionService:
    """Stateful fusion service with hysteresis tracking."""

    def __init__(self, config: LocalizationFusionConfig) -> None:
        self._config = config
        self._previous_mode = LocalizationMode.GNSS_PRIMARY
        self._ticks_in_mode: int = 0

    def evaluate(
        self,
        gnss_trust: float,
        gnss_state: str,
        vio_health_score: float,
        effective_vio_state: str,
    ) -> FusionAssessment:
        gnss_weight, vio_weight = compute_source_weights(
            gnss_trust=gnss_trust,
            vio_health_score=vio_health_score,
            config=self._config,
        )
        localization_confidence = compute_localization_confidence(
            gnss_trust=gnss_trust,
            vio_health_score=vio_health_score,
            gnss_weight=gnss_weight,
            vio_weight=vio_weight,
        )
        candidate_mode = select_localization_mode(
            gnss_state=gnss_state,
            effective_vio_state=effective_vio_state,
            localization_confidence=localization_confidence,
            config=self._config,
        )
        final_mode = apply_hysteresis(
            candidate_mode=candidate_mode,
            previous_mode=self._previous_mode,
            ticks_in_current_mode=self._ticks_in_mode,
            config=self._config,
        )

        mode_stable = final_mode == self._previous_mode
        if mode_stable:
            self._ticks_in_mode += 1
        else:
            self._ticks_in_mode = 1
        self._previous_mode = final_mode

        return FusionAssessment(
            localization_mode=final_mode,
            localization_confidence=localization_confidence,
            gnss_weight=gnss_weight,
            vio_weight=vio_weight,
            mode_stable=mode_stable,
        )
