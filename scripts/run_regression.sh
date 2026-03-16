#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUN_ID="${1:-$(date -u +%Y%m%dT%H%M%SZ)}"
RUN_DIR="$ROOT_DIR/artifacts/runs/$RUN_ID"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/sim/default.yaml}"
EVAL_CONFIG_PATH="${EVAL_CONFIG_PATH:-$ROOT_DIR/configs/eval/default.yaml}"
ENABLE_NODE_PARITY="${ENABLE_NODE_PARITY:-false}"
NODE_PARITY_SCENARIOS="${NODE_PARITY_SCENARIOS:-s1_nominal,s3_gnss_denied_zone}"
NODE_PARITY_RUN_DIR="$RUN_DIR/node_runtime"
ENABLE_ROS2_LAUNCH_PROBE="${ENABLE_ROS2_LAUNCH_PROBE:-false}"
ROS2_LAUNCH_SCENARIOS="${ROS2_LAUNCH_SCENARIOS:-s1_nominal,s3_gnss_denied_zone}"
ROS2_LAUNCH_RUN_DIR="$RUN_DIR/ros2_launch_runtime"
ROS2_LAUNCH_BACKEND="${ROS2_LAUNCH_BACKEND:-repo_wrapper}"
ENABLE_ROS2_VERIFICATION_PROBE="${ENABLE_ROS2_VERIFICATION_PROBE:-false}"
ROS2_VERIFICATION_SCENARIOS="${ROS2_VERIFICATION_SCENARIOS:-s1_nominal,s3_gnss_denied_zone}"
ROS2_VERIFICATION_RUN_DIR="$RUN_DIR/ros2_verification_runtime"
ENABLE_HEALTH_MONITOR_PROBE="${ENABLE_HEALTH_MONITOR_PROBE:-false}"
HEALTH_MONITOR_SCENARIOS="${HEALTH_MONITOR_SCENARIOS:-s1_nominal,s13_sync_low_nominal}"
HEALTH_MONITOR_RUN_DIR="$RUN_DIR/health_monitor_runtime"

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

if [[ "$ENABLE_ROS2_VERIFICATION_PROBE" == "true" && "$ENABLE_ROS2_LAUNCH_PROBE" != "true" ]]; then
  echo "ENABLE_ROS2_VERIFICATION_PROBE=true requires ENABLE_ROS2_LAUNCH_PROBE=true." >&2
  exit 1
fi

mkdir -p "$RUN_DIR"
NODE_PARITY_EXIT=0
ROS2_LAUNCH_EXIT=0
ROS2_VERIFICATION_EXIT=0
HEALTH_MONITOR_EXIT=0

echo "Running baseline regression into $RUN_DIR"
for scenario in "${SCENARIOS[@]}"; do
  scenario_name="$(basename "$scenario")"
  echo "Scenario $scenario_name uses manifest-driven VIO pipeline inputs"
  RUN_ID="$RUN_ID" CONFIG_PATH="$CONFIG_PATH" "$ROOT_DIR/scripts/run_scenario.sh" "$scenario" "$RUN_DIR"
done

if [[ "$ENABLE_NODE_PARITY" == "true" ]]; then
  mkdir -p "$NODE_PARITY_RUN_DIR"
  IFS=',' read -r -a NODE_PARITY_IDS <<< "$NODE_PARITY_SCENARIOS"
  echo "Running node parity probe into $NODE_PARITY_RUN_DIR"
  for scenario_id in "${NODE_PARITY_IDS[@]}"; do
    scenario_id="${scenario_id// /}"
    if [[ -z "$scenario_id" ]]; then
      continue
    fi
    scenario_path="$ROOT_DIR/scenarios/baseline/$scenario_id.yaml"
    if [[ ! -f "$scenario_path" ]]; then
      echo "Missing scenario manifest for node parity: $scenario_path" >&2
      exit 1
    fi
    RUN_ID="${RUN_ID}-node" CONFIG_PATH="$CONFIG_PATH" "$ROOT_DIR/scripts/run_node_scenario.sh" "$scenario_path" "$NODE_PARITY_RUN_DIR"
  done
  "$PYTHON_BIN" -m evaluation.node_parity_compare "$RUN_DIR" "$NODE_PARITY_RUN_DIR" --scenarios "${NODE_PARITY_IDS[@]}" --output-dir "$RUN_DIR"
  NODE_PARITY_RESULT="$("$PYTHON_BIN" - <<'PY' "$RUN_DIR/node_parity_results.json"
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload.get("overall_result", "FAIL"))
PY
)"
  if [[ "$NODE_PARITY_RESULT" != "PASS" ]]; then
    echo "Node parity result is $NODE_PARITY_RESULT" >&2
    NODE_PARITY_EXIT=1
  fi
