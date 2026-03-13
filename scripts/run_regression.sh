#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_ID="${1:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$ROOT_DIR/artifacts/runs/$RUN_ID"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/sim/default.yaml}"
EVAL_CONFIG_PATH="${EVAL_CONFIG_PATH:-$ROOT_DIR/configs/eval/default.yaml}"

SCENARIOS=(
  "$ROOT_DIR/scenarios/baseline/s1_nominal.yaml"
  "$ROOT_DIR/scenarios/baseline/s2_gnss_degraded_corridor.yaml"
  "$ROOT_DIR/scenarios/baseline/s3_gnss_denied_zone.yaml"
  "$ROOT_DIR/scenarios/baseline/s4_denied_vio_good.yaml"
  "$ROOT_DIR/scenarios/baseline/s5_denied_vio_weak.yaml"
  "$ROOT_DIR/scenarios/baseline/s6_denied_vio_lost.yaml"
  "$ROOT_DIR/scenarios/baseline/s7_conflict_score_dominates.yaml"
  "$ROOT_DIR/scenarios/baseline/s8_conflict_state_dominates.yaml"
  "$ROOT_DIR/scenarios/baseline/s9_fusion_gnss_primary.yaml"
  "$ROOT_DIR/scenarios/baseline/s10_fusion_degraded_fused.yaml"
  "$ROOT_DIR/scenarios/baseline/s11_fusion_denied_vio_only.yaml"
  "$ROOT_DIR/scenarios/baseline/s12_fusion_dead_reckoning.yaml"
  "$ROOT_DIR/scenarios/baseline/s13_sync_low_nominal.yaml"
  "$ROOT_DIR/scenarios/baseline/s14_sync_low_denied_good.yaml"
  "$ROOT_DIR/scenarios/baseline/s15_safe_hold_timeout_abort.yaml"
  "$ROOT_DIR/scenarios/baseline/s16_recovery_dwell_delays_resume.yaml"
  "$ROOT_DIR/scenarios/baseline/s17_state_oscillation_safe_hold.yaml"
  "$ROOT_DIR/scenarios/baseline/s18_abort_terminal.yaml"
  "$ROOT_DIR/scenarios/baseline/s19_ew_mid_route_denial_hotspot.yaml"
  "$ROOT_DIR/scenarios/baseline/s20_ew_decay_after_recovery.yaml"
)

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

mkdir -p "$RUN_DIR"

echo "Running baseline regression into $RUN_DIR"
for scenario in "${SCENARIOS[@]}"; do
  scenario_name="$(basename "$scenario")"
  echo "Scenario $scenario_name uses manifest-driven VIO pipeline inputs"
  RUN_ID="$RUN_ID" CONFIG_PATH="$CONFIG_PATH" "$ROOT_DIR/scripts/run_scenario.sh" "$scenario" "$RUN_DIR"
done

set +e
"$PYTHON_BIN" -m evaluation.regression_compare "$RUN_DIR" --config "$CONFIG_PATH" --output "$RUN_DIR/regression_result.json"
REGRESSION_EXIT=$?
set -e

"$PYTHON_BIN" -m trust_engine.calibration "$RUN_DIR" --config "$CONFIG_PATH" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.ew_metrics "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.tactical_summary_bundle "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.replay_evaluation "$RUN_DIR" --config "$CONFIG_PATH" --eval-config "$EVAL_CONFIG_PATH" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.summary_report "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
"$ROOT_DIR/scripts/check_artifacts.sh" "$RUN_DIR"

echo
cat "$RUN_DIR/summary.md"
echo
echo "Artifacts stored in $RUN_DIR"

exit "$REGRESSION_EXIT"
