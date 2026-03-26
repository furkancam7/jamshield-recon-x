# Simulated-to-Real Sensor Replacement Matrix

## Purpose

This runbook defines the Phase 15-A2 simulated-to-real sensor replacement matrix for field transition planning.

This is a doc-only contract. Runtime behavior, topic contracts, and message schemas remain unchanged in this step.

## Scope Boundary

- Covers camera, IMU, GNSS, and time-sync transition mapping.
- Defines preserved contracts versus transform requirements.
- Defines validation evidence expectations per mapping row.
- Does not introduce implementation-level driver code.

## Contract Rules

- `docs/interfaces/topic-contracts.md` and `docs/interfaces/message-schemas.md` remain authoritative.
- `/truth/*` remains evaluation-only and must not be consumed by runtime autonomy nodes.
- Mission decision authority remains `mission_continuity_node`.
- Any transform must preserve external topic/message contracts unless explicitly approved in a later phase.

## Replacement Matrix

| Sensor family | Current simulator source | Current topic family | Future hardware counterpart | Contract preserved vs transform | Validation evidence expectations | Blocker class if missing |
| --- | --- | --- | --- | --- | --- | --- |
| camera | simulator camera stream | `/sensors/camera/front/image` | physical camera driver + `camera_adapter_node` | Preserve `SensorImageFrame` contract; source binding changes from simulator stream to device capture path. | Field-level schema completeness check, sequence monotonicity check, replay determinism sample comparison. | `B2-Critical` |
| imu | simulator IMU stream | `/sensors/imu/data` | physical IMU driver + `imu_adapter_node` | Preserve `SensorImuSample`; internal axis alignment/calibration preprocessing may be added without schema change. | Covariance presence/shape check, timestamp monotonicity check, timing-rate assumption traceability (`docs/interfaces/timing-rate-assumptions.md`). | `B2-Critical` |
| gnss | simulator GNSS stream | `/sensors/gnss/fix`, `/localization/gnss/estimate` | GNSS receiver parser + estimate publisher path | External contracts preserved; internal split/merge is allowed if output topics and schemas remain stable. | Fix-to-estimate coherence check, trust-facing reason-code consistency check, replay parity evidence snapshot. | `B2-Critical` |
| time_sync | simulator schedule + sync model | `/sync/status` | hardware clock discipline + `time_sync_node` | Preserve `SyncStatus` schema and semantics; source becomes hardware clock and transport timing inputs. | `max_skew_ms` reporting continuity, missing-topic diagnostics check, sync-quality reason-code traceability. | `B3-Stop` |

## Validation Evidence Bundle (Minimum)

Each sensor row above requires the following minimum evidence entries in review artifacts:

- contract reference: topic + schema path linkage
- preservation decision: preserved or transform-needed statement
- evidence location: artifact/log/report path
- verdict: `PASS`, `HOLD`, or `NO-GO` recommendation note
- reviewer note: unresolved risk and owner (if any)

## Integration Notes

- This matrix is consumed by:
  - `#76` calibration and sync validation planning
  - `#77` field safety and manual override checklist preparation
- Dependency order from `docs/runbooks/hil-transition-roadmap.md` remains normative.

## Out of Scope

- Hardware driver implementation details.
- Runtime mission/trust/tactical logic changes.
- Topic/message schema/API changes.
- Final field go-live decision authority (handled at epic `#16` phase completion review).

## References

- `docs/runbooks/hil-transition-roadmap.md`
- `docs/runbooks/portability-transition.md`
- `docs/interfaces/topic-contracts.md`
- `docs/interfaces/message-schemas.md`
- `docs/interfaces/timing-rate-assumptions.md`
- issue `#75`
