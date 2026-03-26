# Sensor Adapter Contracts

## Purpose

This document defines the doc-level interface contracts for Phase 14-A sensor adapters.

It clarifies adapter ownership, required message fields, deterministic publication rules, and simulator-to-future-hardware mapping boundaries without changing runtime behavior.

## Authority and Boundaries

- This contract is normative for adapter boundaries and must remain aligned with:
  - `docs/interfaces/topic-contracts.md`
  - `docs/interfaces/message-schemas.md`
  - `docs/architecture/03-ros2-node-architecture.md`
- Runtime authority is unchanged:
  - mission decision authority remains `mission_continuity_node`
  - `/truth/*` remains evaluation-only
  - file-based replay/evaluation fallback remains valid
- Numeric timing/rate thresholds are out of scope here and are handled in `#72`.

## Adapter Ownership

| Adapter node | Ownership boundary | Input source | Output topics | Message schemas |
| --- | --- | --- | --- | --- |
| `camera_adapter_node` | Converts simulator camera stream into portable camera message contract only; no trust/mission logic. | simulator camera stream | `/sensors/camera/front/image` | `SensorImageFrame` |
| `imu_adapter_node` | Converts simulator IMU stream into portable inertial message contract only; no trust/mission logic. | simulator IMU stream | `/sensors/imu/data` | `SensorImuSample` |
| `gnss_adapter_node` | Converts simulator GNSS stream into GNSS fix and GNSS-derived localization estimate contracts; no trust decision authority. | simulator GNSS stream | `/sensors/gnss/fix`, `/localization/gnss/estimate` | `SensorGnssFix`, `LocalizationEstimate` |
| `ground_truth_adapter_node` | Publishes evaluation-only truth contract; runtime autonomy consumers are forbidden. | simulator truth state | `/truth/pose` | `GroundTruthPose` |

## Required Fields by Adapter Output

The following required fields are direct references to `message-schemas.md` and are not new schema definitions.

| Adapter node | Topic | Schema | Required fields |
| --- | --- | --- | --- |
| `camera_adapter_node` | `/sensors/camera/front/image` | `SensorImageFrame` | `timestamp_ns`, `frame_id`, `width_px`, `height_px`, `encoding`, `sequence_id`, `exposure_us`, `image_uri` |
| `imu_adapter_node` | `/sensors/imu/data` | `SensorImuSample` | `timestamp_ns`, `frame_id`, `sequence_id`, `angular_velocity_radps.{x,y,z}`, `linear_acceleration_mps2.{x,y,z}`, `covariance.angular_velocity`, `covariance.linear_acceleration` |
| `gnss_adapter_node` | `/sensors/gnss/fix` | `SensorGnssFix` | `timestamp_ns`, `frame_id`, `sequence_id`, `latitude_deg`, `longitude_deg`, `altitude_m`, `velocity_ned_mps.{north,east,down}`, `hdop`, `vdop`, `satellites_used`, `carrier_lock_ratio`, `spoof_suspect_flag` |
| `gnss_adapter_node` | `/localization/gnss/estimate` | `LocalizationEstimate` | `timestamp_ns`, `frame_id`, `child_frame_id`, `source`, `pose.{x_m,y_m,z_m,roll_rad,pitch_rad,yaw_rad}`, `velocity_mps.{x,y,z}`, `covariance_diag`, `is_valid`, `freshness_ms`, `quality_score` |
| `ground_truth_adapter_node` | `/truth/pose` | `GroundTruthPose` | `timestamp_ns`, `frame_id`, `child_frame_id`, `pose.{x_m,y_m,z_m,roll_rad,pitch_rad,yaw_rad}`, `velocity_mps.{x,y,z}` |

## Deterministic Interface Rules

1. Adapter outputs must be deterministic for the same simulator input stream, manifest, and software revision.
2. `timestamp_ns` must represent simulation time semantics; wall-clock time must not be used as message time authority.
3. Publication ordering must remain stable within a run for identical inputs and event schedule.
4. Adapters must not inject mission/trust decisions; they only publish sensor or truth contracts.
5. `ground_truth_adapter_node` remains evaluation-only and must not create runtime autonomy data paths.
6. Replay compatibility requires adapter outputs to stay schema-consistent with `message-schemas.md`.

Timing/rate numeric validation and freshness thresholds are tracked in `#72` and must not be introduced here.

## Simulator to Future Hardware Mapping Matrix

| Current adapter node | Current simulator source | Future hardware-facing adapter role | Mapping mode | Notes |
| --- | --- | --- | --- | --- |
| `camera_adapter_node` | simulator camera stream | camera driver adapter (`camera_adapter_node` contract preserved) | 1:1 | Preserve `SensorImageFrame` output contract; source implementation swaps from simulator to hardware driver. |
| `imu_adapter_node` | simulator IMU stream | IMU driver adapter (`imu_adapter_node` contract preserved) | 1:1 | Preserve `SensorImuSample`; hardware-specific calibration stays outside this contract. |
| `gnss_adapter_node` | simulator GNSS stream | GNSS driver adapter + GNSS-derived estimate publisher | split (internal), stable external outputs | Internal implementation may split receiver parsing and estimate derivation, but external topics remain `/sensors/gnss/fix` and `/localization/gnss/estimate`. |
| `ground_truth_adapter_node` | simulator truth state | no runtime hardware equivalent | simulator-only retained | Kept for evaluation workflows in simulation/HIL contexts; remains outside runtime autonomy decisions. |

## Out of Scope

- Runtime code changes, ROS2 API/schema changes, or mission/trust behavior changes.
- Numeric thresholds for rate, latency, skew, or freshness.
- Hardware driver implementation details.
