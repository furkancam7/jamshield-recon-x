"""Public contracts for the deterministic VIO metric skeleton."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VioFrame:
    timestamp_ns: int
    profile_id: str
    width_px: int
    height_px: int
    pixels: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class VioImuBurst:
    timestamp_ns: int
    profile_id: str
    sample_dt_s: float
    angular_velocity_z_radps: tuple[float, ...]
    linear_acceleration_xy_mps2: tuple[tuple[float, float], ...]


@dataclass(frozen=True)
class VioFeatureSet:
    timestamp_ns: int
    profile_id: str
    features: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True)
class VioMatchSet:
    timestamp_ns: int
    profile_id: str
    matches: tuple[tuple[int, int, int, int], ...]


@dataclass(frozen=True)
class VioPoseDelta:
    timestamp_ns: int
    profile_id: str
    pose_delta_xy_m: float
    yaw_delta_rad: float
    reprojection_error_px: float


@dataclass(frozen=True)
class VioMetricReport:
    timestamp_ns: int
    profile_id: str
    feature_count: int
    matched_feature_count: int
    track_continuity: float
    reprojection_error_px: float
    pose_delta_xy_m: float
    yaw_delta_rad: float
    imu_alignment_error: float
    vio_health_score: float
    vio_state: str
    effective_vio_state: str
    reason_codes: tuple[str, ...]

