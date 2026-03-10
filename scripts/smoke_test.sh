#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TMP_DIR="$(mktemp -d)"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" -m unittest discover -s "$ROOT_DIR/tests/unit"

VIO_HEALTHY=true "$ROOT_DIR/scripts/run_scenario.sh" "$ROOT_DIR/scenarios/baseline/s1_nominal.yaml" "$TMP_DIR"
VIO_HEALTHY=false "$ROOT_DIR/scripts/run_scenario.sh" "$ROOT_DIR/scenarios/baseline/s3_gnss_denied_zone.yaml" "$TMP_DIR"

echo "Smoke test artifacts written to $TMP_DIR"
