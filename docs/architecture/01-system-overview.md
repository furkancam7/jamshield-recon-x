# System Overview

## Purpose

JamShield Recon-X Sim is a simulation-first autonomy stack designed to maintain mission continuity when GNSS quality degrades, is denied, or exhibits spoof-like behavior. The stack detects navigation anomalies, computes GNSS trust, shifts localization authority to Visual-Inertial Odometry (VIO) when required, fuses available estimates with confidence-aware localization logic, and produces deterministic tactical and evaluation artifacts.

## Scope Boundary

Implemented system scope:

- simulated sensor ingestion
- deterministic runtime autonomy
- tactical intelligence derived from runtime signals
- deterministic replay and offline evaluation

Excluded from current scope:

- real sensor drivers
- real vehicle actuation interfaces
- field validation

These excluded items belong to the Future hardware integration phase.

## System Roles

### Runtime autonomy

Runtime autonomy converts sensor observations into localization, trust decisions, and mission actions. It is composed of:

- `time_sync_node`
- `gnss_trust_node`
- `vio_node`
- `fusion_node`
- `trust_engine_node`
- `mission_continuity_node`
- `health_monitor_node`
- `sitl_bridge_node`

### Tactical intelligence

Tactical intelligence converts navigation degradation patterns into operator-facing summaries without closing the control loop. It is composed of:

- `ew_risk_map_node`
- `tactical_summary_node`

### Evaluation systems

Evaluation systems consume recorded runtime outputs plus evaluation-only ground truth. They never influence runtime autonomy. They are composed of:

- `ground_truth_adapter_node`
- `logger_node`
- `evaluation_node`

### Operator interface

The operator interface is read-only for deterministic runs. It is composed of:

- `operator_station_node`

## Layered Architecture

### Layer 1: Scenario control and simulation bridge

- `scenario_orchestrator_node`
- `sitl_bridge_node`

This layer loads the scenario manifest, applies deterministic event scheduling, and binds the ROS2 graph to the simulator.

### Layer 2: Sensor ingress

- `camera_adapter_node`
- `imu_adapter_node`
- `gnss_adapter_node`
- `ground_truth_adapter_node`

This layer translates simulator-native streams into hardware-portable ROS2 contracts.

### Layer 3: Time and health supervision

- `time_sync_node`
- `health_monitor_node`

This layer enforces a common simulation clock and detects timing, heartbeat, and data freshness faults.

### Layer 4: Localization and trust

- `gnss_trust_node`
- `vio_node`
- `trust_engine_node`
- `fusion_node`

This layer estimates localization state and source confidence. `gnss_trust_node` produces GNSS trust from GNSS behavior. `trust_engine_node` converts trust and estimator health into deterministic source selection inputs. `fusion_node` produces the fused navigation estimate.

### Layer 5: Mission continuity and tactical products

- `mission_continuity_node`
- `ew_risk_map_node`
- `tactical_summary_node`

This layer preserves mission continuity using deterministic state transitions and emits tactical outputs for the operator.

### Layer 6: Logging, replay, and evaluation

- `logger_node`
- `evaluation_node`

This layer provides deterministic replay, metrics extraction, and regression evidence.

## Control Philosophy

### GNSS trust

GNSS trust is a bounded score in `[0.0, 1.0]` derived from fixed-weight checks:

- measurement quality
- temporal stability
- kinematic consistency
- innovation consistency against non-GNSS motion estimates

The weighting is static by design so that the same input stream always produces the same GNSS trust output.

### Confidence-aware localization

Confidence-aware localization uses two principles:

- low-confidence sources are hard-gated out instead of weakly blended
- transitions between source modes use explicit hysteresis and dwell timers

This prevents oscillation during borderline GNSS conditions and keeps mission continuity explainable.

### Mission continuity

Mission continuity is the deterministic control policy that maps localization quality and system health to mission action. It must be explainable from recorded inputs. The policy is state-machine based and cannot depend on opaque learned behavior.

## Ground Truth Isolation

`ground_truth_adapter_node` exists only to publish evaluation-only ground truth on `/truth/*`. The only approved consumers are:

- `logger_node`
- `evaluation_node`

Runtime autonomy nodes and tactical nodes must not subscribe to `/truth/*`.

## Replay and Evaluation Model

Every simulation run is expected to record:

- scenario events
- raw sensor streams
- trust outputs
- localization outputs
- mission continuity decisions
- tactical outputs
- evaluation-only ground truth

Deterministic replay re-executes the autonomy path against the recorded stream and compares outputs against the original run. Offline evaluation then computes metrics against evaluation-only ground truth.
