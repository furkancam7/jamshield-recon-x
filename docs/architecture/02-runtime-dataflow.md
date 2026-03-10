# Runtime Data Flow

## Primary Runtime Flow

The runtime graph is organized around a single deterministic simulation clock.

1. `scenario_orchestrator_node` loads the scenario manifest, sets the seed, schedules event injection, and initializes simulator state.
2. `camera_adapter_node`, `imu_adapter_node`, and `gnss_adapter_node` translate simulator outputs into `/sensors/*` topics.
3. `time_sync_node` validates timestamp monotonicity and data alignment, then publishes `/sync/status`.
4. `gnss_trust_node` consumes `/sensors/gnss/fix` and the non-GNSS motion context needed for residual checks, then publishes `/trust/gnss`.
5. `vio_node` consumes camera and IMU data and publishes `/localization/vio/estimate`.
6. `gnss_adapter_node` also publishes a GNSS-derived navigation estimate on `/localization/gnss/estimate`.
7. `trust_engine_node` consumes `/trust/gnss`, `/localization/vio/estimate`, `/localization/source_status`, and `/mission/health`, then publishes `/trust/source_confidence` and `/trust/decision`.
8. `fusion_node` consumes GNSS and VIO estimates plus `/trust/source_confidence`, applies confidence-aware localization rules, and publishes `/localization/fused/estimate` and `/localization/source_status`.
9. `mission_continuity_node` consumes `/localization/fused/estimate`, `/trust/decision`, `/mission/health`, and scenario route progress, then publishes `/mission/state`, `/mission/action`, and `/mission/explanation`.
10. `sitl_bridge_node` translates `/mission/action` into simulator commands.
11. `ew_risk_map_node` consumes trust and localization degradation signals and publishes `/tactical/ew_risk_map`.
12. `tactical_summary_node` merges mission state, trust status, and EW risk map outputs into `/tactical/summary`.
13. `operator_station_node` visualizes mission and tactical outputs without influencing runtime autonomy.
14. `logger_node` records runtime topics and evaluation-only ground truth for deterministic replay.

## Data Class Separation

### Runtime autonomy topics

Runtime autonomy topics are:

- `/sensors/*`
- `/sync/*`
- `/localization/*`
- `/trust/*`
- `/mission/*`
- `/events/*`

These topics drive decisions during the live run.

### Tactical intelligence topics

Tactical intelligence topics are:

- `/tactical/*`

These are derived products for operator interpretation and post-run analysis.

### Evaluation topics

Evaluation topics are:

- `/truth/*`
- `/evaluation/*`

These are prohibited from influencing runtime autonomy.

## Confidence-Aware Localization Flow

`fusion_node` implements a deterministic mode table:

- `GNSS_PRIMARY`: `c_gnss >= 0.75` and `c_vio >= 0.40`
- `BLENDED`: `0.45 <= c_gnss < 0.75` and `c_vio >= 0.50`
- `VIO_PRIMARY`: `c_gnss < 0.45` and `c_vio >= 0.55`
- `HOLD_LAST_SAFE`: `c_gnss < 0.20` and `c_vio < 0.55`

Where:

- `c_gnss` comes from GNSS trust after hard penalties for denial or spoof-like signatures
- `c_vio` comes from VIO tracking quality, IMU consistency, and freshness checks

Mode transitions are delayed by fixed dwell timers to avoid thrashing:

- degrade dwell: `1.0 s`
- fallback dwell: `0.5 s`
- recovery dwell: `3.0 s` from `BLENDED`, `5.0 s` from `VIO_PRIMARY`

## EW Risk Map Flow

`ew_risk_map_node` consumes:

- GNSS trust gradients over time
- source confidence transitions
- mission path location

It emits a spatial risk map that marks areas where navigation degradation repeatedly occurred. The output is tactical only. It is not fed back into runtime autonomy during the same run.

## Health and Fault Flow

`health_monitor_node` monitors:

- node heartbeats
- topic freshness
- sync drift
- estimator stall conditions

It publishes:

- `/mission/health` for deterministic mission continuity decisions
- `/events/faults` for logging and investigation

## Deterministic Replay Flow

Deterministic replay preserves the original ordering of:

- sensor messages
- scenario events
- trust outputs
- mission continuity transitions

Replay flow is:

1. `logger_node` provides the recorded stream.
2. `evaluation_node` replays the stream through the same node graph or a replay harness with identical parameters.
3. Runtime outputs are compared against recorded outputs for state and reason-code equality.
4. Evaluation metrics are computed against evaluation-only ground truth and published on `/evaluation/*`.

Any divergence in mission state sequence, trust decision sequence, or fused localization hash invalidates deterministic replay.
