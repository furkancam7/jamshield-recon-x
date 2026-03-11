"""Stable schema validation for evaluation artifacts."""

from __future__ import annotations

from typing import Any

REPORT_SCHEMA_VERSION = "1.0"
SUMMARY_SCHEMA_VERSION = "1.0"

REQUIRED_REPORT_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_id",
    "map_name",
    "run_seed",
    "gnss_condition",
    "gnss_state",
    "trust_score",
    "mission_confidence",
    "mission_state",
    "vio_healthy",
    "vio_state",
    "ate_m",
    "route_length_m",
    "ground_truth_usage",
    "config_id",
    "software_revision",
    "timestamp",
    "scenario_metadata",
}

REQUIRED_SUMMARY_FIELDS = {
    "schema_version",
    "run_id",
    "scenario_ids",
    "scenarios",
    "checks",
    "overall_regression_result",
    "config_id",
    "software_revision",
    "generated_at",
}

SCENARIO_METADATA_FIELDS = {"title", "description", "owner"}


def validate_report(payload: dict[str, Any]) -> None:
    missing = REQUIRED_REPORT_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Report missing required fields: {missing_list}")

    metadata = payload["scenario_metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("scenario_metadata must be a mapping.")
    metadata_missing = SCENARIO_METADATA_FIELDS.difference(metadata)
    if metadata_missing:
        missing_list = ", ".join(sorted(metadata_missing))
        raise ValueError(f"scenario_metadata missing required fields: {missing_list}")

    if payload["schema_version"] != REPORT_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported report schema_version: {payload['schema_version']}"
        )


def validate_summary(payload: dict[str, Any]) -> None:
    missing = REQUIRED_SUMMARY_FIELDS.difference(payload)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Summary missing required fields: {missing_list}")

    if payload["schema_version"] != SUMMARY_SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported summary schema_version: {payload['schema_version']}"
        )
