# P16-A2 Trust Calibration Tuning

## Purpose

This document records the trust calibration tuning changes applied in Phase 16-A2 and the measured effect on mismatch residuals.

## Tuning Changes

- Config updates in `configs/sim/default.yaml`:
  - `trust_engine.calibration_medium_floor`: `0.45 -> 0.40`
  - `trust_engine.effective_vio_weak_penalty`: `0.04`
  - `trust_engine.effective_vio_lost_penalty`: `0.06`
- Runtime wiring updates:
  - `TrustEngineService.evaluate(...)` now consumes `effective_vio_state`
  - `scenario_orchestrator` and `runtime.node_runner` pass `effective_vio_state` into trust evaluation

## Validation Run

- Run ID: `p16_a2_tuning_20260326T1716Z`
- Command: `bash scripts/run_regression.sh p16_a2_tuning_20260326T1716Z`
- Core evidence:
  - `artifacts/runs/p16_a2_tuning_20260326T1716Z/trust_calibration.json`
  - `artifacts/runs/p16_a2_tuning_20260326T1716Z/trust_calibration.md`
  - `artifacts/runs/p16_a2_tuning_20260326T1716Z/trust_calibration.csv`
  - `artifacts/runs/p16_a2_tuning_20260326T1716Z/regression_result.json`

## Outcome Summary

- Scenario count: `20`
- `band_mismatch` count: `0`
- `missing_primary_reason` count: `0`
- `missing_supporting_reasons` count: `0`
- Regression overall result: `PASS`

## Decision Notes

- Mission decision authority remains unchanged (`mission_continuity_node`).
- `/truth/*` runtime isolation remains unchanged.
- No report/summary schema bump was introduced.

## Risk and Rollback

- Risk:
  - Lowering `calibration_medium_floor` can over-classify marginal denied scenarios as `medium`.
  - Added VIO-state penalties can suppress confidence more aggressively in weak/lost states.
- Rollback path:
  - Revert `configs/sim/default.yaml` trust calibration values to previous baseline (`calibration_medium_floor=0.45`, no effective-vio penalties).
  - Re-run `bash scripts/run_regression.sh <run_id>` and compare `trust_calibration.json` against the P16-A1 baseline.
