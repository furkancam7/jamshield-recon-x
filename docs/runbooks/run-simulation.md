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

Current-slice note:

- The executable flow is file-based.
- ROS2 launch wrappers and node-orchestrated runtime remain Phase 12 migration work.

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

## Immediate Triage Rules

Stop the run and mark it suspect if:

- any required scenario artifact is missing
- report uses legacy mission/localization values outside the current executable set
- deterministic replay for a scenario is not `PASS` in `replay_results.json`
- `scripts/check_artifacts.sh` fails for the run directory
