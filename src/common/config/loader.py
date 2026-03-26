"""YAML loading helpers and app config loading."""

from __future__ import annotations

from copy import deepcopy
import json
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GnssTrustConfig:
    quality_weight: float
    availability_weight: float
    denied_outage_ratio_threshold: float
    denied_trust_threshold: float
    degraded_trust_threshold: float


@dataclass(frozen=True)
class TrustEngineConfig:
    gnss_trust_weight: float
    localization_confidence_weight: float
    vio_trust_weight: float
    sync_quality_weight: float
    gnss_low_threshold: float
    localization_low_threshold: float
    vio_low_threshold: float
    sync_low_threshold: float
    default_sync_quality: float
    mode_unstable_penalty: float
    effective_vio_weak_penalty: float
    effective_vio_lost_penalty: float
    calibration_high_floor: float
    calibration_medium_floor: float


@dataclass(frozen=True)
class MissionConfig:
    nominal_confidence_threshold: float
    degraded_confidence_threshold: float
    denied_fallback_confidence_threshold: float
    emergency_land_confidence_threshold: float
    denied_allowed_states: tuple[str, ...]
    recovery_dwell_ticks: int
    safe_hold_escalation_ticks: int
    oscillation_window_ticks: int
    max_state_transitions_in_window: int


@dataclass(frozen=True)
class VioHealthConfig:
    good_threshold: float
    weak_threshold: float


@dataclass(frozen=True)
class VioPipelineConfig:
    max_features: int
    gradient_threshold: float
    match_distance_px: float
    continuity_window: int
    imu_gain: float


@dataclass(frozen=True)
class VioMetricWeights:
    feature_count: float
    track_continuity: float
    reprojection_error: float
    imu_alignment: float


@dataclass(frozen=True)
class VioTrustConfig:
    feature_count_floor: int
    track_continuity_floor: float
    reprojection_error_ceiling_px: float
    imu_alignment_ceiling: float
    metric_weights: VioMetricWeights


@dataclass(frozen=True)
class LocalizationFusionConfig:
    gnss_base_weight: float
    vio_base_weight: float
    fused_confidence_floor: float
    hysteresis_ticks: int


@dataclass(frozen=True)
class EwRiskMapConfig:
    cell_size_m: float
    grid_padding_m: float
    stamp_radius_m: float
    global_decay_per_tick: float
    corridor_sample_step_m: float
    corridor_band_half_width_m: float
    risk_low_floor: float
    risk_medium_floor: float
    weight_gnss_denied: float
    weight_gnss_degraded: float
    weight_sync_low: float
    weight_localization_unstable: float


@dataclass(frozen=True)
class AppConfig:
    config_id: str
    schema_version: str
    gnss_trust: GnssTrustConfig
    trust_engine: TrustEngineConfig
    mission: MissionConfig
    vio_health: VioHealthConfig
    vio_pipeline: VioPipelineConfig
    vio_trust: VioTrustConfig
    localization_fusion: LocalizationFusionConfig
    ew_risk_map: EwRiskMapConfig


