# Phase 15 - Field Transition Preparation Backlog

## Goal

Prepare a decision-complete field-transition package for HIL and future hardware integration without changing current runtime contracts in this kickoff slice.

## Scope (P15-A)

- Define HIL transition roadmap with stage gates and blocker policy.
- Define simulated-to-real sensor replacement matrix across camera/IMU/GNSS/time-sync.
- Define calibration and sync validation planning baseline, including real-log evidence requirements.
- Define field safety constraints and manual override checklist baseline.

## Non-Goals (P15-A)

- No runtime mission/trust/tactical behavior changes.
- No ROS2 topic or message schema/API bump.
- No direct hardware driver implementation in this kickoff step.
- No changes to `/truth/*` evaluation-only boundaries or mission decision authority ownership.

## Child Issue Set

- `#74` P15-A1 HIL transition roadmap
- `#75` P15-A2 Simulated-to-real sensor replacement matrix
- `#76` P15-A3 Calibration and sync validation plan
- `#77` P15-A4 Field safety constraints and manual override checklist

## Kickoff Evidence

- Epic kickoff baseline is tracked in issue `#16`.
- P15-A child issue set `#74/#75/#76/#77` is created and linked to phase scope.
- Active phase tracker is moved to Phase 15 in-progress state.

## Landed Evidence

- `#74` landed via `docs/runbooks/hil-transition-roadmap.md` with runbook index linkage in `docs/runbooks/README.md`.
- `#75` landed via `docs/runbooks/sensor-replacement-matrix.md` with runbook index linkage in `docs/runbooks/README.md`.
- `#76` landed via `docs/runbooks/calibration-sync-validation.md` with runbook index linkage in `docs/runbooks/README.md`.
- `#77` landed via `docs/runbooks/field-safety-override-checklist.md` with runbook index linkage in `docs/runbooks/README.md`.

## Acceptance Gates

- Transition readiness review package is decision-complete.
- Calibration workflow and sync validation plan are reviewable end-to-end.
- Safety constraints and manual override checklist are explicit and actionable.
- HIL roadmap is written, sequenced, and implementation-ready.

## Residual Boundaries

- Cross-phase trust calibration tuning remains phase-external and does not block P15 kickoff.
- Runtime authority model remains unchanged:
  - file-based replay/evaluation fallback remains valid
  - mission decision authority remains `mission_continuity_node`
  - `/truth/*` remains evaluation-only

## Phase Completion Review

- Completion review finalized on epic `#16` with P15-A child set `#74/#75/#76/#77` closed.
- P15 remained doc-only in this slice; no runtime/topic/message API behavior changes were introduced.
- All planned phases in the current roadmap are now completed; remaining trust calibration tuning stays phase-external.
