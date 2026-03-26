# HIL Transition Roadmap

## Purpose

This runbook defines the Phase 15-A1 HIL transition roadmap for moving from simulation-first operation toward controlled hardware integration readiness.

This is a doc-only delivery. Runtime behavior, topic contracts, and message schemas remain unchanged in this step.

## Scope Boundary

- Scope applies to transition planning and readiness review only.
- No runtime autonomy logic changes are introduced here.
- `/truth/*` remains evaluation-only.
- Mission decision authority remains `mission_continuity_node`.
- File-based replay/evaluation fallback remains authoritative during transition preparation.

## HIL Transition Stages and Gates

| Stage | Entry criteria | Exit criteria | Primary evidence |
| --- | --- | --- | --- |
| `S0: Simulation Baseline Lock` | P14 portability contracts are landed and Phase 15 is active. | Contracts and runbooks are cross-linked and drift-checked. | `docs/interfaces/*`, `docs/runbooks/portability-transition.md`, `docs/roadmap/progress-tracker.md` |
| `S1: HIL Plan Definition` | S0 complete and P15 child set active. | HIL sequence, dependencies, blocker policy, and review checklist are documented. | this document and issue `#74` closure notes |
| `S2: Integration Readiness Package` | S1 complete and matrix/calibration/safety drafts available. | Sensor replacement matrix, calibration/sync plan, and safety/override checklist are review-complete. | issues `#75/#76/#77` evidence docs |
| `S3: Go/No-Go Review` | S2 complete and residual risks are listed. | Readiness review produces explicit `GO`, `HOLD`, or `NO-GO` decision with blockers. | readiness review record linked from issue `#16` |

## Dependency Ordering (Sensor/Time/Safety)

The following order is normative for transition readiness review:

1. Sensor mapping completeness (`#75`) must be completed first.
2. Calibration and sync validation plan (`#76`) must reference the sensor mapping assumptions.
3. Safety and manual override checklist (`#77`) must consume both mapping and calibration/sync assumptions.
4. Final phase review on `#16` must evaluate all three artifacts together.

## Blocker Classification Policy

| Class | Definition | Decision impact | Example |
| --- | --- | --- | --- |
| `B0-Info` | Documentation gap without immediate safety or determinism risk. | Can proceed with tracked follow-up. | missing non-critical explanatory note |
| `B1-Quality` | Readiness quality issue that reduces confidence but has workaround. | Proceed only with explicit mitigation note. | incomplete non-critical validation traceability |
| `B2-Critical` | Safety, authority-boundary, or determinism risk. | `HOLD` until resolved. | unclear override path, authority boundary ambiguity |
| `B3-Stop` | Missing mandatory artifact or contradictory gate result. | `NO-GO` until corrected and re-reviewed. | missing checklist gate evidence |

## Risk Register (Initial)

| Risk | Trigger | Mitigation |
| --- | --- | --- |
| HIL roadmap remains too abstract | Stages do not map to concrete evidence | Enforce stage-exit evidence links in each child issue |
| Dependency inversion across child deliveries | Safety/checklist is written before mapping assumptions | Keep dependency order mandatory and verify in epic review |
| Drift between roadmap and tracker | Phase docs and issue states diverge | Update tracker and epic sync comments on each child closure |

## Review Checklist

- Stage definitions include both entry and exit criteria.
- Dependency order is explicit and references child issues.
- Blocker classes include clear decision outcomes (`GO/HOLD/NO-GO` mapping).
- Risks and mitigations are listed and traceable.
- References and evidence links are valid.

## Decision Outcomes

Readiness review at `S3` must produce one of:

- `GO`: transition package is complete and consistent for next implementation slice.
- `HOLD`: known blockers exist but can be resolved within Phase 15 child scope.
- `NO-GO`: critical blockers or missing mandatory evidence require rework before continuation.

## References

- `docs/roadmap/phase-15-backlog.md`
- `docs/roadmap/progress-tracker.md`
- `docs/runbooks/portability-transition.md`
- `docs/interfaces/topic-contracts.md`
- `docs/interfaces/message-schemas.md`
