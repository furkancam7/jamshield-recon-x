# Message Schemas

## Common Conventions

- `timestamp_ns`: unsigned 64-bit simulation timestamp in nanoseconds
- `frame_id`: reference frame identifier
- `run_id`: immutable identifier for a simulation run
- `scenario_id`: identifier from the scenario manifest
- `reason_codes`: ordered list of codes defined in `reason-codes.md`

## `SensorImageFrame`

```yaml
SensorImageFrame:
  timestamp_ns: uint64
  frame_id: string
  width_px: uint32
  height_px: uint32
  encoding: string
  sequence_id: uint64
  exposure_us: uint32
  image_uri: string
```

## `SensorImuSample`

```yaml
SensorImuSample:
  timestamp_ns: uint64
  frame_id: string
  sequence_id: uint64
  angular_velocity_radps:
    x: float64
    y: float64
    z: float64
  linear_acceleration_mps2:
    x: float64
    y: float64
    z: float64
  covariance:
    angular_velocity: [float64, float64, float64]
    linear_acceleration: [float64, float64, float64]
```

## `SensorGnssFix`

```yaml
SensorGnssFix:
  timestamp_ns: uint64
  frame_id: string
  sequence_id: uint64
  latitude_deg: float64
  longitude_deg: float64
  altitude_m: float64
  velocity_ned_mps:
    north: float64
    east: float64
    down: float64
  hdop: float32
  vdop: float32
  satellites_used: uint16
  carrier_lock_ratio: float32
  spoof_suspect_flag: bool
```

## `SyncStatus`

```yaml
SyncStatus:
  timestamp_ns: uint64
  sim_time_ok: bool
  monotonic_ok: bool
  max_skew_ms: float32
  missing_topics: [string]
  severity: string
  reason_codes: [string]
```

## `LocalizationEstimate`

```yaml
LocalizationEstimate:
  timestamp_ns: uint64
  frame_id: string
  child_frame_id: string
  source: string
  pose:
    x_m: float64
    y_m: float64
    z_m: float64
    roll_rad: float64
    pitch_rad: float64
    yaw_rad: float64
  velocity_mps:
    x: float64
    y: float64
    z: float64
  covariance_diag: [float64, float64, float64, float64, float64, float64]
  is_valid: bool
  freshness_ms: float32
  quality_score: float32
```

## `LocalizationSourceStatus`

```yaml
LocalizationSourceStatus:
  timestamp_ns: uint64
  active_mode: string
  gnss_in_use: bool
  vio_in_use: bool
  gnss_gated: bool
  vio_gated: bool
  continuity_ok: bool
  reason_codes: [string]
```

## `GnssTrustReport`

```yaml
GnssTrustReport:
  timestamp_ns: uint64
  gnss_trust: float32
  measurement_quality: float32
  temporal_stability: float32
  kinematic_consistency: float32
  innovation_consistency: float32
  anomaly_class: string
  denial_suspect: bool
  spoof_suspect: bool
  reason_codes: [string]
```

## `SourceConfidenceReport`

```yaml
SourceConfidenceReport:
  timestamp_ns: uint64
  c_gnss: float32
  c_vio: float32
  recommended_mode: string
  hysteresis_state: string
  reason_codes: [string]
```

## `TrustDecision`

```yaml
TrustDecision:
  timestamp_ns: uint64
  selected_primary_source: string
  allow_gnss_update: bool
  allow_vio_update: bool
  transition_pending: bool
  primary_reason_code: string
  reason_codes: [string]
```

## `MissionState`

```yaml
MissionState:
  timestamp_ns: uint64
  state: string
  action: string
  route_progress_pct: float32
  localization_mode: string
  primary_reason_code: string
  reason_codes: [string]
```

## `MissionAction`

```yaml
MissionAction:
  timestamp_ns: uint64
  command: string
  speed_limit_mps: float32
  hold_position:
    x_m: float64
    y_m: float64
    z_m: float64
  reason_codes: [string]
```

## `MissionExplanation`

```yaml
MissionExplanation:
  timestamp_ns: uint64
  previous_state: string
  new_state: string
  c_gnss: float32
  c_vio: float32
  primary_reason_code: string
  reason_codes: [string]
  narrative: string
```

## `HealthStatus`

```yaml
HealthStatus:
  timestamp_ns: uint64
  subsystem: string
  severity: string
  stale_duration_ms: float32
  primary_reason_code: string
  reason_codes: [string]
```

## `EwRiskMap`

```yaml
EwRiskMap:
  timestamp_ns: uint64
  frame_id: string
  cell_size_m: float32
  width_cells: uint32
  height_cells: uint32
  origin:
    x_m: float64
    y_m: float64
  risk_cells: [float32]
  evidence_codes: [string]
```

## `TacticalSummary`

```yaml
TacticalSummary:
  timestamp_ns: uint64
  mission_state: string
  mission_confidence: float32
  localization_mode: string
  ew_risk_level: string
  affected_area_count: uint32
  ew_corridor_cost: float32
  primary_reason_code: string
  reason_codes: [string]
  advisory_code: string
  advisory_text: string
  summary_text: string
```

## `ScenarioEvent`

```yaml
ScenarioEvent:
  timestamp_ns: uint64
  event_id: string
  phase: string
  event_type: string
  target: string
  parameters: map<string, string>
```

## `FaultEvent`

```yaml
FaultEvent:
  timestamp_ns: uint64
  event_id: string
  subsystem: string
  severity: string
  primary_reason_code: string
  reason_codes: [string]
  details: string
```

## `GroundTruthPose`

```yaml
GroundTruthPose:
  timestamp_ns: uint64
  frame_id: string
  child_frame_id: string
  pose:
    x_m: float64
    y_m: float64
    z_m: float64
    roll_rad: float64
    pitch_rad: float64
    yaw_rad: float64
  velocity_mps:
    x: float64
    y: float64
    z: float64
```

## `EvaluationRunMetadata`

```yaml
EvaluationRunMetadata:
  run_id: string
  scenario_id: string
  manifest_hash: string
  replay_hash: string
  deterministic_replay_passed: bool
  invalid_run: bool
  invalid_reason_codes: [string]
```

## `EvaluationMetric`

```yaml
EvaluationMetric:
  run_id: string
  scenario_id: string
  metric_name: string
  metric_value: float64
  units: string
  passed: bool
  threshold_value: float64
```

## `EvaluationVerdict`

```yaml
EvaluationVerdict:
  run_id: string
  scenario_id: string
  verdict: string
  primary_reason_code: string
  reason_codes: [string]
  mission_success: bool
```
