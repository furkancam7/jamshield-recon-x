"""Localization fusion contracts and mode definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LocalizationMode(str, Enum):
    """Active localization source mode.

    Modes are ordered by degradation severity:
        GNSS_PRIMARY < BLENDED < VIO_PRIMARY < HOLD_LAST_SAFE
    """

    GNSS_PRIMARY = "GNSS_PRIMARY"
    BLENDED = "BLENDED"
    VIO_PRIMARY = "VIO_PRIMARY"
    HOLD_LAST_SAFE = "HOLD_LAST_SAFE"


LOCALIZATION_MODE_SEVERITY: dict[LocalizationMode, int] = {
    LocalizationMode.GNSS_PRIMARY: 0,
    LocalizationMode.BLENDED: 1,
    LocalizationMode.VIO_PRIMARY: 2,
    LocalizationMode.HOLD_LAST_SAFE: 3,
}


@dataclass(frozen=True)
class FusionAssessment:
    """Output of the localization fusion service."""

    localization_mode: LocalizationMode
    localization_confidence: float  # 0.0-1.0
    gnss_weight: float  # 0.0-1.0
    vio_weight: float  # 0.0-1.0
    mode_stable: bool  # True if mode did not change from previous tick
