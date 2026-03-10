# Topic Contracts

## Contract Rules

- Publishers are single-writer unless explicitly stated otherwise.
- Message timestamps use simulation time from `time_sync_node`.
- `/truth/*` is reserved for evaluation-only ground truth.
- `/evaluation/*` exists only during replay or offline evaluation.

## Topic Naming Convention

Topic families define the top-level namespace boundary for a class of data. Concrete topics are the repository-approved contracts that live under those families.

Locked topic families are:

- `/sensors/*`
- `/sync/*`
- `/localization/*`
- `/trust/*`
- `/mission/*`
- `/tactical/*`
- `/events/*`
- `/truth/*`
- `/evaluation/*`

Concrete topic naming follows the general pattern:

`/family/component/resource`

Examples:

- `/sensors/camera/front/image`
- `/localization/gnss/estimate`
- `/localization/fused/estimate`
- `/trust/gnss/value`
- `/trust/localization/confidence`
- `/trust/mission_confidence`
- `/mission/state`
- `/tactical/summary`

Naming rules:

- The family identifies the data domain.
- The component identifies the producing subsystem or data source.
- The resource identifies the specific contract carried on the topic.
- Some concrete topics may use a shorter form such as `/mission/state` when the family contract is singular and already unambiguous.
- Topic names under `/trust/*` must not imply control or mission decision authority.
- Mission decisions are published only under `/mission/*`.

## Topic Matrix

| Topic | Message | Publisher | Subscribers | Class | Notes |
| --- | --- | --- | --- | --- | --- |
| `/sensors/camera/front/image` | `SensorImageFrame` | `camera_adapter_node` | `vio_node`, `time_sync_node`, `logger_node` | runtime autonomy | Front camera stream used by VIO |
| `/sensors/imu/data` | `SensorImuSample` | `imu_adapter_node` | `vio_node`, `time_sync_node`, `logger_node` | runtime autonomy | Primary inertial stream |
| `/sensors/gnss/fix` | `SensorGnssFix` | `gnss_adapter_node` | `gnss_trust_node`, `time_sync_node`, `logger_node` | runtime autonomy | Raw GNSS observation contract |
| `/sync/status` | `SyncStatus` | `time_sync_node` | `vio_node`, `gnss_trust_node`, `fusion_node`, `health_monitor_node`, `logger_node` | runtime autonomy | Clock health and freshness |
| `/localization/gnss/estimate` | `LocalizationEstimate` | `gnss_adapter_node` | `fusion_node`, `logger_node` | runtime autonomy | GNSS-only navigation estimate |
| `/localization/vio/estimate` | `LocalizationEstimate` | `vio_node` | `gnss_trust_node`, `fusion_node`, `trust_engine_node`, `health_monitor_node`, `logger_node` | runtime autonomy | VIO estimate with estimator quality |
| `/localization/fused/estimate` | `LocalizationEstimate` | `fusion_node` | `mission_continuity_node`, `ew_risk_map_node`, `health_monitor_node`, `logger_node` | runtime autonomy | Active fused localization estimate |
| `/localization/source_status` | `LocalizationSourceStatus` | `fusion_node` | `trust_engine_node`, `logger_node` | runtime autonomy | Current source mode and quality flags |
| `/trust/gnss/value` | `GnssTrustReport` | `gnss_trust_node` | `trust_engine_node`, `ew_risk_map_node`, `logger_node` | runtime autonomy | GNSS trust and anomaly indicators |
| `/trust/localization/confidence` | `SourceConfidenceReport` | `trust_engine_node` | `fusion_node`, `ew_risk_map_node`, `logger_node` | runtime autonomy | Confidence-aware localization input |
| `/trust/mission_confidence` | `TrustDecision` | `trust_engine_node` | `mission_continuity_node`, `tactical_summary_node`, `health_monitor_node`, `logger_node` | runtime autonomy | Aggregated trust output used by downstream mission continuity and tactical interpretation |
| `/mission/state` | `MissionState` | `mission_continuity_node` | `tactical_summary_node`, `health_monitor_node`, `operator_station_node`, `logger_node` | runtime autonomy | Authoritative mission continuity state |
| `/mission/action` | `MissionAction` | `mission_continuity_node` | `sitl_bridge_node`, `logger_node` | runtime autonomy | Deterministic mission action output |
| `/mission/explanation` | `MissionExplanation` | `mission_continuity_node` | `operator_station_node`, `logger_node` | runtime autonomy | Transition rationale with reason codes |
| `/mission/health` | `HealthStatus` | `health_monitor_node` | `trust_engine_node`, `mission_continuity_node`, `tactical_summary_node`, `operator_station_node`, `logger_node` | runtime autonomy | Health severity and affected subsystem |
| `/tactical/ew_risk_map` | `EwRiskMap` | `ew_risk_map_node` | `tactical_summary_node`, `operator_station_node`, `logger_node` | tactical intelligence | Navigation degradation heat map |
| `/tactical/summary` | `TacticalSummary` | `tactical_summary_node` | `operator_station_node`, `logger_node` | tactical intelligence | Operator-oriented tactical summary |
| `/events/scenario` | `ScenarioEvent` | `scenario_orchestrator_node` | `mission_continuity_node`, `ew_risk_map_node`, `logger_node` | runtime autonomy | Scenario schedule and lifecycle events |
| `/events/faults` | `FaultEvent` | `health_monitor_node` | `logger_node` | runtime autonomy | Detected runtime faults |
| `/truth/pose` | `GroundTruthPose` | `ground_truth_adapter_node` | `logger_node`, `evaluation_node` | evaluation-only ground truth | Prohibited from runtime autonomy |
| `/evaluation/run_metadata` | `EvaluationRunMetadata` | `evaluation_node` | `operator_station_node` | evaluation | Replay metadata and manifest hash |
| `/evaluation/metrics` | `EvaluationMetric` | `evaluation_node` | `operator_station_node` | evaluation | Metric stream emitted after replay |
| `/evaluation/verdict` | `EvaluationVerdict` | `evaluation_node` | `operator_station_node` | evaluation | Pass, fail, or invalid run decision |

## Separation Constraints

### Prohibited subscriptions

The following subscriptions are forbidden:

- any runtime autonomy node subscribing to `/truth/*`
- any runtime autonomy node subscribing to `/evaluation/*`
- `operator_station_node` publishing into runtime autonomy topics during deterministic runs

### Logging requirements

`logger_node` must record all runtime autonomy topics, tactical intelligence topics, and `/truth/pose`. It must not synthesize or alter messages in transit.

### Replay requirements

During deterministic replay, `/evaluation/*` topics may be produced only after the replayed autonomy outputs have been frozen for comparison.
