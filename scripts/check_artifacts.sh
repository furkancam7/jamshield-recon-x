#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:?usage: check_artifacts.sh <run_dir>}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

REQUIRED_FILES=(
  "$RUN_DIR/regression_result.json"
  "$RUN_DIR/summary.json"
  "$RUN_DIR/summary.md"
  "$RUN_DIR/trust_calibration.json"
  "$RUN_DIR/trust_calibration.md"
  "$RUN_DIR/trust_calibration.csv"
  "$RUN_DIR/ew_metrics.json"
  "$RUN_DIR/ew_metrics.md"
  "$RUN_DIR/ew_metrics.csv"
  "$RUN_DIR/tactical_summary_bundle.json"
  "$RUN_DIR/tactical_summary_bundle.md"
  "$RUN_DIR/tactical_summary_bundle.csv"
  "$RUN_DIR/replay_results.json"
  "$RUN_DIR/replay_results.md"
  "$RUN_DIR/replay_results.csv"
  "$RUN_DIR/evaluation_metrics.json"
  "$RUN_DIR/evaluation_metrics.md"
  "$RUN_DIR/evaluation_metrics.csv"
  "$RUN_DIR/evaluation_verdicts.json"
  "$RUN_DIR/evaluation_verdicts.md"
  "$RUN_DIR/evaluation_verdicts.csv"
)

for artifact in "${REQUIRED_FILES[@]}"; do
  if [[ ! -f "$artifact" ]]; then
    echo "Missing required artifact: $artifact" >&2
    exit 1
  fi
done

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" - <<'PY' "$RUN_DIR"
import json
import sys
from pathlib import Path

from evaluation.artifact_schema import (
    validate_evaluation_metrics_bundle,
    validate_evaluation_verdicts_bundle,
    validate_ew_metrics_bundle,
    validate_ew_risk_map,
    validate_mission_audit,
    validate_replay_results_bundle,
    validate_report,
    validate_runtime_trace,
    validate_summary,
    validate_tactical_summary,
    validate_tactical_summary_bundle,
    validate_truth_trace,
)
from evaluation.regression_compare import EXPECTED_SCENARIO_IDS

run_dir = Path(sys.argv[1])
for scenario_id in EXPECTED_SCENARIO_IDS:
    report_path = run_dir / f"{scenario_id}_report.json"
    if not report_path.exists():
        raise FileNotFoundError(f"Missing report artifact: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    validate_report(report)

    audit_path = run_dir / f"{scenario_id}_mission_audit.json"
    if not audit_path.exists():
        raise FileNotFoundError(f"Missing mission audit artifact: {audit_path}")
    validate_mission_audit(json.loads(audit_path.read_text(encoding="utf-8")))

    runtime_trace_path = run_dir / f"{scenario_id}_runtime_trace.json"
    if not runtime_trace_path.exists():
        raise FileNotFoundError(f"Missing runtime trace artifact: {runtime_trace_path}")
    validate_runtime_trace(json.loads(runtime_trace_path.read_text(encoding="utf-8")))

    truth_trace_path = run_dir / f"{scenario_id}_truth_trace.json"
    if not truth_trace_path.exists():
        raise FileNotFoundError(f"Missing truth trace artifact: {truth_trace_path}")
    validate_truth_trace(json.loads(truth_trace_path.read_text(encoding="utf-8")))

    ew_map_path = run_dir / f"{scenario_id}_ew_risk_map.json"
    if not ew_map_path.exists():
        raise FileNotFoundError(f"Missing EW risk-map artifact: {ew_map_path}")
    validate_ew_risk_map(json.loads(ew_map_path.read_text(encoding="utf-8")))

    tactical_summary_path = run_dir / f"{scenario_id}_tactical_summary.json"
    if not tactical_summary_path.exists():
        raise FileNotFoundError(
            f"Missing tactical summary artifact: {tactical_summary_path}"
        )
    validate_tactical_summary(
        json.loads(tactical_summary_path.read_text(encoding="utf-8"))
    )

summary_path = run_dir / "summary.json"
validate_summary(json.loads(summary_path.read_text(encoding="utf-8")))
ew_metrics_path = run_dir / "ew_metrics.json"
validate_ew_metrics_bundle(json.loads(ew_metrics_path.read_text(encoding="utf-8")))
tactical_bundle_path = run_dir / "tactical_summary_bundle.json"
validate_tactical_summary_bundle(
    json.loads(tactical_bundle_path.read_text(encoding="utf-8"))
)
replay_results_path = run_dir / "replay_results.json"
validate_replay_results_bundle(
    json.loads(replay_results_path.read_text(encoding="utf-8"))
)
evaluation_metrics_path = run_dir / "evaluation_metrics.json"
validate_evaluation_metrics_bundle(
    json.loads(evaluation_metrics_path.read_text(encoding="utf-8"))
)
evaluation_verdicts_path = run_dir / "evaluation_verdicts.json"
validate_evaluation_verdicts_bundle(
    json.loads(evaluation_verdicts_path.read_text(encoding="utf-8"))
)
PY

echo "Artifact check passed for $RUN_DIR"
