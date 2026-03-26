# P16-A1 Trust Calibration Baseline Characterization

## Purpose

This document records the reproducible baseline characterization for trust calibration residual mismatch bands in Phase 16-A1.

## Baseline Run

- Run ID: `p16_a1_baseline_20260326T1410Z`
- Command: `bash scripts/run_regression.sh p16_a1_baseline_20260326T1410Z`
- Config: `configs/sim/default.yaml`
- Core evidence:
  - `artifacts/runs/p16_a1_baseline_20260326T1410Z/trust_calibration.json`
  - `artifacts/runs/p16_a1_baseline_20260326T1410Z/trust_calibration.md`
  - `artifacts/runs/p16_a1_baseline_20260326T1410Z/trust_calibration.csv`
  - `artifacts/runs/p16_a1_baseline_20260326T1410Z/regression_result.json`

## Aggregate Metrics

- Scenario count: `20`
- `band_mismatch` count: `3`
- `missing_primary_reason` count: `0`
- `missing_supporting_reasons` count: `0`
- Expected band distribution:
  - `high`: `7`
  - `medium`: `7`
  - `low`: `6`
- Observed band distribution:
  - `high`: `7`
  - `medium`: `6`
  - `low`: `7`

## Residual Mismatch Scenarios

| Scenario | Mission confidence | Expected band | Observed band | Failed checks |
| --- | ---: | --- | --- | --- |
| `s14_sync_low_denied_good` | 0.409 | `medium` | `low` | `band_mismatch` |
| `s4_denied_vio_good` | 0.441 | `medium` | `low` | `band_mismatch` |
| `s8_conflict_state_dominates` | 0.450 | `low` | `medium` | `band_mismatch` |

## Reproducibility Notes

- This baseline uses the default scenario set in `scripts/run_regression.sh`.
- Residual extraction is based on `trust_calibration.json` scenario-level `failed_checks`.
- The output of this document is the tuning input for `#80`.
