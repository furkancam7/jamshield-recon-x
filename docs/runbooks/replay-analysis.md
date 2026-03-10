# Replay Analysis

## Purpose

This runbook defines the deterministic replay and offline evaluation workflow.

## Inputs

- recorded run directory
- original scenario manifest
- replay-capable workspace

## Canonical Command Contract

The repository should expose an entry point equivalent to:

```bash
ros2 launch jamshield_recon_x_sim replay.launch.py \
  run_dir:=<run_dir> \
  scenario_manifest:=<manifest_path>
```

If the wrapper is absent, invoke the equivalent replay harness and `evaluation_node` manually.

## Replay Procedure

1. Load the original scenario manifest and verify its hash against run metadata.
2. Reconstruct the runtime event stream from the recorded log bundle.
3. Re-run the autonomy path with identical parameters and deterministic ordering.
4. Compare mission states, trust decisions, and fused localization hashes against the original run.
5. Compute evaluation metrics against `/truth/pose`.
6. Emit `/evaluation/run_metadata`, `/evaluation/metrics`, and `/evaluation/verdict`.

## Required Checks

- replay uses the same seed-independent runtime configuration as the original run
- scenario event ordering matches exactly
- no evaluation metric is computed before deterministic replay comparison completes
- verdict classification follows `PASS`, `FAIL`, or `INVALID` rules only

## Metrics Extraction

At minimum, extract:

- `ATE_RMSE_M`
- `RPE_RMSE_M`
- `DRIFT_PCT`
- `LOCALIZATION_CONTINUITY_PCT`
- `FALLBACK_REACTION_TIME_S`
- `MISSION_SUCCESS`

## Investigation Output

For any non-pass verdict, preserve:

- first divergence timestamp
- first failed threshold
- associated reason codes
- mission state timeline
- trust decision timeline

These artifacts are required for regression triage.
