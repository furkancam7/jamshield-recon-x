# Portability Transition Runbook

## Purpose

This runbook defines the Phase 14-A portability transition contract for moving from simulator-driven sensor inputs to future hardware-backed inputs.

This is a doc-only operational contract. Runtime behavior, topic APIs, and message schemas remain unchanged in this step.

## Current-Slice Boundary

- Simulation-first execution remains the default operating mode.
- Runtime authority model is unchanged:
  - mission decision authority remains `mission_continuity_node`
  - `/truth/*` remains evaluation-only
  - file-based replay/evaluation fallback remains authoritative
- `repo_wrapper` remains the default launch backend. `colcon` remains optional.
- This runbook does not introduce new ROS2 topics, message fields, or runtime decision logic.

## Onboard vs Ground Split Notes

The split below is an operational planning contract for future hardware deployment, not an immediate deployment switch.

| Responsibility area | Default side | Notes |
| --- | --- | --- |
| Sensor ingestion adapters (`camera_adapter_node`, `imu_adapter_node`, `gnss_adapter_node`) | onboard | Move data acquisition to hardware-facing adapters while preserving topic/schema contracts. |
| Time and sync health (`time_sync_node`) | onboard | Remains the source of simulation-time compatible sync health semantics. |
| Runtime autonomy core (`vio_node`, `gnss_trust_node`, `fusion_node`, `trust_engine_node`, `mission_continuity_node`, `health_monitor_node`, `ew_risk_map_node`) | onboard | Autonomy decision loop should remain co-located with sensor ingestion to avoid control-latency drift. |
| Tactical/operator outputs (`tactical_summary_node`, `operator_station_node`) | ground | Ground-facing interpretation and operator presentation remain outside onboard control authority. |
| Evaluation and replay (`evaluation_node`, file-based replay artifacts) | ground | Keep evaluation isolation and `/truth/*` boundaries intact. |
| Logging and release evidence collection | ground | Keep release evidence generation and archival independent from onboard runtime authority. |

## Simulator to Hardware Mapping Matrix

| Current source/topic family | Future hardware counterpart | Contract preserved or transform needed | Validation note | Deferred owner/phase |
| --- | --- | --- | --- | --- |
| simulator camera stream -> `/sensors/camera/front/image` | physical camera driver + `camera_adapter_node` | preserved (`SensorImageFrame`) | Validate field completeness and manifest-relative timing/rate assumptions from `docs/interfaces/timing-rate-assumptions.md`. | P15 HIL preparation |
| simulator IMU stream -> `/sensors/imu/data` | physical IMU driver + `imu_adapter_node` | preserved (`SensorImuSample`) | Validate monotonic timestamps, rate deviation window checks, and replay determinism parity. | P15 HIL preparation |
| simulator GNSS stream -> `/sensors/gnss/fix`, `/localization/gnss/estimate` | GNSS receiver parser + estimate publisher path | external contracts preserved, internal split allowed | Validate trust-facing consistency and mapping parity against current GNSS contracts. | P15 HIL preparation |
| simulator sync schedule -> `/sync/status` | hardware clock discipline + `time_sync_node` | preserved (`SyncStatus`) with source adaptation | Validate `max_skew_ms`, missing-topic reporting, and reason-code consistency. | P15 timing hardening |
| simulator truth stream -> `/truth/pose` | no onboard runtime equivalent | preserved as simulation/evaluation-only | Runtime autonomy consumers remain prohibited; keep evaluation-only isolation. | stays evaluation-only (cross-phase) |
| replay/evaluation artifacts -> `/evaluation/*` outputs | ground-side replay/evaluation pipeline | preserved as ground/evaluation path | Validate PASS/FAIL/INVALID policy in replay workflow before release decisions. | P15 release hardening |

## Integration Readiness Checklist

- Adapter boundaries remain aligned with `docs/interfaces/sensor-adapter-contracts.md`.
- Timing/rate validation expectations remain aligned with `docs/interfaces/timing-rate-assumptions.md`.
- Topic and message references remain aligned with:
  - `docs/interfaces/topic-contracts.md`
  - `docs/interfaces/message-schemas.md`
- `/truth/*` and `/evaluation/*` separation constraints remain intact.
- Release evidence workflow includes minimum gate, regression, and artifact validation before portability decisions.

## Deferred Items (Phase 15 / HIL)

- Hardware driver implementation and calibration loops.
- Real-device clock discipline and transport-layer jitter mitigation.
- HIL validation automation for adapter and timing parity.
- Field deployment policy and rollback automation beyond simulation-first operation.

## References

- `docs/interfaces/sensor-adapter-contracts.md`
- `docs/interfaces/timing-rate-assumptions.md`
- `docs/interfaces/topic-contracts.md`
- `docs/interfaces/message-schemas.md`
- `docs/runbooks/run-simulation.md`
- `docs/runbooks/replay-analysis.md`
- `docs/runbooks/known-limitations.md`
