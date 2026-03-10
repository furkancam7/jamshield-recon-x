# Runtime Dataflow Diagram

## Purpose

This file defines the runtime data movement and control boundaries of JamShield Recon-X Sim.

It focuses on how runtime data moves through the ROS2 graph, where mission decisions are produced, how tactical outputs are derived, and how logging and evaluation remain separated from runtime autonomy.

## Dataflow Modeling Rules

- The runtime autonomy loop is separate from evaluation.
- Ground truth is evaluation-only and must not enter runtime autonomy.
- `gnss_trust_node` produces GNSS trust, not mission decisions.
- `fusion_node` produces fused localization, not final mission confidence.
- `trust_engine_node` produces trust decisions and source confidence, not control commands.
- `mission_continuity_node` consumes trust and localization state to produce deterministic mission decisions.
- `logger_node` is passive and records data without influencing runtime behavior.
- `evaluation_node` performs observer-side replay and analysis using recorded runtime outputs and `/truth/*`.

## Core Runtime Flow

1. `scenario_orchestrator_node` starts the run, loads the `scenario_manifest`, and publishes scenario lifecycle events on `/events/*`.
2. `camera_adapter_node`, `imu_adapter_node`, and `gnss_adapter_node` publish simulated sensor data on `/sensors/*`.
3. `time_sync_node` validates timing alignment and freshness across the sensor streams and publishes `/sync/*`.
4. `gnss_trust_node` consumes GNSS observations, sync state, and non-GNSS motion context to produce GNSS trust on `/trust/*`.
5. `vio_node` consumes camera and IMU data and produces VIO localization outputs on `/localization/*`.
6. `gnss_adapter_node` also provides GNSS-derived localization on `/localization/*`.
7. `trust_engine_node` combines trust and runtime health context to produce source confidence and trust decisions on `/trust/*`.
8. `fusion_node` consumes GNSS localization, VIO localization, source confidence, and sync state to produce fused localization and source status on `/localization/*`.
9. `mission_continuity_node` consumes fused localization, trust decisions, mission health, and scenario progress to produce deterministic mission state, mission action, and mission explanation on `/mission/*`.
10. `sitl_bridge_node` consumes `/mission/*` action outputs and closes the control loop with the simulator.
11. The simulator responds to the mission action, producing the next sensor cycle.

## Tactical Dataflow

`ew_risk_map_node` consumes:

- `/trust/*`
- `/localization/*`
- `/events/*`

It publishes tactical EW risk outputs on `/tactical/*`.

`tactical_summary_node` consumes:

- `/tactical/*`
- `/mission/*`
- `/trust/*`

It publishes tactical summaries on `/tactical/*`.

Tactical outputs reach the operator through `operator_station_node`. Tactical outputs do not control the vehicle and do not replace mission continuity.

## Evaluation and Logging Boundary

`logger_node` subscribes passively to:

- `/events/*`
- `/sensors/*`
- `/sync/*`
- `/localization/*`
- `/trust/*`
- `/mission/*`
- `/tactical/*`
- `/truth/*`

It records runtime evidence without participating in trust, fusion, or mission decision logic.

`evaluation_node` consumes:

- recorded runtime outputs
- `/truth/*`

It produces `/evaluation/*` outputs for replay, metrics, and verdicts.

`/truth/*` never enters runtime autonomy.

## Operator Visibility

`operator_station_node` observes:

- localization outputs through mission and tactical runtime products
- trust-related outputs through mission explanations and tactical outputs
- mission state through `/mission/state`
- tactical summaries through `/tactical/*`
- evaluation outputs through `/evaluation/*` when available

`operator_station_node` is a visibility endpoint only. It does not publish runtime control commands during deterministic runs.

## PlantUML Runtime Dataflow Diagram

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam shadowing false

package "Scenario and Sensor Nodes" {
  component scenario_orchestrator_node
  component camera_adapter_node
  component imu_adapter_node
  component gnss_adapter_node
  component ground_truth_adapter_node
}

