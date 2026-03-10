# Acceptance Criteria

## Purpose

Acceptance criteria define the validation conditions for JamShield Recon-X Sim simulation runs.

They are used to verify whether a deterministic run satisfies required mission behavior, localization performance, trust behavior, and replay integrity under controlled scenario conditions.

## Terminology Alignment

This file follows `docs/architecture/terminology-lock.md` as the authoritative terminology source.

- Mission states must use only the locked mission-state names.
- Localization modes must use only the locked localization-mode names.
- Trust behavior must use the locked trust-signal names.
- Scenario categories must remain separate from mission states and localization modes.

## Mission-Level Acceptance Criteria

Mission-level acceptance evaluates deterministic mission continuity behavior.

### Accepted mission states

- `MISSION_PREPARE`
- `MISSION_EXECUTE`
- `MISSION_DEGRADED`
- `MISSION_FALLBACK`
- `MISSION_SAFE_HOLD`
- `MISSION_ABORT`
- `MISSION_COMPLETE`

### Mission behavior requirements

- Mission state transitions must be deterministic under deterministic replay.
- Mission continuity decisions must be explainable from recorded runtime outputs.
- A nominal mission must progress from `MISSION_PREPARE` to `MISSION_EXECUTE` and then to `MISSION_COMPLETE`.
- `MISSION_DEGRADED` is acceptable when GNSS quality degrades but mission continuity remains controlled.
- `MISSION_FALLBACK` is acceptable when fallback localization is required and valid.
- `MISSION_SAFE_HOLD` is acceptable when localization continuity is temporarily insufficient for forward progress.
- `MISSION_ABORT` is acceptable only when scenario conditions justify terminal mission failure.

## Localization Acceptance Criteria

Localization acceptance evaluates runtime localization performance and localization-mode behavior.

### Accepted localization modes

- `GNSS_PRIMARY`
- `BLENDED`
- `VIO_PRIMARY`
- `HOLD_LAST_SAFE`

### Localization behavior requirements

- `GNSS_PRIMARY` is expected during nominal GNSS conditions.
- `BLENDED` is acceptable when GNSS and VIO both remain valid for confidence-aware localization.
- `VIO_PRIMARY` is required when GNSS trust collapses and VIO remains the valid localization basis.
- `HOLD_LAST_SAFE` is acceptable only as a temporary continuity-preservation mode when active sources do not satisfy minimum confidence requirements.

### Localization metrics

- `ATE`
- `RPE`
- `drift`
- `localization_continuity`
- `fallback_reaction_time`

### Initial simulation-phase thresholds

| Acceptance profile | ATE | RPE | drift | localization_continuity | fallback_reaction_time |
| --- | --- | --- | --- | --- | --- |
| `baseline_nominal_profile_v1` | `<= 1.5 m` | `<= 0.6 m` | `<= 0.5 %` | `>= 99.5 %` | `<= 2.0 s` if triggered |
| `urban_canyon_profile_v1` | `<= 4.0 m` | `<= 1.5 m` | `<= 1.5 %` | `>= 98.0 %` | `<= 2.0 s` if triggered |
| `denial_corridor_profile_v1` | `<= 7.0 m` | `<= 2.5 m` | `<= 3.0 %` | `>= 97.0 %` | `<= 1.5 s` |
| `spoof_like_drift_profile_v1` | `<= 6.0 m` | `<= 2.0 m` | `<= 2.0 %` | `>= 97.5 %` | `<= 1.0 s` |
| `comms_instability_profile_v1` | `<= 8.0 m` | `<= 3.0 m` | `<= 4.0 %` | `>= 95.0 %` | `<= 2.5 s` |

## Trust Evaluation Criteria

Trust evaluation verifies whether trust signals respond correctly to runtime degradation.

### Required trust signals

- `gnss_trust`
- `vio_trust`
- `sync_quality`
- `localization_confidence`
- `mission_confidence`

### Trust behavior requirements

- `gnss_trust` must decrease when GNSS anomalies occur.
- `vio_trust` must reflect visual tracking quality and decrease when VIO quality degrades.
- `sync_quality` must decrease when timing alignment or message freshness degrades.
- `localization_confidence` must decrease when fused localization quality or continuity degrades.
- `mission_confidence` must decrease when both localization sources degrade or when the system approaches `MISSION_SAFE_HOLD` or `MISSION_ABORT`.

## Scenario Validation

Scenario validation checks whether the system responds correctly to controlled scenario categories. Scenario categories are not mission states and are not localization modes.

### Nominal mission

- Scenario condition: nominal route execution with no induced GNSS degradation
- Expected mission behavior: `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_COMPLETE`
- Expected localization behavior: remain primarily in `GNSS_PRIMARY`

### GNSS degraded corridor

- Scenario condition: `gnss_degraded_corridor`
- Expected mission behavior: controlled entry into `MISSION_DEGRADED` and recovery to `MISSION_EXECUTE`
- Expected localization behavior: transition from `GNSS_PRIMARY` to `BLENDED` may occur

### GNSS denied zone

- Scenario condition: `gnss_denied_zone`
- Expected mission behavior: controlled entry into `MISSION_FALLBACK`
- Expected localization behavior: transition away from GNSS-led localization and into `VIO_PRIMARY`

### Spoof-like drift

- Scenario condition: `spoof_like_drift`
- Expected mission behavior: controlled degraded or fallback behavior without uncontrolled oscillation
- Expected localization behavior: transition away from purely GNSS-led localization when trust degrades

### Communication degradation

- Scenario condition: degraded timing or message freshness
- Expected mission behavior: controlled degraded behavior, safe hold, or justified abort
- Expected localization behavior: reduction in `sync_quality` and `localization_confidence`

## Provisional Thresholds

All numeric thresholds in this file are initial simulation-phase thresholds.

- They are intended for simulation-first verification.
- They are not hardware validation claims.
- They may be recalibrated during the Future hardware integration phase.
- Threshold changes must preserve deterministic evaluation and terminology consistency.

## Invalid Run Conditions

A run is invalid if any of the following occur:

- runtime nodes consume `/truth/*`
- evaluation-only ground truth is missing, truncated, or time-misaligned
- required sensor streams are missing without scenario justification
- time synchronization failure prevents valid runtime evaluation
- telemetry logs are incomplete or corrupted
- deterministic replay diverges from recorded runtime outputs
- scenario identity or configuration identity does not match the evaluated artifacts

## Evaluation Discipline

Every evaluated run must record:

- `scenario_id`
- `configuration_id`
- `software_revision`
- `evaluation_metrics`

Evaluation discipline rules:

- evaluation uses evaluation-only ground truth
- runtime autonomy remains independent from evaluation-only ground truth
- mission behavior, localization behavior, and trust behavior are evaluated separately
- acceptance conclusions must be reproducible under deterministic replay