CANONICAL_CONFIG_EXCLUDED_FIELDS = frozenset({"config_id"})


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load a YAML document from disk.

    PyYAML is used when available. A small indentation-based fallback parser is
    provided so the vertical slice remains runnable with the standard library.
    """

    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore
    except ImportError:
        data = _parse_simple_yaml(text)
    else:
        data = yaml.safe_load(text)

    if not isinstance(data, dict):
        raise ValueError(f"Top-level YAML document must be a mapping: {source_path}")

    return data


def load_app_config(path: str | Path) -> AppConfig:
    return resolve_app_config(path)


def resolve_app_config(
    base_path: str | Path,
    scenario_override_path: str | Path | None = None,
    cli_override_path: str | Path | None = None,
) -> AppConfig:
    payload = resolve_app_config_payload(
        base_path=base_path,
        scenario_override_path=scenario_override_path,
        cli_override_path=cli_override_path,
    )
    return _validate_app_config(payload, Path(base_path))


def serialize_canonical_config(
    base_path: str | Path,
    scenario_override_path: str | Path | None = None,
    cli_override_path: str | Path | None = None,
) -> str:
    payload = resolve_app_config_payload(
        base_path=base_path,
        scenario_override_path=scenario_override_path,
        cli_override_path=cli_override_path,
    )
    return canonicalize_config_payload(payload)


def canonicalize_config_payload(payload: dict[str, Any]) -> str:
    normalized = _normalize_canonical_value(
        _strip_canonical_excluded_fields(payload)
    )
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )


def canonicalize_app_config(config: AppConfig) -> str:
    return canonicalize_config_payload(asdict(config))


def resolve_app_config_payload(
    base_path: str | Path,
    scenario_override_path: str | Path | None = None,
    cli_override_path: str | Path | None = None,
) -> dict[str, Any]:
    payload = load_yaml_file(base_path)
    payload = _apply_config_override(
        payload,
        scenario_override_path,
    )
    payload = _apply_config_override(
        payload,
        cli_override_path,
    )
    return payload


def _validate_app_config(payload: dict[str, Any], source_path: Path) -> AppConfig:
    required_fields = {
        "config_id",
        "schema_version",
        "gnss_trust",
        "trust_engine",
        "mission",
        "vio_health",
        "vio_pipeline",
        "vio_trust",
        "localization_fusion",
        "ew_risk_map",
    }
    missing = required_fields.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(
            f"Config missing required fields in {source_path}: {missing_list}"
        )

    gnss_trust_payload = _require_mapping(payload["gnss_trust"], "gnss_trust")
    trust_engine_payload = _require_mapping(payload["trust_engine"], "trust_engine")
    mission_payload = _require_mapping(payload["mission"], "mission")
    vio_health_payload = _require_mapping(payload["vio_health"], "vio_health")
    vio_pipeline_payload = _require_mapping(payload["vio_pipeline"], "vio_pipeline")
    vio_trust_payload = _require_mapping(payload["vio_trust"], "vio_trust")
    vio_metric_weights_payload = _require_mapping(
        vio_trust_payload["metric_weights"],
        "vio_trust.metric_weights",
    )
    fusion_payload = _require_mapping(
        payload["localization_fusion"], "localization_fusion"
    )
    ew_risk_map_payload = _require_mapping(payload["ew_risk_map"], "ew_risk_map")

    ew_risk_map = EwRiskMapConfig(
        cell_size_m=_read_float(ew_risk_map_payload, "cell_size_m"),
        grid_padding_m=_read_float(ew_risk_map_payload, "grid_padding_m"),
        stamp_radius_m=_read_float(ew_risk_map_payload, "stamp_radius_m"),
        global_decay_per_tick=_read_float(
            ew_risk_map_payload, "global_decay_per_tick"
        ),
        corridor_sample_step_m=_read_float(
            ew_risk_map_payload, "corridor_sample_step_m"
        ),
        corridor_band_half_width_m=_read_float(
            ew_risk_map_payload, "corridor_band_half_width_m"
        ),
        risk_low_floor=_read_float(ew_risk_map_payload, "risk_low_floor"),
        risk_medium_floor=_read_float(ew_risk_map_payload, "risk_medium_floor"),
        weight_gnss_denied=_read_float(ew_risk_map_payload, "weight_gnss_denied"),
        weight_gnss_degraded=_read_float(
            ew_risk_map_payload, "weight_gnss_degraded"
        ),
        weight_sync_low=_read_float(ew_risk_map_payload, "weight_sync_low"),
        weight_localization_unstable=_read_float(
            ew_risk_map_payload, "weight_localization_unstable"
        ),
    )
    _validate_ew_risk_map_config(ew_risk_map)

    return AppConfig(
        config_id=_read_string(payload, "config_id"),
        schema_version=_read_string(payload, "schema_version"),
        gnss_trust=GnssTrustConfig(
            quality_weight=_read_float(gnss_trust_payload, "quality_weight"),
            availability_weight=_read_float(
                gnss_trust_payload, "availability_weight"
            ),
            denied_outage_ratio_threshold=_read_float(
                gnss_trust_payload, "denied_outage_ratio_threshold"
            ),
            denied_trust_threshold=_read_float(
                gnss_trust_payload, "denied_trust_threshold"
            ),
            degraded_trust_threshold=_read_float(
                gnss_trust_payload, "degraded_trust_threshold"
            ),
        ),
        trust_engine=TrustEngineConfig(
            gnss_trust_weight=_read_float(
                trust_engine_payload, "gnss_trust_weight"
            ),
            localization_confidence_weight=_read_float(
                trust_engine_payload, "localization_confidence_weight"
            ),
            vio_trust_weight=_read_float(trust_engine_payload, "vio_trust_weight"),
            sync_quality_weight=_read_float(
                trust_engine_payload, "sync_quality_weight"
            ),
            gnss_low_threshold=_read_float(
                trust_engine_payload, "gnss_low_threshold"
            ),
            localization_low_threshold=_read_float(
                trust_engine_payload, "localization_low_threshold"
            ),
            vio_low_threshold=_read_float(trust_engine_payload, "vio_low_threshold"),
            sync_low_threshold=_read_float(
                trust_engine_payload, "sync_low_threshold"
            ),
            default_sync_quality=_read_float(
                trust_engine_payload, "default_sync_quality"
            ),
            mode_unstable_penalty=_read_float(
                trust_engine_payload, "mode_unstable_penalty"
            ),
            effective_vio_weak_penalty=_read_float(
                trust_engine_payload, "effective_vio_weak_penalty"
            ),
            effective_vio_lost_penalty=_read_float(
                trust_engine_payload, "effective_vio_lost_penalty"
            ),
            calibration_high_floor=_read_float(
                trust_engine_payload, "calibration_high_floor"
            ),
            calibration_medium_floor=_read_float(
                trust_engine_payload, "calibration_medium_floor"
            ),
        ),
        mission=MissionConfig(
            nominal_confidence_threshold=_read_float(
                mission_payload, "nominal_confidence_threshold"
            ),
            degraded_confidence_threshold=_read_float(
                mission_payload, "degraded_confidence_threshold"
            ),
            denied_fallback_confidence_threshold=_read_float(
                mission_payload, "denied_fallback_confidence_threshold"
            ),
            emergency_land_confidence_threshold=_read_float(
                mission_payload, "emergency_land_confidence_threshold"
            ),
            denied_allowed_states=_read_string_list(
                mission_payload,
                "denied_allowed_states",
            ),
            recovery_dwell_ticks=_read_int(
                mission_payload,
                "recovery_dwell_ticks",
            ),
            safe_hold_escalation_ticks=_read_int(
                mission_payload,
                "safe_hold_escalation_ticks",
            ),
            oscillation_window_ticks=_read_int(
                mission_payload,
                "oscillation_window_ticks",
            ),
            max_state_transitions_in_window=_read_int(
                mission_payload,
                "max_state_transitions_in_window",
            ),
        ),
        vio_health=VioHealthConfig(
            good_threshold=_read_float(vio_health_payload, "good_threshold"),
            weak_threshold=_read_float(vio_health_payload, "weak_threshold"),
        ),
        vio_pipeline=VioPipelineConfig(
            max_features=_read_int(vio_pipeline_payload, "max_features"),
            gradient_threshold=_read_float(vio_pipeline_payload, "gradient_threshold"),
            match_distance_px=_read_float(vio_pipeline_payload, "match_distance_px"),
            continuity_window=_read_int(vio_pipeline_payload, "continuity_window"),
            imu_gain=_read_float(vio_pipeline_payload, "imu_gain"),
        ),
        vio_trust=VioTrustConfig(
            feature_count_floor=_read_int(vio_trust_payload, "feature_count_floor"),
            track_continuity_floor=_read_float(
                vio_trust_payload,
                "track_continuity_floor",
            ),
            reprojection_error_ceiling_px=_read_float(
                vio_trust_payload,
                "reprojection_error_ceiling_px",
            ),
            imu_alignment_ceiling=_read_float(
                vio_trust_payload,
                "imu_alignment_ceiling",
            ),
            metric_weights=VioMetricWeights(
                feature_count=_read_float(vio_metric_weights_payload, "feature_count"),
                track_continuity=_read_float(
                    vio_metric_weights_payload,
                    "track_continuity",
                ),
                reprojection_error=_read_float(
                    vio_metric_weights_payload,
                    "reprojection_error",
                ),
                imu_alignment=_read_float(
                    vio_metric_weights_payload,
                    "imu_alignment",
                ),
            ),
        ),
        localization_fusion=LocalizationFusionConfig(
            gnss_base_weight=_read_float(fusion_payload, "gnss_base_weight"),
            vio_base_weight=_read_float(fusion_payload, "vio_base_weight"),
            fused_confidence_floor=_read_float(fusion_payload, "fused_confidence_floor"),
            hysteresis_ticks=_read_int(fusion_payload, "hysteresis_ticks"),
        ),
        ew_risk_map=ew_risk_map,
    )


def _apply_config_override(
    base_payload: dict[str, Any],
    override_path: str | Path | None,
) -> dict[str, Any]:
    if override_path is None:
        return base_payload

    override_payload = load_yaml_file(override_path)
    return _merge_config_mappings(
        base_payload=base_payload,
        override_payload=override_payload,
        override_source=Path(override_path),
        field_path="config",
    )


def _merge_config_mappings(
    base_payload: dict[str, Any],
    override_payload: dict[str, Any],
    override_source: Path,
    field_path: str,
) -> dict[str, Any]:
    merged = deepcopy(base_payload)

    for key, override_value in override_payload.items():
        current_path = f"{field_path}.{key}"
        if key not in merged:
            raise ValueError(
                f"Unknown config override field in {override_source}: {current_path}"
            )

        base_value = merged[key]
        if isinstance(base_value, dict):
            if not isinstance(override_value, dict):
                raise ValueError(
                    f"Config override field {current_path} in {override_source} "
                    "must remain a mapping."
                )
            merged[key] = _merge_config_mappings(
                base_payload=base_value,
                override_payload=override_value,
                override_source=override_source,
                field_path=current_path,
            )
            continue

        if isinstance(override_value, dict):
            raise ValueError(
                f"Config override field {current_path} in {override_source} "
                "must not replace a scalar with a mapping."
            )

        merged[key] = deepcopy(override_value)

    return merged


def _strip_canonical_excluded_fields(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(payload)
    for field_name in CANONICAL_CONFIG_EXCLUDED_FIELDS:
        normalized.pop(field_name, None)
    return normalized


def _normalize_canonical_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _normalize_canonical_value(value[key])
            for key in sorted(value)
        }
    if isinstance(value, tuple):
        return [_normalize_canonical_value(item) for item in value]
    if isinstance(value, list):
        return [_normalize_canonical_value(item) for item in value]
    return value


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping.")
    return value


def _read_float(payload: dict[str, Any], field_name: str) -> float:
    if field_name not in payload:
        raise ValueError(f"Missing config field: {field_name}")

    raw_value = payload[field_name]
    if isinstance(raw_value, bool):
        raise ValueError(f"Config field {field_name} must be numeric, got boolean.")

    try:
        value = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Config field {field_name} must be numeric.") from exc

    if not isfinite(value):
        raise ValueError(f"Config field {field_name} must be finite.")

    return value


def _read_int(payload: dict[str, Any], field_name: str) -> int:
    if field_name not in payload:
        raise ValueError(f"Missing config field: {field_name}")

    raw_value = payload[field_name]
    if isinstance(raw_value, bool):
        raise ValueError(f"Config field {field_name} must be an integer, got boolean.")

    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Config field {field_name} must be an integer.") from exc

    return value


def _read_string(payload: dict[str, Any], field_name: str) -> str:
    if field_name not in payload:
        raise ValueError(f"Missing config field: {field_name}")

    raw_value = payload[field_name]
    if not isinstance(raw_value, str):
        raise ValueError(f"Config field {field_name} must be a string.")

    value = raw_value.strip()
    if not value:
        raise ValueError(f"Config field {field_name} must be a non-empty string.")

    return value


def _read_string_list(payload: dict[str, Any], field_name: str) -> tuple[str, ...]:
    if field_name not in payload:
        raise ValueError(f"Missing config field: {field_name}")

    raw_value = payload[field_name]
    if not isinstance(raw_value, list) or not raw_value:
        raise ValueError(f"{field_name} must be a non-empty list.")

    values: list[str] = []
    for item in raw_value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} entries must be strings.")
        value = item.strip()
        if not value:
            raise ValueError(f"{field_name} entries must be non-empty strings.")
        values.append(value)

    return tuple(values)


def _validate_ew_risk_map_config(config: EwRiskMapConfig) -> None:
    positive_fields = {
        "cell_size_m": config.cell_size_m,
        "grid_padding_m": config.grid_padding_m,
        "stamp_radius_m": config.stamp_radius_m,
        "corridor_sample_step_m": config.corridor_sample_step_m,
        "corridor_band_half_width_m": config.corridor_band_half_width_m,
    }
    for field_name, value in positive_fields.items():
        if value <= 0.0:
            raise ValueError(f"ew_risk_map.{field_name} must be positive.")

    bounded_fields = {
        "global_decay_per_tick": config.global_decay_per_tick,
        "risk_low_floor": config.risk_low_floor,
        "risk_medium_floor": config.risk_medium_floor,
        "weight_gnss_denied": config.weight_gnss_denied,
        "weight_gnss_degraded": config.weight_gnss_degraded,
        "weight_sync_low": config.weight_sync_low,
        "weight_localization_unstable": config.weight_localization_unstable,
    }
    for field_name, value in bounded_fields.items():
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"ew_risk_map.{field_name} must be within 0.0-1.0.")

    if config.risk_low_floor > config.risk_medium_floor:
        raise ValueError("ew_risk_map.risk_low_floor must not exceed risk_medium_floor.")


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = _prepare_lines(text)
    if not lines:
        return {}

    value, next_index = _parse_block(lines, 0, lines[0][0])
    if next_index != len(lines):
        raise ValueError("Failed to consume the full YAML document.")
    if not isinstance(value, dict):
        raise ValueError("Top-level YAML document must be a mapping.")
    return value


def _prepare_lines(text: str) -> list[tuple[int, str]]:
    prepared: list[tuple[int, str]] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError("Fallback YAML parser requires 2-space indentation.")
        prepared.append((indent, line.lstrip()))

    return prepared


def _parse_block(
    lines: list[tuple[int, str]], index: int, indent: int
) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index

    current_indent, content = lines[index]
    if current_indent != indent:
        raise ValueError(
            f"Unexpected indentation at line {index + 1}: expected {indent}, got {current_indent}"
        )

    if content.startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_dict(lines, index, indent)


def _parse_dict(
    lines: list[tuple[int, str]], index: int, indent: int
) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}

    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ValueError(
                f"Unexpected indentation inside mapping at line {index + 1}: {current_indent}"
            )
        if content.startswith("- "):
            break

        if ":" not in content:
            raise ValueError(f"Invalid mapping entry at line {index + 1}: {content}")

        key, remainder = content.split(":", 1)
        key = key.strip()
        remainder = remainder.strip()

        if remainder:
            result[key] = _parse_scalar(remainder)
            index += 1
            continue

        index += 1
        if index >= len(lines) or lines[index][0] <= indent:
            result[key] = {}
            continue

        nested_value, index = _parse_block(lines, index, indent + 2)
        result[key] = nested_value

    return result, index


def _parse_list(
    lines: list[tuple[int, str]], index: int, indent: int
) -> tuple[list[Any], int]:
    result: list[Any] = []

    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent != indent or not content.startswith("- "):
            break

        remainder = content[2:].strip()
        if remainder:
            result.append(_parse_scalar(remainder))
            index += 1
            continue

        index += 1
        if index >= len(lines) or lines[index][0] <= indent:
            result.append(None)
            continue

        nested_value, index = _parse_block(lines, index, indent + 2)
        result.append(nested_value)

    return result, index


def _parse_scalar(value: str) -> Any:
    if value.startswith("{") or value.startswith("["):
        return json.loads(value)

    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "none"}:
        return None

    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value