fi

if [[ "$ENABLE_ROS2_LAUNCH_PROBE" == "true" ]]; then
  mkdir -p "$ROS2_LAUNCH_RUN_DIR"
  IFS=',' read -r -a ROS2_LAUNCH_IDS <<< "$ROS2_LAUNCH_SCENARIOS"
  echo "Running ROS2 launch probe into $ROS2_LAUNCH_RUN_DIR (backend=$ROS2_LAUNCH_BACKEND)"
  for scenario_id in "${ROS2_LAUNCH_IDS[@]}"; do
    scenario_id="${scenario_id// /}"
    if [[ -z "$scenario_id" ]]; then
      continue
    fi
    scenario_path="$ROOT_DIR/scenarios/baseline/$scenario_id.yaml"
    if [[ ! -f "$scenario_path" ]]; then
      echo "Missing scenario manifest for ROS2 launch probe: $scenario_path" >&2
      exit 1
    fi
    RUN_ID="${RUN_ID}-launch" CONFIG_PATH="$CONFIG_PATH" ROS2_LAUNCH_BACKEND="$ROS2_LAUNCH_BACKEND" "$ROOT_DIR/scripts/run_ros2_launch_scenario.sh" "$scenario_path" "$ROS2_LAUNCH_RUN_DIR"
  done
  "$PYTHON_BIN" -m evaluation.ros2_launch_probe_compare "$RUN_DIR" "$ROS2_LAUNCH_RUN_DIR" --scenarios "${ROS2_LAUNCH_IDS[@]}" --output-dir "$RUN_DIR"
  ROS2_LAUNCH_RESULT="$("$PYTHON_BIN" - <<'PY' "$RUN_DIR/ros2_launch_probe_results.json"
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload.get("overall_result", "FAIL"))
PY
)"
  if [[ "$ROS2_LAUNCH_RESULT" != "PASS" ]]; then
    echo "ROS2 launch probe result is $ROS2_LAUNCH_RESULT" >&2
    ROS2_LAUNCH_EXIT=1
  fi
fi

if [[ "$ENABLE_ROS2_VERIFICATION_PROBE" == "true" ]]; then
  mkdir -p "$ROS2_VERIFICATION_RUN_DIR"
  IFS=',' read -r -a ROS2_VERIFICATION_IDS <<< "$ROS2_VERIFICATION_SCENARIOS"
  echo "Running ROS2 verification probe into $ROS2_VERIFICATION_RUN_DIR (backend=$ROS2_LAUNCH_BACKEND)"
  for scenario_id in "${ROS2_VERIFICATION_IDS[@]}"; do
    scenario_id="${scenario_id// /}"
    if [[ -z "$scenario_id" ]]; then
      continue
    fi
    scenario_path="$ROOT_DIR/scenarios/baseline/$scenario_id.yaml"
    if [[ ! -f "$scenario_path" ]]; then
      echo "Missing scenario manifest for ROS2 verification probe: $scenario_path" >&2
      exit 1
    fi
    RUN_ID="${RUN_ID}-verification" CONFIG_PATH="$CONFIG_PATH" EVAL_CONFIG_PATH="$EVAL_CONFIG_PATH" ENABLE_VERIFICATION_NODES=true ROS2_LAUNCH_BACKEND="$ROS2_LAUNCH_BACKEND" "$ROOT_DIR/scripts/run_ros2_launch_scenario.sh" "$scenario_path" "$ROS2_VERIFICATION_RUN_DIR"
  done
  "$PYTHON_BIN" -m evaluation.ros2_verification_probe_compare "$RUN_DIR" "$ROS2_VERIFICATION_RUN_DIR" --scenarios "${ROS2_VERIFICATION_IDS[@]}" --output-dir "$RUN_DIR"
  ROS2_VERIFICATION_RESULT="$("$PYTHON_BIN" - <<'PY' "$RUN_DIR/ros2_verification_probe_results.json"
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload.get("overall_result", "FAIL"))
PY
)"
  if [[ "$ROS2_VERIFICATION_RESULT" != "PASS" ]]; then
    echo "ROS2 verification probe result is $ROS2_VERIFICATION_RESULT" >&2
    ROS2_VERIFICATION_EXIT=1
  fi
