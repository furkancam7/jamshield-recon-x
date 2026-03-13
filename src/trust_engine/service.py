"""Trust aggregation service for Phase 7 trust-engine maturity."""

from __future__ import annotations

from dataclasses import dataclass
import re

from common.config import TrustEngineConfig

_SNAKE_CASE_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_DEFICIT_TOLERANCE = 1e-9


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


@dataclass(frozen=True)
class TrustEngineAssessment:
    scenario_id: str
    gnss_trust: float
    gnss_state: str
    vio_trust: float
    sync_quality: float
    localization_confidence: float
    mission_confidence: float
    trust_primary_reason_code: str
    trust_reason_codes: tuple[str, ...]


class TrustEngineService:
    """Aggregates trust signals without assuming mission authority."""

    def __init__(self, config: TrustEngineConfig) -> None:
        self._config = config

    def evaluate(
        self,
        scenario_id: str,
        gnss_trust: float,
        gnss_state: str,
        vio_health_score: float,
        localization_confidence: float,
        mode_stable: bool,
        sync_quality: float | None,
    ) -> TrustEngineAssessment:
        resolved_sync_quality = (
            self._config.default_sync_quality if sync_quality is None else sync_quality
        )
        resolved_sync_quality = round(_clamp(resolved_sync_quality), 3)
        vio_trust = round(_clamp(vio_health_score), 3)
        adjusted_localization_confidence = round(
            _clamp(
                localization_confidence
                - (0.0 if mode_stable else self._config.mode_unstable_penalty)
            ),
            3,
        )

        mission_confidence = round(
            _clamp(
                (gnss_trust * self._config.gnss_trust_weight)
                + (
                    adjusted_localization_confidence
                    * self._config.localization_confidence_weight
                )
                + (vio_trust * self._config.vio_trust_weight)
                + (resolved_sync_quality * self._config.sync_quality_weight)
            ),
            3,
        )

        primary_reason_code, reason_codes = _resolve_reason_codes(
            gnss_trust=gnss_trust,
            gnss_state=gnss_state,
            vio_trust=vio_trust,
            sync_quality=resolved_sync_quality,
            localization_confidence=adjusted_localization_confidence,
            config=self._config,
        )

        return TrustEngineAssessment(
            scenario_id=scenario_id,
            gnss_trust=round(_clamp(gnss_trust), 3),
            gnss_state=gnss_state,
            vio_trust=vio_trust,
            sync_quality=resolved_sync_quality,
            localization_confidence=adjusted_localization_confidence,
            mission_confidence=mission_confidence,
            trust_primary_reason_code=primary_reason_code,
            trust_reason_codes=reason_codes,
        )


def _resolve_reason_codes(
    gnss_trust: float,
    gnss_state: str,
    vio_trust: float,
    sync_quality: float,
    localization_confidence: float,
    config: TrustEngineConfig,
) -> tuple[str, tuple[str, ...]]:
    component_codes = (
        (
            sync_quality,
            config.sync_low_threshold,
            "sync_quality_low",
        ),
        (
            gnss_trust,
            config.gnss_low_threshold,
            "gnss_denial_suspected"
            if gnss_state == "denied"
            else "gnss_measurement_quality_low",
        ),
        (
            vio_trust,
            config.vio_low_threshold,
            "vio_trust_low",
        ),
        (
            localization_confidence,
            config.localization_low_threshold,
            "localization_confidence_low",
        ),
    )

    low_components = [
        (threshold - value, code)
        for value, threshold, code in component_codes
        if value < threshold
    ]
    if not low_components:
        return "trust_inputs_nominal", tuple()

    max_deficit = max(deficit for deficit, _ in low_components)
    primary_reason_code = next(
        code
        for deficit, code in low_components
        if abs(deficit - max_deficit) <= _DEFICIT_TOLERANCE
    )
    reason_codes = tuple(code for _, code in low_components)
    _validate_reason_codes((primary_reason_code, *reason_codes))
    return primary_reason_code, reason_codes


def _validate_reason_codes(reason_codes: tuple[str, ...]) -> None:
    for code in reason_codes:
        if not _SNAKE_CASE_RE.fullmatch(code):
            raise ValueError(f"Reason code must be snake_case: {code!r}")
