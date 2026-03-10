#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP_DIR="$(mktemp -d)"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" -m unittest discover -s "$ROOT_DIR/tests/unit"
"$PYTHON_BIN" -m scenario_orchestrator.main "$ROOT_DIR/scenarios/baseline/s1_nominal.yaml" --output-dir "$TMP_DIR"
"$PYTHON_BIN" -m scenario_orchestrator.main "$ROOT_DIR/scenarios/baseline/s3_gnss_denied_zone.yaml" --output-dir "$TMP_DIR" --vio-unhealthy

echo "Smoke test artifacts written to $TMP_DIR"

