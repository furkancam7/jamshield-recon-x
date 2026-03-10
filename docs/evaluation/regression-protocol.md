# Regression Protocol

## Purpose

The regression protocol ensures that code changes preserve deterministic replay, mission continuity behavior, and scenario acceptance performance.

## Required Inputs

- canonical scenario manifest
- fixed simulator build or version identifier
- fixed autonomy configuration
- clean output directory for logs and evaluation artifacts

## Regression Sequence

1. Build the workspace and record the build identifier.
2. Run each baseline scenario manifest once and record all required topics.
3. Replay the recorded run through `evaluation_node`.
4. Compare replayed runtime outputs against the original run for deterministic equality.
5. Compute evaluation metrics.
6. Compare results to scenario acceptance thresholds.
7. Persist verdicts, metric artifacts, and manifest hashes.

## Determinism Checks

The following artifacts must match between original run and replay:

- mission state sequence
- mission action sequence
- trust decision sequence
- fused localization hash after timestamp normalization
- scenario event lifecycle sequence

If any of these differ, mark the run `INVALID` with `EVAL_INVALID_REPLAY_DIVERGENCE`.

## Baseline Regression Set

The minimum regression set is:

- `baseline_nominal_v1`
- `urban_canyon_degradation_v1`
- `denial_corridor_v1`
- `spoof_like_drift_recovery_v1`
- `comms_loss_with_gnss_instability_v1`

## Change Classification

### Mandatory full regression

Run the full baseline regression set when a change touches:

- localization logic
- trust logic
- mission continuity logic
- timing or logging behavior
- scenario event scheduling

### Targeted regression allowed

Targeted regression is acceptable for:

- operator station presentation changes
- documentation-only changes
- non-runtime evaluation report formatting

Even in targeted mode, `baseline_nominal_v1` must still pass deterministic replay.

## Failure Handling

If a regression fails:

1. classify the failure as `FAIL` or `INVALID`
2. identify first divergence timestamp
3. extract associated reason codes and scenario events
4. re-run the same manifest with the same seed once to confirm repeatability
5. do not relax thresholds without an ADR or explicit requirement change

## Output Artifacts

Each regression run must produce:

- recorded log bundle
- manifest copy or manifest hash
- deterministic replay report
- metric report
- final verdict

Artifact retention policy is repository or CI specific and may be expanded as a Future system extension.
