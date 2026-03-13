"""Deterministic pure-Python VIO metric skeleton."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil, hypot, sqrt
import random

from common.config import VioHealthConfig, VioPipelineConfig, VioTrustConfig
from vio.contracts import (
    VioFeatureSet,
    VioFrame,
    VioImuBurst,
    VioMatchSet,
    VioMetricReport,
    VioPoseDelta,
)
from vio_health.scoring import resolve_effective_vio_state, score_to_state


_PIXEL_TO_METERS = 0.12
_FRAME_WIDTH_PX = 32
_FRAME_HEIGHT_PX = 24
_FRAME_DT_NS = 50_000_000


@dataclass(frozen=True)
class _Profile:
    profile_id: str
    base_feature_count: int
    translation_px: tuple[float, float]
    noise_px: float
    drop_probability: float
    yaw_delta_rad: float
    imu_bias: float
    brightness_low: int
    brightness_high: int


_PROFILES = {
    "nominal_v1": _Profile(
        profile_id="nominal_v1",
        base_feature_count=24,
        translation_px=(2.8, 1.1),
        noise_px=0.05,
        drop_probability=0.02,
        yaw_delta_rad=0.08,
        imu_bias=0.01,
        brightness_low=170,
        brightness_high=255,
    ),
    "weak_texture_v1": _Profile(
        profile_id="weak_texture_v1",
        base_feature_count=12,
        translation_px=(2.1, 0.7),
        noise_px=0.95,
        drop_probability=0.42,
        yaw_delta_rad=0.12,
        imu_bias=0.08,
        brightness_low=120,
        brightness_high=215,
    ),
    "lost_tracking_v1": _Profile(
        profile_id="lost_tracking_v1",
        base_feature_count=6,
        translation_px=(1.7, 0.4),
        noise_px=3.00,
        drop_probability=0.72,
        yaw_delta_rad=0.18,
        imu_bias=0.22,
        brightness_low=95,
        brightness_high=170,
    ),
}


def available_profile_ids() -> tuple[str, ...]:
    return tuple(sorted(_PROFILES))


def run_vio_pipeline(
    run_seed: int,
    profile_id: str,
    pipeline_config: VioPipelineConfig,
    trust_config: VioTrustConfig,
    health_config: VioHealthConfig,
) -> VioMetricReport:
    if profile_id not in _PROFILES:
        available = ", ".join(available_profile_ids())
        raise ValueError(f"Unknown VIO profile_id {profile_id!r}. Expected one of: {available}")

    profile = _PROFILES[profile_id]
    first_frame, second_frame, imu_burst = _generate_inputs(run_seed, profile)
    preprocessed_first = _preprocess_frame(first_frame)
    preprocessed_second = _preprocess_frame(second_frame)
    first_features = _extract_features(preprocessed_first, pipeline_config)
    second_features = _extract_features(preprocessed_second, pipeline_config)
    matches = _match_features(first_features, second_features, pipeline_config)
    pose_delta = _estimate_pose_delta(matches, profile_id)
    imu_prediction = _propagate_imu(imu_burst, pipeline_config)
    return _build_metric_report(
        first_features=first_features,
        matches=matches,
        pose_delta=pose_delta,
        imu_prediction=imu_prediction,
        pipeline_config=pipeline_config,
        trust_config=trust_config,
        health_config=health_config,
    )


def serialize_metric_report(report: VioMetricReport) -> dict[str, object]:
    payload = asdict(report)
    payload["reason_codes"] = list(report.reason_codes)
    return payload


def _generate_inputs(
    run_seed: int,
    profile: _Profile,
) -> tuple[VioFrame, VioFrame, VioImuBurst]:
    rng = random.Random(f"{run_seed}:{profile.profile_id}")
    timestamp_ns = run_seed * 1_000_000
    feature_points = _generate_feature_points(rng, profile)
    translated_points = _translate_points(rng, feature_points, profile)
    first_frame = _render_frame(timestamp_ns, profile, feature_points)
    second_frame = _render_frame(timestamp_ns + _FRAME_DT_NS, profile, translated_points)
    imu_burst = _generate_imu_burst(timestamp_ns + _FRAME_DT_NS, rng, profile)
    return first_frame, second_frame, imu_burst


def _generate_feature_points(
    rng: random.Random,
    profile: _Profile,
) -> tuple[tuple[int, int, int], ...]:
    points: list[tuple[int, int, int]] = []
    columns = max(2, ceil(sqrt(profile.base_feature_count * (_FRAME_WIDTH_PX / _FRAME_HEIGHT_PX))))
    rows = max(2, ceil(profile.base_feature_count / columns))
    usable_width = _FRAME_WIDTH_PX - 6
    usable_height = _FRAME_HEIGHT_PX - 6
    spacing_x = usable_width / max(columns - 1, 1)
    spacing_y = usable_height / max(rows - 1, 1)

    for index in range(profile.base_feature_count):
        row = index // columns
        col = index % columns
        x = int(round(3 + (col * spacing_x) + rng.uniform(-0.6, 0.6)))
        y = int(round(3 + (row * spacing_y) + rng.uniform(-0.6, 0.6)))
        x = min(_FRAME_WIDTH_PX - 3, max(2, x))
        y = min(_FRAME_HEIGHT_PX - 3, max(2, y))
        intensity = rng.randint(profile.brightness_low, profile.brightness_high)
        point = (x, y, intensity)
        if point not in points:
            points.append(point)
    while len(points) < profile.base_feature_count:
        x = rng.randint(2, _FRAME_WIDTH_PX - 3)
        y = rng.randint(2, _FRAME_HEIGHT_PX - 3)
        intensity = rng.randint(profile.brightness_low, profile.brightness_high)
        point = (x, y, intensity)
        if point not in points:
            points.append(point)
    return tuple(points)


def _translate_points(
    rng: random.Random,
    points: tuple[tuple[int, int, int], ...],
    profile: _Profile,
) -> tuple[tuple[int, int, int], ...]:
    translated: list[tuple[int, int, int]] = []
    for x, y, intensity in points:
        if rng.random() < profile.drop_probability:
            continue
        dx = profile.translation_px[0] + rng.uniform(-profile.noise_px, profile.noise_px)
        dy = profile.translation_px[1] + rng.uniform(-profile.noise_px, profile.noise_px)
        target_x = min(_FRAME_WIDTH_PX - 2, max(1, round(x + dx)))
        target_y = min(_FRAME_HEIGHT_PX - 2, max(1, round(y + dy)))
        translated.append((target_x, target_y, intensity))
    return tuple(translated)


def _render_frame(
    timestamp_ns: int,
    profile: _Profile,
    points: tuple[tuple[int, int, int], ...],
) -> VioFrame:
    pixels = [[0 for _ in range(_FRAME_WIDTH_PX)] for _ in range(_FRAME_HEIGHT_PX)]
    for x, y, intensity in points:
        pixels[y][x] = intensity
        pixels[y][x - 1] = max(pixels[y][x - 1], intensity // 4)
        pixels[y][x + 1] = max(pixels[y][x + 1], intensity // 4)
        pixels[y - 1][x] = max(pixels[y - 1][x], intensity // 4)
        pixels[y + 1][x] = max(pixels[y + 1][x], intensity // 4)
    return VioFrame(
        timestamp_ns=timestamp_ns,
        profile_id=profile.profile_id,
        width_px=_FRAME_WIDTH_PX,
        height_px=_FRAME_HEIGHT_PX,
        pixels=tuple(tuple(row) for row in pixels),
    )


def _generate_imu_burst(
    timestamp_ns: int,
    rng: random.Random,
    profile: _Profile,
) -> VioImuBurst:
    samples = 6
    sample_dt_s = (_FRAME_DT_NS / 1_000_000_000) / samples
    angular_velocity = []
    acceleration = []
    target_yaw_rate = profile.yaw_delta_rad / (_FRAME_DT_NS / 1_000_000_000)
    target_accel = hypot(*profile.translation_px) * _PIXEL_TO_METERS / ((_FRAME_DT_NS / 1_000_000_000) ** 2)
    for _ in range(samples):
        angular_velocity.append(
            round(target_yaw_rate + rng.uniform(-profile.imu_bias, profile.imu_bias), 6)
        )
        acceleration.append(
            (
                round(target_accel + rng.uniform(-profile.imu_bias, profile.imu_bias), 6),
                round(target_accel / 2 + rng.uniform(-profile.imu_bias, profile.imu_bias), 6),
            )
        )
    return VioImuBurst(
        timestamp_ns=timestamp_ns,
        profile_id=profile.profile_id,
        sample_dt_s=sample_dt_s,
        angular_velocity_z_radps=tuple(angular_velocity),
        linear_acceleration_xy_mps2=tuple(acceleration),
    )


def _preprocess_frame(frame: VioFrame) -> VioFrame:
    max_value = max(max(row) for row in frame.pixels) or 1
    normalized = tuple(
        tuple(int(round((value / max_value) * 255)) for value in row)
        for row in frame.pixels
    )
    return VioFrame(
        timestamp_ns=frame.timestamp_ns,
        profile_id=frame.profile_id,
        width_px=frame.width_px,
        height_px=frame.height_px,
        pixels=normalized,
    )


def _extract_features(frame: VioFrame, config: VioPipelineConfig) -> VioFeatureSet:
    candidates: list[tuple[int, int, int]] = []
    intensity_threshold = int(round(config.gradient_threshold * 255))
    for y in range(1, frame.height_px - 1):
        for x in range(1, frame.width_px - 1):
            center = frame.pixels[y][x]
            if center < intensity_threshold:
                continue
            if center <= max(
                frame.pixels[y][x - 1],
                frame.pixels[y][x + 1],
                frame.pixels[y - 1][x],
                frame.pixels[y + 1][x],
            ):
                continue
            candidates.append((x, y, center))
    candidates.sort(key=lambda item: (-item[2], item[1], item[0]))
    return VioFeatureSet(
        timestamp_ns=frame.timestamp_ns,
        profile_id=frame.profile_id,
        features=tuple(candidates[: config.max_features]),
    )


def _match_features(
    first_features: VioFeatureSet,
    second_features: VioFeatureSet,
    config: VioPipelineConfig,
) -> VioMatchSet:
    remaining = list(second_features.features)
    matches: list[tuple[int, int, int, int]] = []
    if remaining and first_features.features:
        mean_source_x = sum(feature[0] for feature in first_features.features) / len(first_features.features)
        mean_source_y = sum(feature[1] for feature in first_features.features) / len(first_features.features)
        mean_target_x = sum(feature[0] for feature in remaining) / len(remaining)
        mean_target_y = sum(feature[1] for feature in remaining) / len(remaining)
        guess_dx = mean_target_x - mean_source_x
        guess_dy = mean_target_y - mean_source_y
    else:
        guess_dx = 0.0
        guess_dy = 0.0
    for source_x, source_y, _ in first_features.features:
        best_index = None
        best_distance = None
        for index, (target_x, target_y, _) in enumerate(remaining):
            distance = hypot(target_x - source_x, target_y - source_y)
            if distance > config.match_distance_px:
                continue
            translation_error = hypot(
                (target_x - source_x) - guess_dx,
                (target_y - source_y) - guess_dy,
            )
            candidate_score = translation_error + (distance * 0.1)
            if best_distance is None or candidate_score < best_distance:
                best_distance = candidate_score
                best_index = index
        if best_index is None:
            continue
        target_x, target_y, _ = remaining.pop(best_index)
        matches.append((source_x, source_y, target_x, target_y))
    return VioMatchSet(
        timestamp_ns=second_features.timestamp_ns,
        profile_id=second_features.profile_id,
        matches=tuple(matches),
    )


def _estimate_pose_delta(matches: VioMatchSet, profile_id: str) -> VioPoseDelta:
    if not matches.matches:
        return VioPoseDelta(
            timestamp_ns=matches.timestamp_ns,
            profile_id=profile_id,
            pose_delta_xy_m=0.0,
            yaw_delta_rad=0.0,
            reprojection_error_px=999.0,
        )

    dx_values = [target_x - source_x for source_x, _, target_x, _ in matches.matches]
    dy_values = [target_y - source_y for _, source_y, _, target_y in matches.matches]
    mean_dx = sum(dx_values) / len(dx_values)
    mean_dy = sum(dy_values) / len(dy_values)
    residuals = [
        hypot((target_x - source_x) - mean_dx, (target_y - source_y) - mean_dy)
        for source_x, source_y, target_x, target_y in matches.matches
    ]
    residual_penalty = max(0, 4 - len(matches.matches)) * 0.9
    yaw_delta = (mean_dy / max(abs(mean_dx), 1.0)) * 0.08
    return VioPoseDelta(
        timestamp_ns=matches.timestamp_ns,
        profile_id=profile_id,
        pose_delta_xy_m=round(hypot(mean_dx, mean_dy) * _PIXEL_TO_METERS, 3),
        yaw_delta_rad=round(yaw_delta, 3),
        reprojection_error_px=round((sum(residuals) / len(residuals)) + residual_penalty, 3),
    )


def _propagate_imu(
    imu_burst: VioImuBurst,
    config: VioPipelineConfig,
) -> dict[str, float]:
    total_dt = imu_burst.sample_dt_s * len(imu_burst.angular_velocity_z_radps)
    yaw_delta = sum(imu_burst.angular_velocity_z_radps) * imu_burst.sample_dt_s * config.imu_gain
    accel_sum = sum(hypot(ax, ay) for ax, ay in imu_burst.linear_acceleration_xy_mps2)
    planar_translation = 0.5 * accel_sum * (imu_burst.sample_dt_s ** 2) * config.imu_gain
    return {
        "yaw_delta_rad": round(yaw_delta, 3),
        "planar_translation_m": round(planar_translation, 3),
        "total_dt_s": round(total_dt, 6),
    }


def _build_metric_report(
    first_features: VioFeatureSet,
    matches: VioMatchSet,
    pose_delta: VioPoseDelta,
    imu_prediction: dict[str, float],
    pipeline_config: VioPipelineConfig,
    trust_config: VioTrustConfig,
    health_config: VioHealthConfig,
) -> VioMetricReport:
    feature_count = len(first_features.features)
    matched_feature_count = len(matches.matches)
    denominator = max(1, min(feature_count, pipeline_config.continuity_window))
    track_continuity = round(min(1.0, matched_feature_count / denominator), 3)
    reprojection_error_px = round(
        pose_delta.reprojection_error_px + ((1.0 - track_continuity) * 1.2),
        3,
    )
    imu_alignment_error = round(
        abs(imu_prediction["yaw_delta_rad"] - pose_delta.yaw_delta_rad)
        + abs(imu_prediction["planar_translation_m"] - pose_delta.pose_delta_xy_m),
        3,
    )

    reason_codes: list[str] = []
    if feature_count < trust_config.feature_count_floor:
        reason_codes.append("low_feature_count")
    if track_continuity < trust_config.track_continuity_floor:
        reason_codes.append("track_continuity_drop")
    if reprojection_error_px > trust_config.reprojection_error_ceiling_px:
        reason_codes.append("high_reprojection_error")

    feature_score = _clamp(feature_count / trust_config.feature_count_floor)
    continuity_score = _clamp(track_continuity / trust_config.track_continuity_floor)
    reprojection_score = _clamp(
        1.0 - (reprojection_error_px / trust_config.reprojection_error_ceiling_px)
    )
    imu_score = _clamp(
        1.0 - (imu_alignment_error / trust_config.imu_alignment_ceiling)
    )

    weights = trust_config.metric_weights
    total_weight = (
        weights.feature_count
        + weights.track_continuity
        + weights.reprojection_error
        + weights.imu_alignment
    )
    health_score = round(
        (
            feature_score * weights.feature_count
            + continuity_score * weights.track_continuity
            + reprojection_score * weights.reprojection_error
            + imu_score * weights.imu_alignment
        )
        / total_weight,
        3,
    )
    health_score = round(_clamp(health_score - (0.05 * len(reason_codes))), 3)
    vio_state = score_to_state(health_score, health_config)
    effective_vio_state = resolve_effective_vio_state(
        vio_state=vio_state,
        vio_health_score=health_score,
        config=health_config,
    )

    return VioMetricReport(
        timestamp_ns=pose_delta.timestamp_ns,
        profile_id=first_features.profile_id,
        feature_count=feature_count,
        matched_feature_count=matched_feature_count,
        track_continuity=track_continuity,
        reprojection_error_px=reprojection_error_px,
        pose_delta_xy_m=pose_delta.pose_delta_xy_m,
        yaw_delta_rad=pose_delta.yaw_delta_rad,
        imu_alignment_error=imu_alignment_error,
        vio_health_score=health_score,
        vio_state=vio_state,
        effective_vio_state=effective_vio_state,
        reason_codes=tuple(reason_codes),
    )


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))
