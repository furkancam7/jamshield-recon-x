"""YAML loading helpers with a stdlib fallback parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


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

