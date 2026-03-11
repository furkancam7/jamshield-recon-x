#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

SCENARIO_PATH="${1:?usage: run_scenario.sh <scenario_yaml> [output_dir]}"
OUTPUT_DIR="${2:-$ROOT_DIR/artifacts}"
VIO_HEALTHY="${VIO_HEALTHY:-true}"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/sim/default.yaml}"
RUN_ID="${RUN_ID:-$(basename "$OUTPUT_DIR")}"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ "$VIO_HEALTHY" == "false" ]]; then
  "$PYTHON_BIN" -m scenario_orchestrator.main "$SCENARIO_PATH" --output-dir "$OUTPUT_DIR" --config "$CONFIG_PATH" --run-id "$RUN_ID" --vio-unhealthy
else
  "$PYTHON_BIN" -m scenario_orchestrator.main "$SCENARIO_PATH" --output-dir "$OUTPUT_DIR" --config "$CONFIG_PATH" --run-id "$RUN_ID"
fi
