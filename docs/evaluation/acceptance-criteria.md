# Acceptance Criteria

## Purpose

Acceptance criteria define the minimum conditions under which a simulation run is considered behaviorally valid for JamShield Recon-X Sim.

These criteria are used to verify system behavior under controlled scenario conditions. They evaluate deterministic mission continuity, localization performance, trust behavior, and replay integrity against scenario-specific expectations.

## Terminology Alignment

This file follows `docs/architecture/terminology-lock.md` as the authoritative terminology source.

- Mission states must use the locked mission-state names.
- Localization modes must use the locked localization-mode names.
- Scenario conditions and scenario events must remain separate from mission states and localization modes.
- Evaluation-only ground truth must remain isolated from runtime autonomy.

## Mission-Level Acceptance Criteria

Mission-level acceptance evaluates whether mission continuity remained deterministic, explainable, and appropriate for the scenario conditions.

### Accepted mission states

The only mission states used for acceptance are:

- `MISSION_PREPARE`
- `MISSION_EXECUTE`
- `MISSION_DEGRADED`
- `MISSION_FALLBACK`
- `MISSION_SAFE_HOLD`
- `MISSION_ABORT`
- `MISSION_COMPLETE`

### Mission behavior requirements

- Mission state transitions must be deterministic under deterministic replay.
- Mission state outputs must be explainable from runtime evidence and recorded reason codes.
- A nominal mission must progress from `MISSION_PREPARE` to `MISSION_EXECUTE` and then to `MISSION_COMPLETE` without entering `MISSION_ABORT`.
- Under degraded GNSS conditions, the system may enter `MISSION_DEGRADED` while maintaining mission continuity.
- When fallback localization becomes necessary and valid, the system may enter `MISSION_FALLBACK`.
- If localization continuity becomes insufficient, the system may enter `MISSION_SAFE_HOLD`.
- `MISSION_ABORT` is acceptable only when the scenario definition or acceptance profile explicitly allows terminal mission failure.

### Mission success requirements

A run satisfies mission-level success only if:

- route objectives are completed in order, unless the scenario explicitly allows abort
- mission continuity decisions remain deterministic
- no invalid-run condition occurs
- replay integrity is preserved

## Localization Acceptance Criteria

Localization acceptance evaluates fused localization behavior and mode transitions without redefining mission states.

### Accepted localization modes

The only localization modes used for acceptance are:

- `GNSS_PRIMARY`
- `BLENDED`
- `VIO_PRIMARY`
- `HOLD_LAST_SAFE`

### Localization behavior requirements

- `GNSS_PRIMARY` is expected during nominal GNSS conditions.
- `BLENDED` is acceptable when GNSS and VIO both remain valid and confidence-aware localization allows both sources.
- `VIO_PRIMARY` is required when GNSS trust collapses and VIO remains sufficiently reliable.
- `HOLD_LAST_SAFE` is acceptable only as a temporary continuity-preservation mode when no active source satisfies minimum confidence thresholds.

### Localization metrics

The primary localization metrics are:

- `ATE`
- `RPE`
- `drift`
- `localization_continuity`
- `fallback_reaction_time`

### Provisional metric profiles

| Acceptance profile | ATE | RPE | drift | localization_continuity | fallback_reaction_time | Mission success |
| --- | --- | --- | --- | --- | --- | --- |
| `baseline_nominal_profile_v1` | `<= 1.5 m` | `<= 0.6 m` | `<= 0.5 %` | `>= 99.5 %` | `<= 2.0 s` if triggered | required |
| `urban_canyon_profile_v1` | `<= 4.0 m` | `<= 1.5 m` | `<= 1.5 %` | `>= 98.0 %` | `<= 2.0 s` if triggered | required |
| `denial_corridor_profile_v1` | `<= 7.0 m` | `<= 2.5 m` | `<= 3.0 %` | `>= 97.0 %` | `<= 1.5 s` | required |
| `spoof_like_drift_profile_v1` | `<= 6.0 m` | `<= 2.0 m` | `<= 2.0 %` | `>= 97.5 %` | `<= 1.0 s` | required |
| `comms_instability_profile_v1` | `<= 8.0 m` | `<= 3.0 m` | `<= 4.0 %` | `>= 95.0 %` | `<= 2.5 s` | required unless abort-expected |

## Trust Evaluation Criteria

