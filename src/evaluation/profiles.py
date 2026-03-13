"""Evaluation profile loading and threshold access."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.config import load_yaml_file


@dataclass(frozen=True)
class EvaluationProfile:
    name: str
    ate_rmse_m_max: float
    rpe_rmse_m_max: float
    drift_pct_max: float
    localization_continuity_pct_min: float
    fallback_reaction_time_s_max: float
    require_mission_success: bool


DEFAULT_EVAL_CONFIG_PATH = (
    Path(__file__).resolve().parents[2] / "configs" / "eval" / "default.yaml"
)


def load_evaluation_profiles(
    path: str | Path = DEFAULT_EVAL_CONFIG_PATH,
) -> dict[str, EvaluationProfile]:
    payload = load_yaml_file(path)
    profiles_payload = payload.get("profiles")
    if not isinstance(profiles_payload, dict) or not profiles_payload:
        raise ValueError("configs/eval profiles must be a non-empty mapping.")
    profiles: dict[str, EvaluationProfile] = {}
    for profile_name, raw_profile in profiles_payload.items():
        if not isinstance(raw_profile, dict):
            raise ValueError(f"evaluation profile {profile_name} must be a mapping.")
        profiles[profile_name] = EvaluationProfile(
            name=profile_name,
            ate_rmse_m_max=_read_float(raw_profile, "ate_rmse_m_max"),
            rpe_rmse_m_max=_read_float(raw_profile, "rpe_rmse_m_max"),
            drift_pct_max=_read_float(raw_profile, "drift_pct_max"),
            localization_continuity_pct_min=_read_float(
                raw_profile, "localization_continuity_pct_min"
            ),
            fallback_reaction_time_s_max=_read_float(
                raw_profile, "fallback_reaction_time_s_max"
            ),
            require_mission_success=_read_bool(
                raw_profile, "require_mission_success"
            ),
        )
    return profiles


def _read_float(payload: dict[str, Any], field_name: str) -> float:
    if field_name not in payload:
        raise ValueError(f"evaluation profile missing required field: {field_name}")
    return float(payload[field_name])


def _read_bool(payload: dict[str, Any], field_name: str) -> bool:
    if field_name not in payload or not isinstance(payload[field_name], bool):
        raise ValueError(f"evaluation profile {field_name} must be a boolean.")
    return payload[field_name]
