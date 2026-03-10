#!/usr/bin/env bash
set -euo pipefail

RUN_DIR="${1:?usage: check_artifacts.sh <run_dir>}"

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

echo "Artifact check passed for $RUN_DIR"

