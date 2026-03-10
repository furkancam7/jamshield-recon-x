# Baseline Scenarios

## Purpose

These baseline scenarios define the minimum scenario set for architecture validation, acceptance testing, and deterministic regression.

## Scenario Set

### `baseline_nominal_v1`

- Intent: validate nominal end-to-end operation without induced degradation
- Environment: open sky route
- Events: none
- Expected mission path: `PREPARE -> GNSS_PRIMARY -> MISSION_COMPLETE`
- Acceptance profile: `baseline_nominal_profile_v1`

### `urban_canyon_degradation_v1`

- Intent: verify degraded GNSS handling without full denial
- Environment: dense urban corridor
- Events:
  - `gnss_degradation_zone`
  - `sensor_noise_override` on camera with bounded increase
- Expected mission path: `PREPARE -> GNSS_PRIMARY -> GNSS_DEGRADED -> GNSS_PRIMARY -> MISSION_COMPLETE`
- Acceptance profile: `urban_canyon_profile_v1`

### `denial_corridor_v1`

- Intent: verify deterministic fallback to VIO through a GNSS denial zone
- Environment: industrial corridor
- Events:
  - `gnss_denial_zone`
- Expected mission path: `PREPARE -> GNSS_PRIMARY -> VIO_PRIMARY -> GNSS_PRIMARY or MISSION_COMPLETE`
- Acceptance profile: `denial_corridor_profile_v1`

### `spoof_like_drift_recovery_v1`

- Intent: verify spoof-like bias detection and GNSS rejection while preserving mission continuity
- Environment: semi-open route with stable visual texture
- Events:
  - `gnss_spoof_like_drift`
- Expected mission path: `PREPARE -> GNSS_PRIMARY -> VIO_PRIMARY -> GNSS_PRIMARY or MISSION_COMPLETE`
- Acceptance profile: `spoof_like_drift_profile_v1`

### `comms_loss_with_gnss_instability_v1`

- Intent: verify health supervision under communication degradation combined with weak GNSS
- Environment: mixed terrain route
- Events:
  - `gnss_degradation_zone`
  - `communication_degradation`
- Expected mission path: `PREPARE -> GNSS_PRIMARY -> GNSS_DEGRADED -> LOCALIZATION_CONTINGENCY -> VIO_PRIMARY or MISSION_ABORT`
- Acceptance profile: `comms_instability_profile_v1`

## Baseline Rules

- Each baseline scenario must have exactly one canonical manifest.
- Acceptance thresholds are scenario-specific and defined in `../evaluation/acceptance-criteria.md`.
- Regression runs use baseline scenarios before any expanded scenario library.
- New scenarios may be added as a Future system extension, but baseline identifiers must remain stable for CI history.
