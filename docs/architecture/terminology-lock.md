# Terminology Lock

This document is the single authoritative terminology reference for JamShield Recon-X Sim. All repository documentation, interfaces, logs, scenario definitions, and evaluation artifacts must use the terms in this file exactly.

## 1. Terminology Principles

Terminology consistency is a systems requirement, not a style preference.

- Deterministic replay depends on stable names for states, modes, signals, and reason codes.
- Architecture review depends on shared definitions across runtime autonomy, tactical intelligence, and evaluation systems.
- Simulation-based verification depends on exact matching between scenario intent, runtime outputs, and evaluation reports.
- Ground truth separation depends on precise distinction between runtime autonomy topics and evaluation-only topics.

Normative rules:

- A term defined here has one meaning in the repository.
- A concept must not have multiple names across files.
- A name must not refer to multiple concepts.
- New canonical terms must be added here before they appear elsewhere.

## 2. Node Naming Standard

Node names must use `snake_case` and end with `_node`.

| Node | Locked meaning |
| --- | --- |
| `scenario_orchestrator_node` | Loads the scenario manifest, applies deterministic event scheduling, and manages scenario lifecycle. |
| `camera_adapter_node` | Converts simulator camera output into hardware-portable ROS2 image messages. |
| `imu_adapter_node` | Converts simulator IMU output into hardware-portable ROS2 inertial messages. |
| `gnss_adapter_node` | Converts simulator GNSS output into GNSS sensor messages and GNSS-derived localization estimates. |
| `ground_truth_adapter_node` | Publishes evaluation-only ground truth from simulation. |
| `time_sync_node` | Enforces simulation clock consistency and reports timestamp alignment status. |
| `gnss_trust_node` | Computes GNSS trust and GNSS anomaly indicators from GNSS behavior. |
| `vio_node` | Produces VIO localization estimates and VIO quality indicators from camera and IMU data. |
| `fusion_node` | Produces the fused localization estimate and the active localization source status. |
| `trust_engine_node` | Aggregates trust signals and publishes source confidence, localization confidence, and mission confidence outputs for downstream autonomy logic. |
| `mission_continuity_node` | Applies deterministic mission continuity logic and publishes mission state, action, and explanation. |
| `sitl_bridge_node` | Translates mission actions into simulator control inputs. |
| `ew_risk_map_node` | Builds an EW risk map from navigation degradation evidence. |
| `tactical_summary_node` | Produces concise tactical summaries for the operator. |
| `logger_node` | Records runtime, tactical, and evaluation-only streams for deterministic replay and analysis. |
| `evaluation_node` | Replays recorded runs and computes evaluation metrics and verdicts. |
| `health_monitor_node` | Detects freshness, heartbeat, sync, and estimator health faults. |
| `operator_station_node` | Displays mission, tactical, and evaluation outputs without driving runtime autonomy decisions. |

## 3. Topic Families

Only the following topic families are allowed.

| Topic family | Purpose | Allowed publishers |
| --- | --- | --- |
| `/sensors/*` | Raw or near-raw simulator-derived sensor streams used by runtime autonomy. | `camera_adapter_node`, `imu_adapter_node`, `gnss_adapter_node` |
| `/sync/*` | Simulation time alignment, freshness, and sync health outputs. | `time_sync_node` |
| `/localization/*` | Source-specific and fused localization estimates plus source status outputs. | `gnss_adapter_node`, `vio_node`, `fusion_node` |
| `/trust/*` | GNSS trust, source confidence, localization confidence, and mission confidence outputs. | `gnss_trust_node`, `trust_engine_node` |
| `/mission/*` | Mission continuity state, action, explanation, and health outputs. | `mission_continuity_node`, `health_monitor_node` |
| `/tactical/*` | Tactical intelligence products for operator interpretation. | `ew_risk_map_node`, `tactical_summary_node` |
| `/events/*` | Scenario lifecycle events and detected fault events. | `scenario_orchestrator_node`, `health_monitor_node` |
| `/truth/*` | Evaluation-only ground truth published from simulation. | `ground_truth_adapter_node` |
| `/evaluation/*` | Offline replay metadata, metrics, and verdict outputs. | `evaluation_node` |

