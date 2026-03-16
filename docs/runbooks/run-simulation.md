# Run Simulation

## Purpose

This runbook describes the current executable-slice workflow for a deterministic scenario run.

## Inputs

- Python environment with `PYTHONPATH=src`
- selected baseline scenario manifest
- simulation config file
- writable output directory under `artifacts/runs/`

## Canonical Command Contract

Run one scenario:

```bash
bash scripts/run_scenario.sh scenarios/baseline/<scenario>.yaml artifacts/runs/<run_id>
```

Run full baseline regression:

```bash
bash scripts/run_regression.sh <run_id>
```

Run full baseline regression with Phase 12 node parity gate:

```bash
ENABLE_NODE_PARITY=true bash scripts/run_regression.sh <run_id>
```

Run full baseline regression with Phase 12 ROS2 launch probe gate:

```bash
ENABLE_ROS2_LAUNCH_PROBE=true ROS2_LAUNCH_SCENARIOS=s1_nominal,s3_gnss_denied_zone bash scripts/run_regression.sh <run_id>
```

Run full baseline regression with Phase 12 ROS2 launch probe gate through the `colcon` backend:

```bash
ENABLE_ROS2_LAUNCH_PROBE=true ROS2_LAUNCH_BACKEND=colcon ROS2_LAUNCH_SCENARIOS=s1_nominal,s3_gnss_denied_zone bash scripts/run_regression.sh <run_id>
```

Run full baseline regression with Phase 12 ROS2 verification-node gate:

```bash
ENABLE_ROS2_LAUNCH_PROBE=true ENABLE_ROS2_VERIFICATION_PROBE=true ROS2_VERIFICATION_SCENARIOS=s1_nominal,s3_gnss_denied_zone bash scripts/run_regression.sh <run_id>
```

Run full baseline regression with Phase 12 health-monitor gate:

```bash
ENABLE_HEALTH_MONITOR_PROBE=true HEALTH_MONITOR_SCENARIOS=s1_nominal,s13_sync_low_nominal bash scripts/run_regression.sh <run_id>
```

Run one scenario through the Phase 12 node-oriented loop:

```bash
bash scripts/run_node_scenario.sh scenarios/baseline/<scenario>.yaml artifacts/runs/<run_id>
```

Run one scenario through the Phase 12 ROS2 launch-wired probe:

```bash
bash scripts/run_ros2_launch_scenario.sh scenarios/baseline/<scenario>.yaml artifacts/runs/<run_id>
```

Run one scenario through the Phase 12 ROS2 launch-wired probe via `colcon` package launch:

```bash
ROS2_LAUNCH_BACKEND=colcon bash scripts/run_ros2_launch_scenario.sh scenarios/baseline/<scenario>.yaml artifacts/runs/<run_id>
```

Run one scenario through the Phase 12 ROS2 launch-wired probe with verification nodes enabled:

```bash
ENABLE_VERIFICATION_NODES=true bash scripts/run_ros2_launch_scenario.sh scenarios/baseline/<scenario>.yaml artifacts/runs/<run_id>
```

Run Phase 12 parity probe (defaults to `s1_nominal` and `s3_gnss_denied_zone`):

```bash
bash scripts/run_node_parity.sh artifacts/runs/<baseline_run_id> artifacts/runs/<node_run_id>
```

Current-slice note:

- The executable flow is file-based.
- Phase 12 adds a node-oriented in-process runtime probe for parity checks.
- Phase 12 adds a ROS2 launch-wired probe that emits `ros2_launch_plan.json/.md`.
- `scripts/run_ros2_launch_scenario.sh` defaults to `ROS2_LAUNCH_BACKEND=repo_wrapper` and supports `ROS2_LAUNCH_BACKEND=colcon` when ROS2 workspace/package setup is available.
- Phase 12 verification-node hybrid bridge can be enabled with `ENABLE_VERIFICATION_NODES=true`.
- Phase 12 health-monitor publication emits `<scenario>_mission_health.json` and `<scenario>_fault_events.json`.

## Execution Procedure

1. Select a single scenario manifest and record its hash.
2. Ensure the output directory is empty or versioned by `run_id`.
3. Run `scripts/run_scenario.sh` for a single scenario or `scripts/run_regression.sh` for `s1-s20`.
4. Confirm per-scenario artifacts are emitted:
   - `*_report.json`
   - `*_runtime_trace.json`
   - `*_truth_trace.json`
   - `*_mission_audit.json`
   - `*_ew_risk_map.json`
   - `*_tactical_summary.json`
5. Confirm mission states remain in the current executable set:
   - `MISSION_EXECUTE`
   - `MISSION_DEGRADED`
   - `MISSION_FALLBACK`
   - `MISSION_SAFE_HOLD`
   - `MISSION_ABORT`
6. Run artifact validation when needed:
   - `bash scripts/check_artifacts.sh artifacts/runs/<run_id>`
7. For parity probes, run `scripts/run_node_parity.sh` against a known-good baseline run.
8. Confirm `node_parity_results.json/.md/.csv` exists in the node run directory.
9. For launch-wired probe runs, confirm `ros2_launch_plan.json/.md` exists in the run directory.
10. If launch probe gate is enabled in regression, confirm `ros2_launch_probe_results.json/.md/.csv` exists in the run directory.
11. If verification probe gate is enabled in regression, confirm `ros2_verification_probe_results.json/.md/.csv` exists in the run directory.
12. If health-monitor gate is enabled in regression, confirm `health_monitor_probe_results.json/.md/.csv` exists in the run directory.
13. If single-scenario launch probe runs with verification enabled, confirm `<scenario>_verification_node_results.json` exists in the run directory.
14. Confirm health-monitor scenario artifacts exist for node/launch probe runs:
   - `<scenario>_mission_health.json`
   - `<scenario>_fault_events.json`
15. If `ROS2_LAUNCH_BACKEND=colcon` is used, ensure ROS2 workspace was built and sourced before execution.

## Required Runtime Checks

- scenario report includes `manifest_hash`, `config_hash`, and `evaluation_profile`
- replay/evaluation bundles are present for regression runs
- reason codes in reports remain `snake_case`
- `/truth/*` stays evaluation-only and is not used as runtime autonomy input

## Expected Outputs

- scenario artifacts listed above for each scenario
- run-level bundles on regression runs:
  - `replay_results.json/.md/.csv`
  - `evaluation_metrics.json/.md/.csv`
  - `evaluation_verdicts.json/.md/.csv`
  - `summary.json/.md`
  - `regression_result.json`
- launch-wired probe bundle on launch runs:
  - `ros2_launch_plan.json/.md`
- launch probe comparison bundle on gated regression runs:
  - `ros2_launch_probe_results.json/.md/.csv`
- verification probe comparison bundle on gated regression runs:
  - `ros2_verification_probe_results.json/.md/.csv`
- health-monitor probe comparison bundle on gated regression runs:
  - `health_monitor_probe_results.json/.md/.csv`

## Immediate Triage Rules

Stop the run and mark it suspect if:

- any required scenario artifact is missing
- report uses legacy mission/localization values outside the current executable set
- deterministic replay for a scenario is not `PASS` in `replay_results.json`
- `scripts/check_artifacts.sh` fails for the run directory
