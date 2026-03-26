# Calibration and Sync Validation Plan

## Purpose

This runbook defines the Phase 15-A3 calibration preparation sequence and sync validation plan for field-transition readiness.

This is a doc-only planning artifact. Runtime behavior, topic contracts, and message schemas remain unchanged in this step.

## Scope Boundary

- Defines stepwise calibration preparation workflow.
- Defines sync validation checkpoints and failure actions.
- Defines real-log evidence requirements for readiness review.
- Does not introduce runtime algorithm, schema, or topic changes.

## Calibration Preparation Sequence

| Step | Input | Action | Output evidence | Gate on failure |
| --- | --- | --- | --- | --- |
| `C1` Baseline capture plan | active scenario set, sensor matrix (`#75`) | lock sensor families, sample windows, and required artifact names | calibration plan record with scenario list | `HOLD` |
| `C2` Sensor contract precheck | topic/schema contracts | verify required fields and topic presence expectations per sensor family | contract precheck checklist | `HOLD` |
| `C3` Timing-rate precheck | timing assumptions (`docs/interfaces/timing-rate-assumptions.md`) | bind manifest-relative expected rates and freshness checks | timing-rate precheck sheet | `HOLD` |
| `C4` Calibration rehearsal run | simulation/hil rehearsal run | execute rehearsal collection flow and annotate anomalies | rehearsal run summary + anomaly log | `HOLD` |
| `C5` Review-ready packaging | outputs from C1..C4 | package evidence bundle and unresolved risks for phase review | calibration evidence bundle | `NO-GO` if missing mandatory items |

## Sync Validation Checkpoints

| Checkpoint | Source | Validation rule | Threshold source | Failure action |
| --- | --- | --- | --- | --- |
| `S1` Timestamp monotonicity | sensor traces and `/sync/status` | no backward timestamp progression on required sensor streams | `docs/interfaces/timing-rate-assumptions.md` replay validity policy | open blocker, rerun capture |
| `S2` Max skew continuity | `SyncStatus.max_skew_ms` | skew trends remain within accepted profile window for the scenario | scenario profile and timing assumptions doc | classify `B2-Critical` and hold |
| `S3` Missing topic diagnostics | `SyncStatus.missing_topics` | required topic set is complete for camera/imu/gnss/sync | topic contract + sensor matrix | classify `B3-Stop` and no-go |
| `S4` Freshness alignment | sensor inter-sample gaps + sync status | freshness gaps align with manifest-relative expectations | `docs/interfaces/timing-rate-assumptions.md` | hold and request recalibration |
| `S5` Reason-code consistency | trust/mission reason-code traces | sync degradation signals are traceable and non-contradictory | `docs/interfaces/reason-codes.md` | hold with root-cause note |

## Failure Handling Policy

- `HOLD`: evidence is partially available but not review-safe; corrective action and rerun are required.
- `NO-GO`: mandatory sync/calibration evidence is missing or contradictory; review cannot proceed.
- Any `B3-Stop` blocker from `docs/runbooks/hil-transition-roadmap.md` immediately escalates to `NO-GO`.

## Real-Log Evidence Requirements

Minimum required bundle for each calibration/sync review cycle:

- run metadata:
  - `run_id`
  - scenario identifier
  - capture timestamp window
- sensor integrity summary:
  - topic presence matrix for camera/imu/gnss/sync
  - required-field completeness check summary
- sync summary:
  - max skew trend
  - missing-topics log
  - monotonicity result
- validation verdict sheet:
  - checkpoint-by-checkpoint `PASS/HOLD/NO-GO`
  - blocker class and owner
  - remediation action and target review date

Evidence bundle must be linked from child issue closure notes and referenced from epic `#16` review comment.

## Review Checklist

- Calibration flow steps `C1..C5` are completed or explicitly blocked with owner.
- All sync checkpoints `S1..S5` are evaluated and verdicted.
- Threshold source is referenced for each failed checkpoint.
- Real-log evidence bundle includes all mandatory sections.
- Remaining risks are listed with blocker class and target resolution.

## Integration Links

- Depends on: `docs/runbooks/sensor-replacement-matrix.md` (`#75`).
- Consumed by: `#77` field safety/manual override checklist preparation.
- Reviewed within: epic `#16` phase completion review.

## References

- `docs/runbooks/hil-transition-roadmap.md`
- `docs/runbooks/sensor-replacement-matrix.md`
- `docs/interfaces/timing-rate-assumptions.md`
- `docs/interfaces/topic-contracts.md`
- `docs/interfaces/message-schemas.md`
- `docs/interfaces/reason-codes.md`
- issue `#76`
