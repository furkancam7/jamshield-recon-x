# Phase 11 - Replay and Evaluation Hardening Backlog

## Goal

Harden the executable simulation slice with deterministic runtime traces, pseudo-truth traces, replay comparison, offline metrics, and explicit evaluation verdicts.

## Scope

- Add `src/logging_replay/` helpers for runtime trace and pseudo-truth artifacts.
- Add file-based deterministic replay comparison for `runtime_trace`, `mission_audit`, report payloads, EW hashes, and tactical summaries.
- Add named acceptance profiles under `configs/eval/default.yaml`.
- Require `evaluation_profile` in baseline scenario manifests.
- Produce `replay_results.json/.md/.csv`.
- Produce `evaluation_metrics.json/.md/.csv`.
- Produce `evaluation_verdicts.json/.md/.csv`.
- Upgrade evaluation report and summary schema to `2.4`.

## Current Slice Decisions

- Replay remains file-based in this phase; it is not yet a ROS2 `evaluation_node`.
- Pseudo-truth is deterministic route-progress interpolation, not simulator-native exact truth.
- `MISSION_PREPARE`, `MISSION_COMPLETE`, and `LOCALIZATION_CONTINGENCY` remain architecture targets, not executable current-slice states.
- The executable mission-state set remains:
  - `MISSION_EXECUTE`
  - `MISSION_DEGRADED`
  - `MISSION_FALLBACK`
  - `MISSION_SAFE_HOLD`
  - `MISSION_ABORT`

## Verification Targets

- Unit coverage for trace shape, replay comparison, metrics, and verdict rules
- Full baseline regression on `s1-s20`
- Artifact validation for trace, replay, metric, verdict, calibration, EW, tactical, and summary outputs
- Mixed `2.3/2.4` artifact rejection

## Non-Goals

- Implementing ROS2 `logger_node`
- Implementing ROS2 `evaluation_node`
- Using `/truth/*` as a runtime autonomy input
- Introducing simulator-native exact ground truth into the current executable slice