Trust evaluation verifies that trust signals respond correctly to scenario conditions and estimator degradation.

### Required trust signals

- `gnss_trust`
- `vio_trust`
- `sync_quality`
- `localization_confidence`
- `mission_confidence`

### Trust behavior requirements

- `gnss_trust` must decrease during GNSS anomaly conditions such as GNSS degradation, GNSS denial, or spoof-like drift.
- `vio_trust` must reflect visual tracking quality and decrease when VIO support deteriorates.
- `sync_quality` must decrease when time alignment or freshness degrades.
- `localization_confidence` must decrease when fused localization quality or continuity degrades.
- `mission_confidence` must decrease when the system approaches `MISSION_SAFE_HOLD` or `MISSION_ABORT` conditions.

### Acceptance intent

- Trust outputs must change before or during the corresponding localization-mode transition.
- Trust behavior must remain independent from evaluation-only ground truth.
- Trust outputs must remain deterministic under replay.

## Scenario-Based Validation

Scenario-based validation checks that the system behaves correctly under specific controlled conditions without mixing scenario terms, mission states, and localization modes.

### Nominal mission

- Expected mission behavior: `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_COMPLETE`
- Expected localization behavior: remain primarily in `GNSS_PRIMARY`
- `MISSION_SAFE_HOLD` and `MISSION_ABORT` are failures

### GNSS degraded corridor

- Scenario condition: `gnss_degraded_corridor`
- Expected mission behavior: `MISSION_DEGRADED` may occur without terminal failure
- Expected localization behavior: `BLENDED` or continued `GNSS_PRIMARY` may be acceptable depending on confidence-aware localization outputs
- `MISSION_ABORT` is a failure unless explicitly allowed

### GNSS denied zone

- Scenario condition: `gnss_denied_zone`
- Expected mission behavior: `MISSION_FALLBACK` is expected if continuity is preserved
- Expected localization behavior: entry into `VIO_PRIMARY` is required when GNSS trust collapses
- Persistent `GNSS_PRIMARY` through the denied interval is a failure

### Spoof-like drift scenario

- Scenario condition: `spoof_like_drift`
- Expected mission behavior: deterministic fallback behavior without uncontrolled oscillation
- Expected localization behavior: transition away from GNSS-led operation when trust collapses
- False return to `GNSS_PRIMARY` during active spoof-like drift is a failure

### Communication degradation scenario

- Scenario condition: degraded telemetry timing or freshness
- Expected mission behavior: controlled degradation, `MISSION_SAFE_HOLD`, or allowed abort depending on scenario definition
- Expected localization behavior: reduced `sync_quality` and reduced `localization_confidence`
- A communication fault may justify `MISSION_ABORT` only if the acceptance profile allows it

## Provisional Thresholds

All numeric thresholds in this file are initial simulation-phase thresholds.

- They are intended to support simulation-first verification.
- They are not hardware validation claims.
- They may be recalibrated during a Future hardware integration phase using real sensor data and real timing behavior.
- Any threshold change must preserve terminology consistency and evaluation discipline.

## Invalid Run Conditions

A run is invalid if any of the following occur:

- evaluation-only ground truth is consumed by runtime autonomy
- `/truth/*` is missing, truncated, or time-misaligned
- required sensor streams are missing without scenario justification
- time synchronization collapses and prevents valid replay or evaluation
- telemetry logs are incomplete or corrupted
- deterministic replay diverges from the recorded mission-state sequence
- deterministic replay diverges from the recorded trust-decision sequence
- scenario identity or configuration identity does not match the evaluated artifacts
- simulator seed or clock configuration does not match the scenario manifest

## Evaluation Discipline

Every evaluated run must include:

- scenario identity
- configuration identity
- software revision
- recorded runtime outputs
- evaluation metrics
- final verdict

Evaluation discipline rules:

- evaluation uses evaluation-only ground truth
- runtime autonomy must remain independent from evaluation-only ground truth
- mission states, localization modes, and scenario conditions must remain distinct in evaluation reports
- acceptance conclusions must be reproducible under deterministic replay

## Verdict Rules

- `PASS`: required mission-level, localization, and trust criteria are satisfied and no invalid-run condition occurs
- `FAIL`: one or more required criteria are not satisfied and no invalid-run condition occurs
- `INVALID`: any invalid-run condition occurs