package "Core Autonomy Nodes" {
  component time_sync_node
  component gnss_trust_node
  component vio_node
  component trust_engine_node
  component fusion_node
  component health_monitor_node
  component mission_continuity_node
  component sitl_bridge_node
}

package "Tactical Intelligence Nodes" {
  component ew_risk_map_node
  component tactical_summary_node
}

package "Verification and Operations Nodes" {
  component logger_node
  component evaluation_node
}

package "Operator Interface Node" {
  component operator_station_node
}

scenario_orchestrator_node --> mission_continuity_node : /events/scenario
scenario_orchestrator_node --> ew_risk_map_node : /events/scenario

camera_adapter_node --> time_sync_node : /sensors/camera/front/image
camera_adapter_node --> vio_node : /sensors/camera/front/image

imu_adapter_node --> time_sync_node : /sensors/imu/data
imu_adapter_node --> vio_node : /sensors/imu/data

gnss_adapter_node --> time_sync_node : /sensors/gnss/fix
gnss_adapter_node --> gnss_trust_node : /sensors/gnss/fix
gnss_adapter_node --> fusion_node : /localization/gnss/estimate

time_sync_node --> gnss_trust_node : /sync/status
time_sync_node --> vio_node : /sync/status
time_sync_node --> fusion_node : /sync/status
time_sync_node --> health_monitor_node : /sync/status

vio_node --> gnss_trust_node : /localization/vio/estimate
vio_node --> trust_engine_node : /localization/vio/estimate
vio_node --> fusion_node : /localization/vio/estimate
vio_node --> health_monitor_node : /localization/vio/estimate

gnss_trust_node --> trust_engine_node : /trust/gnss
gnss_trust_node --> ew_risk_map_node : /trust/gnss

health_monitor_node --> trust_engine_node : /mission/health
health_monitor_node --> mission_continuity_node : /mission/health
health_monitor_node --> tactical_summary_node : /mission/health
health_monitor_node --> operator_station_node : /mission/health

trust_engine_node --> fusion_node : /trust/source_confidence
trust_engine_node --> mission_continuity_node : /trust/decision
trust_engine_node --> tactical_summary_node : /trust/decision

fusion_node --> mission_continuity_node : /localization/fused/estimate
fusion_node --> trust_engine_node : /localization/source_status
fusion_node --> ew_risk_map_node : /localization/fused/estimate
fusion_node --> health_monitor_node : /localization/fused/estimate

mission_continuity_node --> sitl_bridge_node : /mission/action
mission_continuity_node --> tactical_summary_node : /mission/state
mission_continuity_node --> operator_station_node : /mission/state
mission_continuity_node --> operator_station_node : /mission/explanation

ew_risk_map_node --> tactical_summary_node : /tactical/ew_risk_map
ew_risk_map_node --> operator_station_node : /tactical/ew_risk_map

tactical_summary_node --> operator_station_node : /tactical/summary

scenario_orchestrator_node ..> logger_node : /events/*
camera_adapter_node ..> logger_node : /sensors/*
imu_adapter_node ..> logger_node : /sensors/*
gnss_adapter_node ..> logger_node : /sensors/*,/localization/*
time_sync_node ..> logger_node : /sync/*
gnss_trust_node ..> logger_node : /trust/*
vio_node ..> logger_node : /localization/*
trust_engine_node ..> logger_node : /trust/*
fusion_node ..> logger_node : /localization/*
health_monitor_node ..> logger_node : /mission/*,/events/*
mission_continuity_node ..> logger_node : /mission/*
ew_risk_map_node ..> logger_node : /tactical/*
tactical_summary_node ..> logger_node : /tactical/*

ground_truth_adapter_node --> evaluation_node : /truth/pose
ground_truth_adapter_node ..> logger_node : /truth/pose
logger_node ..> evaluation_node : recorded runtime outputs

evaluation_node --> operator_station_node : /evaluation/*

note right of ground_truth_adapter_node
  /truth/* is evaluation-only
end note

note bottom of logger_node
  Passive observer only
end note

note bottom of sitl_bridge_node
  Runtime autonomy loop ends here
end note

@enduml
```