Locked constraints:

- `/truth/*` must never be consumed by runtime autonomy nodes.
- `/truth/*` may be consumed only by `logger_node` and `evaluation_node`.
- `/evaluation/*` is evaluation output, not runtime input.
- Mission decisions must be published only under `/mission/*`.
- `operator_station_node` is read-only during deterministic runs.

## 4. Localization Modes

Localization modes describe which localization source is currently authoritative inside confidence-aware localization. They are not scenario terms and they are not reason codes.

| Localization mode | Meaning |
| --- | --- |
| `GNSS_PRIMARY` | GNSS is the primary localization source because GNSS trust is high enough for nominal operation. |
| `BLENDED` | GNSS and VIO are both accepted and fused because both sources satisfy blend entry criteria. |
| `VIO_PRIMARY` | VIO is the primary localization source because GNSS trust is too low for GNSS-led operation. |
| `HOLD_LAST_SAFE` | The system is preserving the last safe localization state because neither GNSS nor VIO meets the minimum active-use threshold. |

Usage rules:

- `GNSS_PRIMARY`, `BLENDED`, `VIO_PRIMARY`, and `HOLD_LAST_SAFE` are localization modes only.
- These terms must not be used as reason codes.
- These terms should appear in localization or source-status fields, not as topic family names.

## 5. Mission States

Mission states describe mission continuity decisions, not estimator internals.

| Mission state | Meaning |
| --- | --- |
| `MISSION_PREPARE` | The system is waiting for a valid initial mission start condition. |
| `MISSION_EXECUTE` | The mission is continuing with acceptable localization continuity. |
| `MISSION_DEGRADED` | The mission is continuing under degraded but still controlled localization conditions. |
| `MISSION_FALLBACK` | The mission is continuing under fallback localization authority, typically VIO-led. |
| `MISSION_SAFE_HOLD` | The mission is holding position because localization continuity is temporarily insufficient. |
| `MISSION_ABORT` | The mission is terminated because safety or continuity criteria can no longer be met. |
| `MISSION_COMPLETE` | The mission route has completed without terminal failure. |

Conceptual trigger logic:

- `MISSION_PREPARE` is active before the first usable localization state is declared.
- `MISSION_EXECUTE` is active during nominal mission continuation.
- `MISSION_DEGRADED` is active when GNSS trust drops but mission continuation remains acceptable.
- `MISSION_FALLBACK` is active when VIO or another non-GNSS source becomes the primary basis for mission continuity.
- `MISSION_SAFE_HOLD` is active when neither source currently supports safe forward progress.
- `MISSION_ABORT` is active when contingency persists beyond deterministic abort limits or health becomes critical.
- `MISSION_COMPLETE` is active after route completion.

Naming rule:

- Mission states must use uppercase with underscores.
- Localization modes and mission states must remain distinct in new documentation and interfaces.

## 6. Trust Signals

Trust signals are scalar or categorical runtime signals used to evaluate source reliability and mission continuity.

| Trust signal | Meaning |
| --- | --- |
| `gnss_trust` | The bounded trust score assigned to GNSS observations. |
| `vio_trust` | The bounded trust score assigned to VIO localization quality. |
| `sync_quality` | The bounded assessment of timing alignment and message freshness across required inputs. |
| `localization_confidence` | The bounded confidence assigned to the currently active fused localization output. |
| `mission_confidence` | The bounded assessment that mission continuity can continue without entering contingency. |

Usage rules:

- Trust signal names must use `snake_case`.
- A trust signal is not a mission state.
- A trust signal is not a localization mode.
- Trust signals may feed decisions, but they do not replace explicit reason codes.

## 7. Reason Codes

Reason codes provide short causal explanations for trust decisions, mission transitions, and evaluation verdicts.

Canonical format:

- `snake_case`
- short and specific
- causal, not narrative

