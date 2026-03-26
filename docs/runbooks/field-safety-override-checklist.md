# Field Safety Constraints and Manual Override Checklist

## Purpose

This runbook defines the Phase 15-A4 safety constraints and manual override checklist for controlled field-transition readiness.

This is a doc-only deliverable. Runtime behavior, topic contracts, and message schemas remain unchanged in this step.

## Scope Boundary

- Defines operational safety constraints for transition rehearsals.
- Defines manual override workflow and operator responsibilities.
- Defines pre-flight and abort criteria checklist items.
- Does not introduce implementation-level control changes.

## Safety Constraints

| Constraint ID | Constraint | Verification method | Failure disposition |
| --- | --- | --- | --- |
| `SC-01` | Runtime authority boundary must remain intact (`mission_continuity_node` only). | Review mission authority documentation and run artifacts for control-source consistency. | `NO-GO` |
| `SC-02` | `/truth/*` remains evaluation-only and is never consumed by runtime autonomy nodes. | Subscription review against topic contracts and replay evidence checks. | `NO-GO` |
| `SC-03` | Sync degradation must surface through defined diagnostics before field-style rehearsal continuation. | Validate `SyncStatus` and reason-code traces against calibration/sync plan. | `HOLD` |
| `SC-04` | Sensor replacement assumptions must be mapped and reviewed for camera/IMU/GNSS/time-sync. | Verify matrix completeness and reviewer sign-off on each sensor row. | `HOLD` |
| `SC-05` | Unresolved `B3-Stop` blockers from HIL roadmap block transition rehearsal. | Blocker register review and explicit closure proof. | `NO-GO` |

## Manual Override Strategy

Manual override is an operator-controlled safety procedure and must be documented before transition rehearsal.

Workflow:

1. Detect trigger condition from checklist or live diagnostics.
2. Operator declares override intent and records trigger reason.
3. Runtime progression is held; autonomy decisions are not extended without review.
4. Recovery path is selected:
   - controlled restart after mitigation, or
   - abort and return to review queue.
5. Post-event record is attached to evidence bundle with owner and remediation date.

## Operator Responsibilities

| Role | Responsibility |
| --- | --- |
| Simulation/HIL operator | Executes checklist, records pass/fail decisions, and initiates override trigger declaration. |
| Safety reviewer | Confirms constraints `SC-01..SC-05` and validates blocker classification outcome. |
| Phase owner | Approves `GO/HOLD/NO-GO` recommendation and ensures epic evidence linkage on `#16`. |

## Pre-Flight Checklist (Rehearsal Readiness)

- [ ] HIL roadmap stage and gate context is confirmed (`docs/runbooks/hil-transition-roadmap.md`).
- [ ] Sensor replacement matrix has no unresolved mandatory row (`docs/runbooks/sensor-replacement-matrix.md`).
- [ ] Calibration and sync validation bundle is available and reviewed (`docs/runbooks/calibration-sync-validation.md`).
- [ ] Safety constraints `SC-01..SC-05` are checked and documented.
- [ ] Override contacts/owner roles are assigned for this rehearsal window.
- [ ] Evidence log template is prepared with run metadata and decision fields.

## Abort Criteria

Immediate abort (no continuation in current cycle) if any of:

- authority boundary ambiguity is detected (`SC-01` violation)
- `/truth/*` boundary breach is detected (`SC-02` violation)
- unresolved `B3-Stop` blocker exists (`SC-05` violation)
- required evidence bundle section is missing at review gate

Hold and remediate (rerun allowed) if:

- sync checkpoint failure is present with mitigation path (`SC-03`)
- sensor mapping evidence is incomplete but recoverable (`SC-04`)

## Rehearsal Record Template (Minimum)

- run metadata: run id, scenario set, timestamp window
- checklist outcome: pre-flight items pass/fail
- override events: trigger, operator, action taken
- abort/hold decision: reason and blocker class
- remediation owner and target date

## Integration Links

- Depends on:
  - `docs/runbooks/hil-transition-roadmap.md`
  - `docs/runbooks/sensor-replacement-matrix.md`
  - `docs/runbooks/calibration-sync-validation.md`
- Consumed by:
  - epic `#16` phase completion review package

## References

- `docs/runbooks/hil-transition-roadmap.md`
- `docs/runbooks/sensor-replacement-matrix.md`
- `docs/runbooks/calibration-sync-validation.md`
- `docs/interfaces/topic-contracts.md`
- `docs/interfaces/reason-codes.md`
- issue `#77`
