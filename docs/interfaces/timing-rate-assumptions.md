# Timing and Rate Assumptions

## Purpose

This document defines Phase 14-A timing/rate/freshness validation assumptions for hardware-portable contracts.

It is a doc-level contract only and does not introduce runtime API or schema changes.

## Authority and Boundaries

- This document is normative for timing/rate validation notes and must remain aligned with:
  - `docs/interfaces/topic-contracts.md`
  - `docs/interfaces/message-schemas.md`
  - `docs/interfaces/reason-codes.md`
  - `docs/scenario-design/scenario-manifest-spec.md`
- Threshold enforcement in code is out of scope for this step.
- Numeric assumptions below are manifest-relative and used for validation/review discipline.

## Measurement Definitions

All measurements are derived from runtime artifacts and existing contracts.

| Metric | Definition |
| --- | --- |
| `expected_period_ms` | `1000 / expected_rate_hz` where `expected_rate_hz = scenario_manifest.sensors.<family>.rate_hz` |
| `observed_rate_hz` | `(sample_count - 1) / (timestamp_last_s - timestamp_first_s)` on the active sample window |
| `rate_deviation_pct` | `100 * abs(observed_rate_hz - expected_rate_hz) / expected_rate_hz` |
| `freshness_gap_ms` | maximum inter-sample gap inside the active sample window |
| `sync_skew_ms` | `SyncStatus.max_skew_ms` from `/sync/status` |

Window policy:

- Use the latest 100 samples per sensor topic when available.
- If fewer than 100 samples exist, use all available samples.
- Fewer than 20 samples on a required sensor topic is insufficient evidence and must be treated as `INVALID`.

## Manifest-Relative Rule

- `expected_rate_hz` is always read from `scenario_manifest.sensors.<family>.rate_hz`.
- Validation must not use hardcoded global rates as source-of-truth.
- If manifest sensor config is missing for a required family, validation is `INVALID`.

## Sensor Acceptance Rules

| Sensor family | Topic | Manifest key | Acceptance rule (manifest-relative) | Freshness rule |
| --- | --- | --- | --- | --- |
| camera | `/sensors/camera/front/image` | `sensors.camera.rate_hz` | `rate_deviation_pct <= 10` | `freshness_gap_ms <= 3 * expected_period_ms` |
| imu | `/sensors/imu/data` | `sensors.imu.rate_hz` | `rate_deviation_pct <= 5` | `freshness_gap_ms <= 2 * expected_period_ms` |
| gnss | `/sensors/gnss/fix` | `sensors.gnss.rate_hz` | `rate_deviation_pct <= 10` | `freshness_gap_ms <= 3 * expected_period_ms` |

Validation output semantics:

- Any acceptance-rule breach with complete evidence is a `FAIL`.
- Missing required topic, missing manifest rate, or insufficient sample count is `INVALID`.

## Sync and Freshness Relation to `sync_quality`

- `/sync/status` is authoritative for cross-stream timing health.
- `sync_skew_ms` and freshness anomalies should align with `sync_quality_low` evidence in reports when timing health degrades.
- Timing/rate validation must be interpreted with:
  - `SyncStatus.{sim_time_ok, monotonic_ok, max_skew_ms, missing_topics}`
  - runtime reason codes (`sync_quality_low`) from trust/mission outputs.

Interpretation rule:

- If sensor acceptance checks pass but `sync_quality_low` persists, treat as sync-layer risk (not adapter-rate contract failure).
- If sensor acceptance checks fail and `sync_quality_low` is present, treat as correlated timing degradation evidence.

## Deterministic Replay Compatibility Notes

Replay-side timing/rate verdict mapping:

- `INVALID` when:
  - required sensor topic is missing from artifacts
  - manifest sensor rate is missing/invalid
  - sample count is below minimum evidence threshold
  - timestamp monotonicity is broken
- `FAIL` when:
  - replay is valid, but one or more sensor acceptance rules are breached
  - replay is valid, but freshness rule is breached with sufficient evidence
- `PASS` when:
  - replay validity holds and all manifest-relative timing/rate/freshness checks pass

This classification must remain consistent with `docs/evaluation/regression-protocol.md` verdict policy.

## Out of Scope

- Runtime behavior changes in trust/mission/tactical logic.
- New topics or schema fields.
- Hardware-driver implementation details.
