#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_ID="${1:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$ROOT_DIR/artifacts/runs/$RUN_ID"

SCENARIOS=(
  "$ROOT_DIR/scenarios/baseline/s1_nominal.yaml"
  "$ROOT_DIR/scenarios/baseline/s2_gnss_degraded_corridor.yaml"
  "$ROOT_DIR/scenarios/baseline/s3_gnss_denied_zone.yaml"
)

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p "$RUN_DIR"

echo "Running baseline regression into $RUN_DIR"
for scenario in "${SCENARIOS[@]}"; do
  scenario_name="$(basename "$scenario")"
  vio_healthy="true"
  if [[ "$scenario_name" == "s3_gnss_denied_zone.yaml" ]]; then
    vio_healthy="false"
  fi

  echo "Scenario $scenario_name uses VIO_HEALTHY=$vio_healthy"
  VIO_HEALTHY="$vio_healthy" "$ROOT_DIR/scripts/run_scenario.sh" "$scenario" "$RUN_DIR"
done

set +e
"$PYTHON_BIN" -m evaluation.regression_compare "$RUN_DIR" --output "$RUN_DIR/regression_result.json"
REGRESSION_EXIT=$?
set -e

"$PYTHON_BIN" -m evaluation.summary_report "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
"$ROOT_DIR/scripts/check_artifacts.sh" "$RUN_DIR"

echo
cat "$RUN_DIR/summary.md"
echo
echo "Artifacts stored in $RUN_DIR"

exit "$REGRESSION_EXIT"
