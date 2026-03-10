# Acceptance Criteria

## General Rules

- Thresholds are scenario-specific.
- All thresholds apply to fused runtime outputs, not post-processed trajectories.
- Evaluation-only ground truth is required for all benchmarked scenarios.
- A run is `INVALID` if invalid-run conditions are met, regardless of metric values.

## Scenario Acceptance Profiles

| Acceptance Profile | ATE_RMSE_M | RPE_RMSE_M | DRIFT_PCT | LOCALIZATION_CONTINUITY_PCT | FALLBACK_REACTION_TIME_S | Mission Success |
| --- | --- | --- | --- | --- | --- | --- |
| `baseline_nominal_profile_v1` | `<= 1.5` | `<= 0.6` | `<= 0.5` | `>= 99.5` | `<= 2.0` if triggered | required |
| `urban_canyon_profile_v1` | `<= 4.0` | `<= 1.5` | `<= 1.5` | `>= 98.0` | `<= 2.0` if triggered | required |
| `denial_corridor_profile_v1` | `<= 7.0` | `<= 2.5` | `<= 3.0` | `>= 97.0` | `<= 1.5` | required |
| `spoof_like_drift_profile_v1` | `<= 6.0` | `<= 2.0` | `<= 2.0` | `>= 97.5` | `<= 1.0` | required |
| `comms_instability_profile_v1` | `<= 8.0` | `<= 3.0` | `<= 4.0` | `>= 95.0` | `<= 2.5` | required unless scenario explicitly expects abort |

## Scenario-Specific Notes

### `baseline_nominal_v1`

- `FALLBACK_REACTION_TIME_S` is informational unless a fault unexpectedly triggers fallback.
- Any transition to `LOCALIZATION_CONTINGENCY` is a failure.

### `urban_canyon_degradation_v1`

- Temporary `GNSS_DEGRADED` is expected.
- Transition to `MISSION_ABORT` is a failure.

### `denial_corridor_v1`

- Entry into `VIO_PRIMARY` is required.
- Remaining in `GNSS_PRIMARY` through the full denial interval is a failure unless GNSS denial event did not activate due to manifest error, which makes the run invalid.

### `spoof_like_drift_recovery_v1`

- `GNSS_SPOOF_LIKE_DRIFT` must appear in the trust logs before GNSS recovery is allowed.
- False recovery to `GNSS_PRIMARY` during active drift is a failure.

### `comms_loss_with_gnss_instability_v1`

- `MISSION_ABORT` is acceptable only if the manifest labels the scenario as abort-expected.
- If abort is not expected, continuity and mission success thresholds apply normally.

## Invalid Run Conditions

A run is invalid if any of the following occur:

- `/truth/pose` is missing, truncated, or time-misaligned
- the manifest hash in the log does not match the evaluated scenario manifest
- deterministic replay diverges in mission state sequence, trust decision sequence, or fused localization hash
- recorded sensor topics are incomplete for more than `5.0 s` before any injected fault justifies the loss
- the simulator seed or clock rate differs from the manifest
- bag or artifact corruption prevents full metric computation

## Verdict Rules

- `PASS`: all required metrics pass and no invalid-run condition occurs
- `FAIL`: at least one required metric fails and no invalid-run condition occurs
- `INVALID`: any invalid-run condition occurs
