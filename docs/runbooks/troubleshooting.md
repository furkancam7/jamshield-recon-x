# Troubleshooting

## Scope

This runbook covers simulation, replay, and evaluation failures. It does not cover real hardware, which belongs to the Future hardware integration phase.

## Symptom: No Fused Localization Output

Check:

1. `/sync/status` for stale or missing sensor inputs
2. `/localization/vio/estimate` freshness and `is_valid`
3. `/trust/source_confidence` for `TRUST_NO_VALID_SOURCE`
4. `/mission/health` for `HEALTH_VIO_STALLED` or `HEALTH_FUSION_INVALID`

Likely causes:

- camera or IMU stream missing
- GNSS and VIO both below confidence thresholds
- sync drift exceeded continuity limit

## Symptom: Unexpected `MISSION_ABORT`

Check:

1. `/mission/explanation` primary reason code
2. `/mission/health` severity immediately before abort
3. scenario event timeline on `/events/scenario`
4. whether the abort exceeded the contingency timeout

Likely causes:

- prolonged `LOCALIZATION_CONTINGENCY`
- critical health fault
- scenario manifest inconsistent with route duration or sensor profile

## Symptom: Replay Marked `INVALID`

Check:

1. manifest hash equality
2. availability and completeness of `/truth/pose`
3. first divergence in mission state or trust decision sequence
4. log corruption or dropped recorded topics

Likely causes:

- log bundle incomplete
- replay configuration differs from original run
- nondeterministic behavior introduced in runtime nodes

## Symptom: GNSS Not Rejected During Spoof-Like Drift

Check:

1. `/trust/gnss` for `GNSS_SPOOF_LIKE_DRIFT`
2. innovation consistency component of the GNSS trust report
3. `/trust/decision` for `TRUST_GNSS_GATED`
4. `/localization/source_status` active mode

Likely causes:

- drift magnitude too small for configured thresholds
- VIO quality too poor to support confident rejection
- trust hysteresis preventing transition due to configuration mismatch

## Symptom: Continuity Breaks During Denial Corridor

Check:

1. fallback reaction time against scenario threshold
2. VIO estimate freshness during denial interval
3. communication degradation events that may have affected camera or IMU timing
4. `LOCALIZATION_CONTINGENCY` entry reason codes

Likely causes:

- VIO underperforming due to visual texture or sensor noise
- delay or loss on required sensor streams
- denial event overlapping with unsupported sensor degradation

## Escalation Rule

If troubleshooting identifies a structural mismatch between architecture intent and runtime behavior, record the issue with:

- scenario id
- run id
- first divergence timestamp
- relevant reason codes
- whether the issue is runtime, replay, or evaluation
