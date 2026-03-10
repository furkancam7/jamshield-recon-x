# ROS2 Node Architecture

## Purpose

This file defines the ROS2 node-level architecture of JamShield Recon-X Sim. It maps the runtime ROS2 graph to the system architecture and fixes the responsibilities, inputs, outputs, and ownership boundaries of each node.

This file must remain consistent with `terminology-lock.md`.

## Node Groups

### Simulation and Ingestion Nodes

- `scenario_orchestrator_node`
- `camera_adapter_node`
- `imu_adapter_node`
- `gnss_adapter_node`
- `ground_truth_adapter_node`

### Core Autonomy Nodes

- `time_sync_node`
- `gnss_trust_node`
- `vio_node`
- `fusion_node`
- `trust_engine_node`
- `mission_continuity_node`
- `sitl_bridge_node`

### Tactical Intelligence Nodes

- `ew_risk_map_node`
- `tactical_summary_node`

### Verification and Operations Nodes

- `health_monitor_node`
- `logger_node`
- `evaluation_node`

### Operator Interface Node

- `operator_station_node`

## Node Responsibilities

| Node | Role | Primary inputs | Primary outputs |
| --- | --- | --- | --- |
| `scenario_orchestrator_node` | Loads the scenario manifest and publishes deterministic scenario events. | scenario manifest, simulator state | `/events/*` |
| `camera_adapter_node` | Publishes simulator camera data as hardware-portable sensor messages. | simulator camera stream | `/sensors/*` |
| `imu_adapter_node` | Publishes simulator IMU data as hardware-portable sensor messages. | simulator IMU stream | `/sensors/*` |
| `gnss_adapter_node` | Publishes simulator GNSS observations and GNSS-derived localization estimates. | simulator GNSS stream | `/sensors/*`, `/localization/*` |
| `ground_truth_adapter_node` | Publishes evaluation-only ground truth from simulation. | simulator truth state | `/truth/*` |
| `time_sync_node` | Monitors simulation clock consistency and input freshness. | `/sensors/*` | `/sync/*` |
| `gnss_trust_node` | Computes GNSS trust and GNSS anomaly outputs. | `/sensors/*`, `/localization/*`, `/sync/*` | `/trust/*` |
| `vio_node` | Computes VIO estimates and VIO quality outputs. | `/sensors/*`, `/sync/*` | `/localization/*` |
| `fusion_node` | Produces confidence-aware fused localization and active source status. | `/localization/*`, `/trust/*`, `/sync/*` | `/localization/*` |
| `trust_engine_node` | Aggregates trust signals and publishes source confidence, localization confidence, and `mission_confidence` for downstream mission continuity. | `/trust/*`, `/localization/*`, `/mission/*` | `/trust/*` |
| `mission_continuity_node` | Applies deterministic mission continuity logic and publishes mission decisions. | `/localization/*`, `/trust/*`, `/mission/*`, `/events/*` | `/mission/*` |
| `sitl_bridge_node` | Converts mission actions into simulator control commands. | `/mission/*` | simulator control inputs |
| `ew_risk_map_node` | Generates EW risk map outputs from navigation degradation evidence. | `/trust/*`, `/localization/*`, `/events/*` | `/tactical/*` |
| `tactical_summary_node` | Produces tactical summaries for operator interpretation. | `/tactical/*`, `/mission/*`, `/trust/*` | `/tactical/*` |
| `logger_node` | Records runtime, tactical, and evaluation-only data for deterministic replay. | `/events/*`, `/sensors/*`, `/sync/*`, `/localization/*`, `/trust/*`, `/mission/*`, `/tactical/*`, `/truth/*` | recorded log artifacts |
| `evaluation_node` | Replays recorded runs and computes evaluation metrics and verdicts. | recorded runtime outputs, `/truth/*` | `/evaluation/*` |
| `health_monitor_node` | Detects sync, freshness, heartbeat, and estimator health faults. | `/sync/*`, `/localization/*`, `/trust/*`, `/mission/*` | `/mission/*`, `/events/*` |
| `operator_station_node` | Displays mission, tactical, and evaluation outputs without affecting runtime autonomy. | `/mission/*`, `/tactical/*`, `/evaluation/*` | none |

## Topic Family Structure

