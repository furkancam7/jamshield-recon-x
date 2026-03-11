"""YAML loading helpers and app config loading."""

from __future__ import annotations

from copy import deepcopy
import json
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TrustConfig:
    quality_weight: float
    availability_weight: float
    mission_confidence_weight: float
    vio_bonus: float
    denied_outage_ratio_threshold: float
    denied_trust_threshold: float
    degraded_trust_threshold: float


@dataclass(frozen=True)
class MissionConfig:
    nominal_confidence_threshold: float
    degraded_confidence_threshold: float
    denied_fallback_confidence_threshold: float
    emergency_land_confidence_threshold: float
    denied_allowed_states: tuple[str, ...]


@dataclass(frozen=True)
class AppConfig:
    config_id: str
    schema_version: str
    trust: TrustConfig
    mission: MissionConfig


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
    required_fields = {"config_id", "schema_version", "trust", "mission"}
    missing = required_fields.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(
            f"Config missing required fields in {source_path}: {missing_list}"
        )

    trust_payload = _require_mapping(payload["trust"], "trust")
    mission_payload = _require_mapping(payload["mission"], "mission")

    return AppConfig(
        config_id=_read_string(payload, "config_id"),
        schema_version=_read_string(payload, "schema_version"),
        trust=TrustConfig(
            quality_weight=_read_float(trust_payload, "quality_weight"),
            availability_weight=_read_float(trust_payload, "availability_weight"),
            mission_confidence_weight=_read_float(
                trust_payload, "mission_confidence_weight"
            ),
            vio_bonus=_read_float(trust_payload, "vio_bonus"),
            denied_outage_ratio_threshold=_read_float(
                trust_payload, "denied_outage_ratio_threshold"
            ),
            denied_trust_threshold=_read_float(
                trust_payload, "denied_trust_threshold"
            ),
            degraded_trust_threshold=_read_float(
                trust_payload, "degraded_trust_threshold"
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
        ),
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
