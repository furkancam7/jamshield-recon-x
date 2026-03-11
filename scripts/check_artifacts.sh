#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:?usage: check_artifacts.sh <run_dir>}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

REQUIRED_FILES=(
  "$RUN_DIR/s1_nominal_report.json"
  "$RUN_DIR/s2_gnss_degraded_corridor_report.json"
  "$RUN_DIR/s3_gnss_denied_zone_report.json"
  "$RUN_DIR/regression_result.json"
  "$RUN_DIR/summary.json"
  "$RUN_DIR/summary.md"
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

from evaluation.artifact_schema import validate_report, validate_summary

run_dir = Path(sys.argv[1])
for report_path in run_dir.glob("*_report.json"):
    validate_report(json.loads(report_path.read_text(encoding="utf-8")))

summary_path = run_dir / "summary.json"
validate_summary(json.loads(summary_path.read_text(encoding="utf-8")))
PY

echo "Artifact check passed for $RUN_DIR"
