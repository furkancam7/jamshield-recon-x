# Evaluation Metrics

## Metric Scope

All metrics in this file are computed offline by `evaluation_node` using recorded runtime outputs and evaluation-only ground truth.

## Pose Alignment

Estimated and ground-truth trajectories must be aligned in the `map` frame using synchronized timestamps. Samples with missing truth or invalid fused localization are excluded and counted toward invalid-run checks.

## Absolute Trajectory Error

`ATE_RMSE_M` measures full-trajectory position accuracy:

`ATE_RMSE_M = sqrt((1 / N) * sum_i || p_est_i - p_truth_i ||^2)`

Where:

- `N` is the number of aligned valid samples
- `p_est_i` is fused position at sample `i`
- `p_truth_i` is evaluation-only ground truth position at sample `i`

## Relative Pose Error

`RPE_RMSE_M` measures short-horizon consistency over a fixed interval `delta`:

`RPE_RMSE_M = sqrt((1 / M) * sum_i || (p_est_{i+delta} - p_est_i) - (p_truth_{i+delta} - p_truth_i) ||^2 )`

Default evaluation interval:

- `delta = 1.0 s`

## Drift

`DRIFT_PCT` measures accumulated position drift relative to path length:

`DRIFT_PCT = 100 * terminal_position_error_m / total_distance_traveled_m`

This metric is especially relevant in `VIO_PRIMARY` segments and denial scenarios.

## Localization Continuity

`LOCALIZATION_CONTINUITY_PCT` measures the percentage of mission time with a valid fused estimate and no gap larger than the continuity limit:

`LOCALIZATION_CONTINUITY_PCT = 100 * valid_localized_time_s / mission_time_s`

Continuity limit:

- a localization gap greater than `0.25 s` is a continuity break

## Fallback Reaction Time

`FALLBACK_REACTION_TIME_S` measures the time from first confirmed GNSS untrustworthy state to first valid `VIO_PRIMARY` mission state:

`FALLBACK_REACTION_TIME_S = t(first VIO_PRIMARY) - t(first GNSS denial or spoof confirmation)`

The trigger time uses `TrustDecision.primary_reason_code` and not evaluation-only ground truth.

## Mission Success

`MISSION_SUCCESS` is a boolean metric. It is true only if:

- all route waypoints are completed in order
- the run does not enter `MISSION_ABORT`
- localization continuity remains above the scenario threshold
- deterministic replay passes

## Supplemental Metrics

The following metrics are recommended for debugging but are not primary acceptance gates unless a scenario profile explicitly promotes them:

- max localization gap
- time spent in `LOCALIZATION_CONTINGENCY`
- false GNSS rejection count
- false GNSS recovery count

## Metric Reporting Rules

- Every metric report must include the threshold used for pass or fail.
- Metrics must be emitted on `/evaluation/metrics`.
- Units must remain stable across releases.
