#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LAUNCH_FILE="${ROOT_DIR}/launch/runtime_probe.launch.py"
PACKAGE_NAME="jamshield_recon_x_sim"
COLCON_LAUNCH_FILE="runtime_probe_colcon.launch.py"
ROS2_LAUNCH_BACKEND="${ROS2_LAUNCH_BACKEND:-repo_wrapper}"

SCENARIO_PATH="${1:?usage: run_ros2_launch_scenario.sh <scenario_yaml> [output_dir]}"
OUTPUT_DIR="${2:-$ROOT_DIR/artifacts}"
VIO_HEALTHY="${VIO_HEALTHY:-true}"
VIO_STATE="${VIO_STATE:-}"
VIO_HEALTH_SCORE="${VIO_HEALTH_SCORE:-}"
CONFIG_PATH="${CONFIG_PATH:-$ROOT_DIR/configs/sim/default.yaml}"
CONFIG_OVERRIDE="${CONFIG_OVERRIDE:-}"
RUN_ID="${RUN_ID:-$(basename "$OUTPUT_DIR")}"
ENABLE_VERIFICATION_NODES="${ENABLE_VERIFICATION_NODES:-false}"

export PYTHONPATH="$ROOT_DIR/src${PYTHONPATH:+:$PYTHONPATH}"

case "$ROS2_LAUNCH_BACKEND" in
  repo_wrapper|colcon)
    ;;
  *)
    echo "Unsupported ROS2_LAUNCH_BACKEND: $ROS2_LAUNCH_BACKEND (expected repo_wrapper|colcon)" >&2
    exit 1
    ;;
esac

if [[ "$ROS2_LAUNCH_BACKEND" == "repo_wrapper" ]]; then
  if [[ ! -f "$LAUNCH_FILE" ]]; then
    echo "Missing launch file: $LAUNCH_FILE" >&2
    exit 1
  fi

  ARGS=(
    "$LAUNCH_FILE"
    "$SCENARIO_PATH"
    --output-dir "$OUTPUT_DIR"
    --config "$CONFIG_PATH"
    --run-id "$RUN_ID"
  )

  if [[ "$ENABLE_VERIFICATION_NODES" == "true" ]]; then
    ARGS+=(--enable-verification-nodes)
  fi

  if [[ -n "$CONFIG_OVERRIDE" ]]; then
    ARGS+=(--config-override "$CONFIG_OVERRIDE")
  fi

  if [[ "$VIO_HEALTHY" == "false" ]]; then
    ARGS+=(--vio-unhealthy)
  else
    if [[ -n "$VIO_STATE" ]]; then
      ARGS+=(--vio-state "$VIO_STATE")
    fi
    if [[ -n "$VIO_HEALTH_SCORE" ]]; then
      ARGS+=(--vio-health-score "$VIO_HEALTH_SCORE")
    fi
  fi

  "$PYTHON_BIN" "${ARGS[@]}"
  exit 0
fi

if [[ -n "$CONFIG_OVERRIDE" ]]; then
  echo "CONFIG_OVERRIDE is not supported when ROS2_LAUNCH_BACKEND=colcon." >&2
  exit 1
fi
if ! command -v ros2 >/dev/null 2>&1; then
  echo "ros2 CLI not found. Install/source ROS2 and workspace before using ROS2_LAUNCH_BACKEND=colcon." >&2
  exit 1
fi
if ! ros2 pkg prefix "$PACKAGE_NAME" >/dev/null 2>&1; then
  echo "ROS2 package '$PACKAGE_NAME' not found. Run colcon build and source install/setup.bash." >&2
  exit 1
fi

ROS_ARGS=(
  launch
  "$PACKAGE_NAME"
  "$COLCON_LAUNCH_FILE"
  "scenario_path:=$SCENARIO_PATH"
  "output_dir:=$OUTPUT_DIR"
  "config_path:=$CONFIG_PATH"
  "run_id:=$RUN_ID"
  "enable_verification_nodes:=$ENABLE_VERIFICATION_NODES"
)

if [[ "$VIO_HEALTHY" == "false" ]]; then
  ROS_ARGS+=("vio_unhealthy:=true")
else
  if [[ -n "$VIO_STATE" ]]; then
    ROS_ARGS+=("vio_state:=$VIO_STATE")
  fi
  if [[ -n "$VIO_HEALTH_SCORE" ]]; then
    ROS_ARGS+=("vio_health_score:=$VIO_HEALTH_SCORE")
  fi
fi

ros2 "${ROS_ARGS[@]}"
