# Regression Protocol

## Purpose

The regression protocol ensures that code changes preserve deterministic replay, mission continuity behavior, and scenario acceptance performance.

## Required Inputs

- canonical scenario manifest
- fixed simulator build or version identifier
- fixed autonomy configuration
- clean output directory for logs and evaluation artifacts
- named evaluation profile configuration (`configs/eval/default.yaml`)

## Regression Sequence

1. Build the workspace and record the build identifier.
2. Run each baseline scenario manifest once and record all required topics.
3. Replay the recorded run through the current file-based replay harness.
4. Compare replayed runtime outputs against the original run for deterministic equality.
5. Compute evaluation metrics.
6. Compare results to scenario acceptance thresholds.
7. Persist verdicts, metric artifacts, and manifest hashes.

## Determinism Checks

The following artifacts must match between original run and replay:

- runtime trace tick sequence (`*_runtime_trace.json`)
- mission audit sequence (`*_mission_audit.json`)
- report payload excluding run-specific fields
- EW risk-map `risk_cells_hash`
- tactical summary `primary_reason_code`, `advisory_code`, and `summary_text`

If any of these differ, mark the run `INVALID` with `deterministic_replay_failed`.

## Baseline Regression Set

The current baseline regression set is `s1-s20` under `scenarios/baseline/`.

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

Even in targeted mode, `s1_nominal` must still pass deterministic replay.

## Failure Handling

If a regression fails:

1. classify the failure as `FAIL` or `INVALID`
2. identify first divergence timestamp
3. extract associated reason codes and scenario events
4. re-run the same manifest with the same seed once to confirm repeatability
5. do not relax thresholds without an ADR or explicit requirement change

Current-slice verdict policy:

- replay divergence -> `INVALID`
- required profile/artifact/hash mismatch -> `INVALID`
- replay valid but threshold exceeded -> `FAIL`
- all checks passed -> `PASS`

## Output Artifacts

Each regression run must produce:

- current-slice runtime trace bundle
- current-slice pseudo-truth trace bundle
- manifest copy or manifest hash
- deterministic replay report
- scenario report set
- mission audit set
- EW risk-map set
- EW metrics bundle
- evaluation metrics bundle
- evaluation verdicts bundle
- summary report
- trust calibration bundle
- final verdict

Artifact retention policy is repository or CI specific and may be expanded as a Future system extension.
