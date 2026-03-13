# Phase 12 - ROS2 Runtime Migration Backlog

## Goal

Open Phase 12 to migrate the current executable slice from script-driven file orchestration toward a node-based ROS2 runtime while preserving deterministic behavior and evaluation boundaries.

## Scope

- Define migration steps from current file-based execution to ROS2 node orchestration with parity gates.
- Keep runtime autonomy and evaluation boundaries intact during migration.
- Preserve current trust/fusion/mission/tactical decision semantics while changing runtime wiring.
- Establish a first executable ROS2 runtime loop with deterministic topic contracts.
- Maintain file-based replay/evaluation as the authoritative fallback until ROS2 parity checks pass.

## Current Slice Decisions

- This phase does not expand mission lifecycle states.
- The executable mission-state set remains:
  - `MISSION_EXECUTE`
  - `MISSION_DEGRADED`
  - `MISSION_FALLBACK`
  - `MISSION_SAFE_HOLD`
  - `MISSION_ABORT`
- `/truth/*` remains evaluation-only and must not be consumed by runtime autonomy nodes.
- `logger_node` and `evaluation_node` are migration targets; they are not considered complete at phase kickoff.

## Verification Targets

- Deterministic parity checks between ROS2 runtime outputs and the current file-based baseline on representative baseline scenarios.
- Runtime autonomy nodes must remain independent from `/truth/*` and `/evaluation/*`.
- Mission continuity remains the sole decision authority for mission state/action outputs.
- Regression and artifact gates continue to pass with schema `2.4` until a future, explicit schema bump.

## Non-Goals

- Implementing hardware drivers or field-integration behaviors
- Feeding ground truth into runtime autonomy decisions
- Rewriting mission lifecycle to include `MISSION_PREPARE` or `MISSION_COMPLETE` in the executable slice