| Topic family | Purpose | Typical publishers | Typical consumers | Restrictions |
| --- | --- | --- | --- | --- |
| `/sensors/*` | Runtime sensor ingress from simulation adapters. | `camera_adapter_node`, `imu_adapter_node`, `gnss_adapter_node` | `time_sync_node`, `vio_node`, `gnss_trust_node`, `logger_node` | Runtime autonomy input only. |
| `/sync/*` | Simulation time alignment and freshness status. | `time_sync_node` | `vio_node`, `gnss_trust_node`, `fusion_node`, `health_monitor_node`, `logger_node` | Must reflect simulation time, not wall-clock time. |
| `/localization/*` | GNSS, VIO, and fused localization outputs plus source status. | `gnss_adapter_node`, `vio_node`, `fusion_node` | `gnss_trust_node`, `fusion_node`, `trust_engine_node`, `mission_continuity_node`, `ew_risk_map_node`, `health_monitor_node`, `logger_node` | Used by runtime autonomy and tactical intelligence, not by evaluation as ground truth. |
| `/trust/*` | GNSS trust, source confidence, localization confidence, and mission confidence outputs. | `gnss_trust_node`, `trust_engine_node` | `fusion_node`, `mission_continuity_node`, `ew_risk_map_node`, `tactical_summary_node`, `health_monitor_node`, `logger_node` | Trust outputs must remain independent from `/truth/*` and must not imply mission decision authority. |
| `/mission/*` | Mission continuity state, action, explanation, and health outputs. | `mission_continuity_node`, `health_monitor_node` | `sitl_bridge_node`, `tactical_summary_node`, `trust_engine_node`, `operator_station_node`, `logger_node` | Mission continuity must remain deterministic. |
| `/tactical/*` | Tactical intelligence products derived from runtime evidence. | `ew_risk_map_node`, `tactical_summary_node` | `tactical_summary_node`, `operator_station_node`, `logger_node` | Tactical outputs do not control runtime autonomy. |
| `/events/*` | Scenario lifecycle events and fault events. | `scenario_orchestrator_node`, `health_monitor_node` | `mission_continuity_node`, `ew_risk_map_node`, `logger_node` | Event ordering is part of deterministic replay. |
| `/truth/*` | Evaluation-only ground truth from simulation. | `ground_truth_adapter_node` | `logger_node`, `evaluation_node` | Runtime autonomy nodes must not consume `/truth/*`. |
| `/evaluation/*` | Replay metadata, evaluation metrics, and evaluation verdicts. | `evaluation_node` | `operator_station_node` | Evaluation outputs must not feed runtime autonomy. |

## Ground Truth Restriction

`/truth/*` topics are evaluation-only.

- `ground_truth_adapter_node` is the only publisher of `/truth/*`.
- `logger_node` may record `/truth/*`.
- `evaluation_node` may consume `/truth/*` during replay and offline evaluation.
- Runtime autonomy nodes must not consume `/truth/*`.
- Tactical intelligence nodes must not consume `/truth/*`.

This restriction preserves the separation between runtime autonomy and evaluation-only ground truth.

## Runtime Ownership Notes

### Runtime autonomy

The runtime autonomy set is:

- `time_sync_node`
- `gnss_trust_node`
- `vio_node`
- `fusion_node`
- `trust_engine_node`
- `mission_continuity_node`
- `sitl_bridge_node`

These nodes drive localization, trust aggregation, fused state estimation, and deterministic mission continuity during live simulation.

### Tactical intelligence

The tactical intelligence set is:

- `ew_risk_map_node`
- `tactical_summary_node`

These nodes derive operator-facing tactical outputs from runtime evidence but do not control the autonomy loop.

### Verification

The verification and replay set is:

- `health_monitor_node`
- `ground_truth_adapter_node`
- `logger_node`
- `evaluation_node`

These nodes support runtime health observation, logging, replay, metrics extraction, and offline verification.

### Operator-facing

The operator-facing node is:

- `operator_station_node`

This node is a display endpoint and not a runtime decision authority.

## Design Discipline Notes

- Node names are locked by `terminology-lock.md`.
- Topic family changes require architecture review.
- Runtime autonomy must remain independent from evaluation-only ground truth.
- `/truth/*` and `/evaluation/*` must not bleed into runtime autonomy.
- Mission continuity remains deterministic and explainable through explicit runtime outputs.