fi

if [[ "$ENABLE_HEALTH_MONITOR_PROBE" == "true" ]]; then
  mkdir -p "$HEALTH_MONITOR_RUN_DIR"
  IFS=',' read -r -a HEALTH_MONITOR_IDS <<< "$HEALTH_MONITOR_SCENARIOS"
  echo "Running health monitor probe into $HEALTH_MONITOR_RUN_DIR (backend=$ROS2_LAUNCH_BACKEND)"
  for scenario_id in "${HEALTH_MONITOR_IDS[@]}"; do
    scenario_id="${scenario_id// /}"
    if [[ -z "$scenario_id" ]]; then
      continue
    fi
    scenario_path="$ROOT_DIR/scenarios/baseline/$scenario_id.yaml"
    if [[ ! -f "$scenario_path" ]]; then
      echo "Missing scenario manifest for health monitor probe: $scenario_path" >&2
      exit 1
    fi
    RUN_ID="${RUN_ID}-health" CONFIG_PATH="$CONFIG_PATH" ROS2_LAUNCH_BACKEND="$ROS2_LAUNCH_BACKEND" "$ROOT_DIR/scripts/run_ros2_launch_scenario.sh" "$scenario_path" "$HEALTH_MONITOR_RUN_DIR"
  done
  "$PYTHON_BIN" -m evaluation.health_monitor_probe_compare "$RUN_DIR" "$HEALTH_MONITOR_RUN_DIR" --scenarios "${HEALTH_MONITOR_IDS[@]}" --output-dir "$RUN_DIR"
  HEALTH_MONITOR_RESULT="$("$PYTHON_BIN" - <<'PY' "$RUN_DIR/health_monitor_probe_results.json"
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(payload.get("overall_result", "FAIL"))
PY
)"
  if [[ "$HEALTH_MONITOR_RESULT" != "PASS" ]]; then
    echo "Health monitor probe result is $HEALTH_MONITOR_RESULT" >&2
    HEALTH_MONITOR_EXIT=1
  fi
fi

set +e
"$PYTHON_BIN" -m evaluation.regression_compare "$RUN_DIR" --config "$CONFIG_PATH" --output "$RUN_DIR/regression_result.json"
REGRESSION_EXIT=$?
set -e

"$PYTHON_BIN" -m trust_engine.calibration "$RUN_DIR" --config "$CONFIG_PATH" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.ew_metrics "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.tactical_summary_bundle "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.replay_evaluation "$RUN_DIR" --config "$CONFIG_PATH" --eval-config "$EVAL_CONFIG_PATH" --regression-result "$RUN_DIR/regression_result.json"
"$PYTHON_BIN" -m evaluation.summary_report "$RUN_DIR" --regression-result "$RUN_DIR/regression_result.json"
CHECK_ENV=()
if [[ "$ENABLE_NODE_PARITY" == "true" ]]; then
  CHECK_ENV+=("REQUIRE_NODE_PARITY=true")
fi
if [[ "$ENABLE_ROS2_LAUNCH_PROBE" == "true" ]]; then
  CHECK_ENV+=("REQUIRE_ROS2_LAUNCH_PROBE=true")
fi
if [[ "$ENABLE_ROS2_VERIFICATION_PROBE" == "true" ]]; then
  CHECK_ENV+=("REQUIRE_ROS2_VERIFICATION_PROBE=true")
fi
if [[ "$ENABLE_HEALTH_MONITOR_PROBE" == "true" ]]; then
  CHECK_ENV+=("REQUIRE_HEALTH_MONITOR_PROBE=true")
fi
if [[ ${#CHECK_ENV[@]} -gt 0 ]]; then
  env "${CHECK_ENV[@]}" "$ROOT_DIR/scripts/check_artifacts.sh" "$RUN_DIR"
else
  "$ROOT_DIR/scripts/check_artifacts.sh" "$RUN_DIR"
fi

echo
cat "$RUN_DIR/summary.md"
echo
echo "Artifacts stored in $RUN_DIR"

if [[ "$REGRESSION_EXIT" -ne 0 || "$NODE_PARITY_EXIT" -ne 0 || "$ROS2_LAUNCH_EXIT" -ne 0 || "$ROS2_VERIFICATION_EXIT" -ne 0 || "$HEALTH_MONITOR_EXIT" -ne 0 ]]; then
  exit 1
fi
exit 0
