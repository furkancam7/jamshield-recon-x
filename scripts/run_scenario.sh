#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

SCENARIO_PATH="${1:?usage: run_scenario.sh <scenario_yaml> [output_dir]}"
OUTPUT_DIR="${2:-$ROOT_DIR/artifacts}"
VIO_HEALTHY="${VIO_HEALTHY:-true}"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

if [[ "$VIO_HEALTHY" == "false" ]]; then
  "$PYTHON_BIN" -m scenario_orchestrator.main "$SCENARIO_PATH" --output-dir "$OUTPUT_DIR" --vio-unhealthy
else
  "$PYTHON_BIN" -m scenario_orchestrator.main "$SCENARIO_PATH" --output-dir "$OUTPUT_DIR"
fi

