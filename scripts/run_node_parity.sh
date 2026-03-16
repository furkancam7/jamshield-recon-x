#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BASELINE_RUN_DIR="${1:?usage: run_node_parity.sh <baseline_run_dir> [node_run_dir] [scenario_id ...]}"
NODE_RUN_DIR="${2:-$ROOT_DIR/artifacts/runs/$(date -u +%Y%m%dT%H%M%SZ)_node_parity}"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/sim/default.yaml}"
RUN_ID="${RUN_ID:-$(basename "$NODE_RUN_DIR")}"

if [[ $# -gt 2 ]]; then
  SCENARIO_IDS=("${@:3}")
else
  SCENARIO_IDS=("s1_nominal" "s3_gnss_denied_zone")
fi

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$NODE_RUN_DIR"

echo "Running node parity scenarios into $NODE_RUN_DIR"
for scenario_id in "${SCENARIO_IDS[@]}"; do
  scenario_path="$ROOT_DIR/scenarios/baseline/${scenario_id}.yaml"
  if [[ ! -f "$scenario_path" ]]; then
    echo "Missing scenario manifest: $scenario_path" >&2
    exit 1
  fi
  RUN_ID="$RUN_ID" CONFIG_PATH="$CONFIG_PATH" "$ROOT_DIR/scripts/run_node_scenario.sh" "$scenario_path" "$NODE_RUN_DIR"
done

"$PYTHON_BIN" -m evaluation.node_parity_compare "$BASELINE_RUN_DIR" "$NODE_RUN_DIR" --scenarios "${SCENARIO_IDS[@]}"
echo
cat "$NODE_RUN_DIR/node_parity_results.md"
