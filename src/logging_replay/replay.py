"""Deterministic replay helpers for file-based regression validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compare_replay_run(
    *,
    scenario_id: str,
    original_run_dir: str | Path,
    replay_run_dir: str | Path,
) -> dict[str, Any]:
    original_base = Path(original_run_dir)
    replay_base = Path(replay_run_dir)

    original_runtime_trace = _load_json(
        original_base / f"{scenario_id}_runtime_trace.json"
    )
    replay_runtime_trace = _load_json(replay_base / f"{scenario_id}_runtime_trace.json")
    divergence = _first_divergence(
        original_runtime_trace.get("entries", []),
        replay_runtime_trace.get("entries", []),
        field_prefix="runtime_trace",
    )
    if divergence is not None:
        return _result("FAIL", scenario_id, divergence)

    original_mission_audit = _load_json(
        original_base / f"{scenario_id}_mission_audit.json"
    )
    replay_mission_audit = _load_json(replay_base / f"{scenario_id}_mission_audit.json")
    divergence = _first_divergence(
        original_mission_audit.get("entries", []),
        replay_mission_audit.get("entries", []),
        field_prefix="mission_audit",
    )
    if divergence is not None:
        return _result("FAIL", scenario_id, divergence)

    original_report = _normalize_report(
        _load_json(original_base / f"{scenario_id}_report.json")
    )
    replay_report = _normalize_report(_load_json(replay_base / f"{scenario_id}_report.json"))
    divergence = _first_divergence(original_report, replay_report, field_prefix="report")
    if divergence is not None:
        return _result("FAIL", scenario_id, divergence)

    original_ew_map = _load_json(original_base / f"{scenario_id}_ew_risk_map.json")
    replay_ew_map = _load_json(replay_base / f"{scenario_id}_ew_risk_map.json")
    if original_ew_map["risk_cells_hash"] != replay_ew_map["risk_cells_hash"]:
        return _result(
            "FAIL",
            scenario_id,
            {
                "tick_index": None,
                "field_name": "ew_risk_map.risk_cells_hash",
                "original_value": original_ew_map["risk_cells_hash"],
                "replay_value": replay_ew_map["risk_cells_hash"],
            },
        )

    original_tactical = _load_json(
        original_base / f"{scenario_id}_tactical_summary.json"
    )
    replay_tactical = _load_json(replay_base / f"{scenario_id}_tactical_summary.json")
    for field_name in ("primary_reason_code", "advisory_code", "summary_text"):
        if original_tactical[field_name] != replay_tactical[field_name]:
            return _result(
                "FAIL",
                scenario_id,
                {
                    "tick_index": None,
                    "field_name": f"tactical_summary.{field_name}",
                    "original_value": original_tactical[field_name],
                    "replay_value": replay_tactical[field_name],
                },
            )

    return _result("PASS", scenario_id, None)


def _normalize_report(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for field_name in (
        "run_id",
        "timestamp",
        "report_path",
        "mission_audit_path",
        "ew_risk_map_path",
        "tactical_summary_path",
        "runtime_trace_path",
        "truth_trace_path",
        "deterministic_replay_passed",
        "evaluation_verdict",
        "invalid_run",
        "evaluation_primary_reason_code",
    ):
        normalized.pop(field_name, None)
    return normalized


def _first_divergence(
    original_value: Any,
    replay_value: Any,
    *,
    field_prefix: str,
) -> dict[str, Any] | None:
    if isinstance(original_value, list) and isinstance(replay_value, list):
        if len(original_value) != len(replay_value):
            return {
                "tick_index": None,
                "field_name": f"{field_prefix}.length",
                "original_value": len(original_value),
                "replay_value": len(replay_value),
            }
        for index, (original_item, replay_item) in enumerate(
            zip(original_value, replay_value)
        ):
            divergence = _first_divergence(
                original_item,
                replay_item,
                field_prefix=f"{field_prefix}[{index}]",
            )
            if divergence is not None:
                if divergence["tick_index"] is None:
                    divergence["tick_index"] = index
                return divergence
        return None

    if isinstance(original_value, dict) and isinstance(replay_value, dict):
        original_keys = sorted(original_value)
        replay_keys = sorted(replay_value)
        if original_keys != replay_keys:
            return {
                "tick_index": None,
                "field_name": f"{field_prefix}.keys",
                "original_value": original_keys,
                "replay_value": replay_keys,
            }
        for key in original_keys:
            divergence = _first_divergence(
                original_value[key],
                replay_value[key],
                field_prefix=f"{field_prefix}.{key}",
            )
            if divergence is not None:
                return divergence
        return None

    if original_value != replay_value:
        return {
            "tick_index": None,
            "field_name": field_prefix,
            "original_value": original_value,
            "replay_value": replay_value,
        }
    return None


def _result(
    status: str,
    scenario_id: str,
    divergence: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "replay_result": status,
        "divergence": divergence,
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
