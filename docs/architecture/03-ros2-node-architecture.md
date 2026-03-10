# ROS2 Node Architecture

## Node Inventory

| Node | Responsibility | Publishes | Subscribes |
| --- | --- | --- | --- |
| `scenario_orchestrator_node` | Loads the scenario manifest, sets deterministic seed, schedules injected events, controls scenario lifecycle | `/events/scenario` | none |
| `camera_adapter_node` | Converts simulator camera output into hardware-portable image frames | `/sensors/camera/front/image` | none |
| `imu_adapter_node` | Converts simulator IMU output into hardware-portable IMU samples | `/sensors/imu/data` | none |
| `gnss_adapter_node` | Converts simulator GNSS output into GNSS fixes and GNSS-only navigation estimates | `/sensors/gnss/fix`, `/localization/gnss/estimate` | none |
| `ground_truth_adapter_node` | Publishes evaluation-only ground truth from the simulator | `/truth/pose` | none |
| `time_sync_node` | Validates timestamp alignment and sim clock monotonicity | `/sync/status` | `/sensors/camera/front/image`, `/sensors/imu/data`, `/sensors/gnss/fix` |
| `gnss_trust_node` | Computes GNSS trust and anomaly classification from GNSS behavior | `/trust/gnss` | `/sensors/gnss/fix`, `/localization/vio/estimate`, `/sync/status` |
| `vio_node` | Computes VIO pose, velocity, and estimator quality | `/localization/vio/estimate` | `/sensors/camera/front/image`, `/sensors/imu/data`, `/sync/status` |
| `fusion_node` | Produces the fused localization estimate and active source status | `/localization/fused/estimate`, `/localization/source_status` | `/localization/gnss/estimate`, `/localization/vio/estimate`, `/trust/source_confidence`, `/sync/status` |
| `trust_engine_node` | Converts GNSS trust and estimator health into source confidence and transition decisions | `/trust/source_confidence`, `/trust/decision` | `/trust/gnss`, `/localization/vio/estimate`, `/localization/source_status`, `/mission/health` |
| `mission_continuity_node` | Applies deterministic mission state transitions and emits mission actions | `/mission/state`, `/mission/action`, `/mission/explanation` | `/localization/fused/estimate`, `/trust/decision`, `/mission/health`, `/events/scenario` |
| `sitl_bridge_node` | Translates mission actions into simulator control commands | none | `/mission/action` |
| `ew_risk_map_node` | Builds a spatial risk map from degradation signatures | `/tactical/ew_risk_map` | `/trust/gnss`, `/trust/source_confidence`, `/localization/fused/estimate`, `/events/scenario` |
| `tactical_summary_node` | Produces operator-readable tactical summaries | `/tactical/summary` | `/tactical/ew_risk_map`, `/mission/state`, `/trust/decision`, `/mission/health` |
| `logger_node` | Records runtime topics, tactical outputs, and evaluation-only ground truth for deterministic replay | none | `/events/scenario`, `/events/faults`, `/sensors/camera/front/image`, `/sensors/imu/data`, `/sensors/gnss/fix`, `/sync/status`, `/localization/gnss/estimate`, `/localization/vio/estimate`, `/localization/fused/estimate`, `/localization/source_status`, `/trust/gnss`, `/trust/source_confidence`, `/trust/decision`, `/mission/state`, `/mission/action`, `/mission/explanation`, `/mission/health`, `/tactical/ew_risk_map`, `/tactical/summary`, `/truth/pose` |
| `evaluation_node` | Replays logs, computes metrics, and publishes evaluation outputs | `/evaluation/run_metadata`, `/evaluation/metrics`, `/evaluation/verdict` | `/truth/pose`, recorded runtime outputs |
| `health_monitor_node` | Detects heartbeat, freshness, and estimator stall faults | `/mission/health`, `/events/faults` | `/sync/status`, `/localization/vio/estimate`, `/localization/fused/estimate`, `/trust/decision`, `/mission/state` |
| `operator_station_node` | Displays mission state, tactical summary, and evaluation products without affecting deterministic runs | none | `/mission/state`, `/mission/explanation`, `/mission/health`, `/tactical/ew_risk_map`, `/tactical/summary`, `/evaluation/run_metadata`, `/evaluation/metrics`, `/evaluation/verdict` |

## Design Notes

### Adapters are hardware-portable boundaries

`camera_adapter_node`, `imu_adapter_node`, `gnss_adapter_node`, and `ground_truth_adapter_node` isolate simulator-specific transport from the rest of the stack. A Future hardware integration phase may replace simulator ingress without changing downstream topic contracts.

### Trust is separated from fusion

`gnss_trust_node` measures GNSS reliability. `trust_engine_node` translates trust and estimator health into source confidence and decision outputs. `fusion_node` does not infer trust by itself; it only applies the provided confidence-aware localization policy.

### Mission continuity is separated from localization

`mission_continuity_node` does not estimate state. It consumes localization and trust outputs and emits mission actions with explicit reason codes. This keeps the decision path auditable.

### Evaluation is isolated

`ground_truth_adapter_node` and `evaluation_node` must remain outside the runtime autonomy path. No runtime node may depend on `/truth/*` or `/evaluation/*` topics.

## Startup Ordering

The required startup order is:

1. `scenario_orchestrator_node`
2. sensor adapter nodes
3. `time_sync_node`
4. `vio_node`
5. `gnss_trust_node`
6. `health_monitor_node`
7. `trust_engine_node`
8. `fusion_node`
9. `mission_continuity_node`
10. `sitl_bridge_node`
11. tactical nodes
12. `logger_node`
13. `operator_station_node`

`ground_truth_adapter_node` may start with the sensor adapters because it is evaluation-only.
