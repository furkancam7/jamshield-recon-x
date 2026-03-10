"""Summary report generation for baseline regression runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.regression_compare import EXPECTED_SCENARIO_IDS, load_reports


def generate_summary(
    run_dir: str | Path, regression_result: dict[str, Any] | None = None
) -> tuple[dict[str, Any], str]:
    base_path = Path(run_dir)
    reports = load_reports(base_path)

    scenarios = []
    for scenario_id in EXPECTED_SCENARIO_IDS:
        report = reports[scenario_id]
        scenarios.append(
            {
                "scenario_id": scenario_id,
                "gnss_state": report["gnss_state"],
                "gnss_trust_score": report["trust_score"],
                "mission_state": report["mission_state"],
                "ate_rmse": report.get("ate_m"),
            }
        )

    summary = {
        "run_id": base_path.name,
        "scenario_ids": EXPECTED_SCENARIO_IDS,
        "scenarios": scenarios,
        "checks": regression_result["checks"] if regression_result else [],
        "overall_regression_result": (
            regression_result["overall_result"] if regression_result else "UNKNOWN"
        ),
    }
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
        "| Scenario | GNSS State | Trust Score | Mission State | ATE RMSE |",
        "| --- | --- | ---: | --- | ---: |",
    ]

    for scenario in summary["scenarios"]:
        lines.append(
            "| {scenario_id} | {gnss_state} | {gnss_trust_score:.3f} | {mission_state} | {ate_rmse:.3f} |".format(
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