Controlled set:

| Reason code | Locked meaning |
| --- | --- |
| `gnss_jump_detected` | GNSS position changed discontinuously beyond the allowed threshold. |
| `gnss_velocity_inconsistent` | GNSS velocity is inconsistent with inertial or VIO motion. |
| `heading_mismatch` | Heading inferred from different sources is inconsistent. |
| `low_feature_count` | Visual feature support is insufficient for stable VIO tracking. |
| `high_reprojection_error` | VIO reprojection residuals exceed the allowed bound. |
| `track_continuity_drop` | Visual or fused tracking continuity dropped below the required limit. |
| `sync_quality_low` | Time alignment or freshness fell below the minimum acceptable threshold. |
| `gnss_denial_suspected` | GNSS behavior matches a denial-like loss pattern. |
| `spoof_like_drift_detected` | GNSS behavior matches a spoof-like drift pattern. |
| `localization_confidence_low` | Fused localization confidence fell below the continuity threshold. |
| `mission_contingency_timeout` | A contingency state exceeded the deterministic timeout. |
| `ground_truth_missing` | Required evaluation-only ground truth is missing or incomplete. |
| `replay_divergence_detected` | Deterministic replay diverged from the recorded run. |

Usage rules:

- Reason codes explain why something happened.
- Reason codes must not encode severity levels or state names.
- Reason codes must remain stable across runtime logs and evaluation outputs.
- Existing uppercase reason-code examples in older documents are legacy forms and are superseded by this file.

## 8. Scenario Terminology

Scenario terminology defines the simulation vocabulary used by manifests, event models, and baseline scenarios.

| Term | Locked meaning |
| --- | --- |
| `scenario_manifest` | The canonical configuration file that defines a deterministic simulation run. |
| `gnss_denied_zone` | A spatial region in which GNSS observations are fully or near-fully denied. |
| `gnss_degraded_corridor` | A route segment or region in which GNSS quality is intentionally reduced but not fully denied. |
| `spoof_like_drift` | A deterministic GNSS bias drift pattern that imitates spoof-like navigation corruption. |
| `sensor_noise_profile` | A named and versioned sensor noise configuration used by a scenario manifest. |
| `deterministic_run` | A run that is fully defined by fixed manifest inputs, deterministic scheduling, and reproducible execution order. |

Usage rules:

- `scenario_manifest` is the authoritative scenario definition term.
- Scenario terms must describe simulation conditions, not runtime conclusions.
- `ground_truth` remains evaluation-only even when scenario logic has simulator access to world state.

## 9. Evaluation Terminology

Evaluation terms define offline measurement and verdict vocabulary.

| Term | Locked meaning |
| --- | --- |
| `ATE` | Absolute Trajectory Error between runtime localization output and evaluation-only ground truth. |
| `RPE` | Relative Pose Error over a fixed time horizon between runtime localization output and evaluation-only ground truth. |
| `drift` | Accumulated terminal localization error relative to traveled path length. |
| `localization_continuity` | The fraction of mission time during which valid localization remained continuously available. |
| `fallback_reaction_time` | The elapsed time between confirmed GNSS untrustworthy behavior and successful fallback localization activation. |
| `mission_success_rate` | The fraction of evaluated runs that complete mission objectives without invalidation or terminal failure. |

Usage rules:

- Evaluation terms belong to offline replay and analysis.
- Evaluation terms must not appear as runtime autonomy inputs.
- Evaluation always uses evaluation-only ground truth.

## 10. Terminology Governance

Future terminology changes must follow these rules:

- New canonical terms must be added to this file before they are used anywhere else.
- Renaming a node, mission state, localization mode, trust signal, or reason code requires architecture review.
- Renaming a repository-wide term with interface impact requires an ADR.
- Topic families cannot change without architecture review.
- `/truth/*` and `/evaluation/*` boundaries cannot change without an ADR.
- Legacy synonyms should be removed, not preserved indefinitely.
- If a term is deprecated, this file must state the replacement term explicitly.
