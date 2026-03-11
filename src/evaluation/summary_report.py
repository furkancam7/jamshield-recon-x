"""Summary report generation for baseline regression runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.artifact_schema import SUMMARY_SCHEMA_VERSION, validate_summary
from evaluation.regression_compare import EXPECTED_SCENARIO_IDS, load_reports
from common.runtime_metadata import utc_timestamp


def generate_summary(
    run_dir: str | Path, regression_result: dict[str, Any] | None = None
) -> tuple[dict[str, Any], str]:
    base_path = Path(run_dir)
    reports = load_reports(base_path)

    scenarios = []
    config_ids = set()
    software_revisions = set()
    for scenario_id in EXPECTED_SCENARIO_IDS:
        report = reports[scenario_id]
        config_ids.add(report["config_id"])
        software_revisions.add(report["software_revision"])
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "gnss_state": report["gnss_state"],
                "gnss_trust_score": report["trust_score"],
                "mission_confidence": report["mission_confidence"],
                "mission_state": report["mission_state"],
                "ate_rmse": report.get("ate_m"),
                "timestamp": report["timestamp"],
            }
        )

    if len(config_ids) != 1:
        raise ValueError("Reports must share a single config_id.")
    if len(software_revisions) != 1:
        raise ValueError("Reports must share a single software_revision.")

    summary = {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "run_id": base_path.name,
        "scenario_ids": EXPECTED_SCENARIO_IDS,
        "scenarios": scenarios,
        "checks": regression_result["checks"] if regression_result else [],
        "overall_regression_result": (
            regression_result["overall_result"] if regression_result else "UNKNOWN"
        ),
        "config_id": next(iter(config_ids)),
        "software_revision": next(iter(software_revisions)),
        "generated_at": utc_timestamp(),
    }
    validate_summary(summary)
    markdown = _render_markdown(summary)
    return summary, markdown


def write_summary_files(
    run_dir: str | Path,
    summary: dict[str, Any],
    markdown: str,
) -> tuple[Path, Path]:
    base_path = Path(run_dir)
    summary_json_path = base_path / "summary.json"
    summary_md_path = base_path / "summary.md"

    summary_json_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    summary_md_path.write_text(markdown, encoding="utf-8")
    return summary_json_path, summary_md_path


def _render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Regression Summary",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Overall result: `{summary['overall_regression_result']}`",
        "",
        "## Scenario Results",
        "",
        f"- Config ID: `{summary['config_id']}`",
        f"- Software revision: `{summary['software_revision']}`",
        "",
        "| Scenario | GNSS State | Trust Score | Mission Confidence | Mission State | ATE RMSE |",
        "| --- | --- | ---: | ---: | --- | ---: |",
    ]

    for scenario in summary["scenarios"]:
        lines.append(
            "| {scenario_id} | {gnss_state} | {gnss_trust_score:.3f} | {mission_confidence:.3f} | {mission_state} | {ate_rmse:.3f} |".format(
                **scenario
            )
        )

    lines.extend(["", "## Checks", ""])

    if summary["checks"]:
        for check in summary["checks"]:
            status = "PASS" if check["passed"] else "FAIL"
            lines.append(f"- `{check['name']}`: {status} - {check['detail']}")
    else:
        lines.append("- No regression checks were provided.")

    lines.append("")
    return "\n".join(lines)


def _load_regression_result(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate regression summary files.")
    parser.add_argument("run_dir", help="Directory containing scenario report artifacts.")
    parser.add_argument(
        "--regression-result",
        help="Path to regression_result.json.",
    )
    args = parser.parse_args()

    regression_result = _load_regression_result(args.regression_result)
    summary, markdown = generate_summary(args.run_dir, regression_result)
    summary_json_path, summary_md_path = write_summary_files(
        args.run_dir, summary, markdown
    )

    print(json.dumps({"summary_json": str(summary_json_path), "summary_md": str(summary_md_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
