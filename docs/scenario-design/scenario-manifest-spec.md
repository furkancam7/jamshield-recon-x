# Scenario Manifest Specification

## Purpose

The scenario manifest is the single source of truth for a deterministic simulation run. It defines environment, timing, vehicle start state, sensor models, mission route, event injection schedule, logging policy, and the evaluation profile to apply after replay.

## Format

- File format: YAML
- Encoding: UTF-8
- Schema version field: required
- Determinism rule: identical manifest content and identical simulator build must produce the same scheduled event stream

## Top-Level Schema

```yaml
schema_version: 1
scenario_id: string
description: string
seed: uint64
clock:
  step_hz: uint32
  max_duration_s: uint32
  startup_timeout_s: uint32
world:
  world_id: string
  weather_profile: string
vehicle:
  platform_id: string
  initial_pose:
    x_m: float64
    y_m: float64
    z_m: float64
    yaw_deg: float64
mission:
  route:
    - waypoint_id: string
      x_m: float64
      y_m: float64
      z_m: float64
      tolerance_m: float32
sensors:
  camera:
    enabled: bool
    rate_hz: uint32
    noise_model: string
  imu:
    enabled: bool
    rate_hz: uint32
    noise_model: string
  gnss:
    enabled: bool
    rate_hz: uint32
    noise_model: string
events:
  - event_id: string
    type: string
    start_s: float64
    duration_s: float64
    priority: uint32
    target: string
    parameters: map<string, scalar>
logging:
  record_runtime_topics: bool
  record_truth_topics: bool
  bag_profile: string
evaluation:
  acceptance_profile: string
  deterministic_replay_required: bool
```

## Field Requirements

| Field | Required | Rule |
| --- | --- | --- |
| `schema_version` | yes | Must equal the supported manifest schema version |
| `scenario_id` | yes | Must be unique within the repository |
| `seed` | yes | Must be explicit; no implicit random seed allowed |
| `clock.step_hz` | yes | Must be constant for the full run |
| `world.world_id` | yes | Must reference a deterministic simulator world configuration |
| `mission.route` | yes | Must contain at least one waypoint |
| `events` | no | If absent, scenario is nominal |
| `logging.record_truth_topics` | yes | Must be true for evaluation-capable runs |
| `evaluation.acceptance_profile` | yes | Must reference a profile defined in `evaluation/acceptance-criteria.md` |

## Deterministic Scheduling Rules

- Events are sorted by `start_s`, then `priority`, then `event_id`.
- Events with identical sort order are invalid.
- Time is interpreted in simulation seconds from mission start, not wall clock time.
- A manifest must not contain overlapping events that target the same field unless the merge rule is defined by the event type.

## Sensor Configuration Rules

- Sensor rates are fixed for the full run.
- Sensor noise model names must map to versioned noise definitions.
- Sensor disablement is allowed only if the scenario intent requires it and the acceptance profile permits it.

## Mission Route Rules

- Waypoints are evaluated in manifest order.
- Route completion requires all waypoints to be satisfied in sequence.
- Mission continuity decisions may reduce speed or hold position, but they may not reorder waypoints.

## Example Manifest

```yaml
schema_version: 1
scenario_id: denial_corridor_v1
description: "Route crosses a deterministic GNSS denial corridor and requires VIO fallback."
seed: 104729
clock:
  step_hz: 100
  max_duration_s: 720
  startup_timeout_s: 20
world:
  world_id: industrial_corridor_01
  weather_profile: clear_day
vehicle:
  platform_id: recon_x_quad_sim
  initial_pose:
    x_m: 0.0
    y_m: 0.0
    z_m: 30.0
    yaw_deg: 90.0
mission:
  route:
    - waypoint_id: wp_01
      x_m: 60.0
      y_m: 0.0
      z_m: 30.0
      tolerance_m: 2.0
    - waypoint_id: wp_02
      x_m: 180.0
      y_m: 40.0
      z_m: 30.0
      tolerance_m: 2.0
sensors:
  camera:
    enabled: true
    rate_hz: 20
    noise_model: camera_nominal_v1
  imu:
    enabled: true
    rate_hz: 200
    noise_model: imu_nominal_v1
  gnss:
    enabled: true
    rate_hz: 10
    noise_model: gnss_nominal_v1
events:
  - event_id: deny_zone_01
    type: gnss_denial_zone
    start_s: 140.0
    duration_s: 80.0
    priority: 10
    target: gnss
    parameters:
      zone_shape: corridor
      x_min_m: 80.0
      x_max_m: 170.0
      y_half_width_m: 25.0
      drop_probability: 1.0
logging:
  record_runtime_topics: true
  record_truth_topics: true
  bag_profile: full
evaluation:
  acceptance_profile: denial_corridor_profile_v1
  deterministic_replay_required: true
```

## Validation Rules

A scenario manifest is invalid if:

- `seed` is missing
- any event has negative duration
- `clock.max_duration_s` is smaller than route completion lower bound
- evaluation recording is disabled for a benchmarked scenario
- event targets or noise models are not recognized

## Current Baseline Slice

The repository currently implements a narrower baseline-friendly manifest subset for deterministic regression:

- `scenario_id`
- `map_name`
- `vehicle_spawn`
- `route_waypoints`
- `gnss_condition`
- `run_seed`
- `evaluation_profile`
- `metadata`
- optional `runtime_health.sync_quality`
- optional `vio.profile_id`
- optional `vio.reported_state`
- optional `vio.health_score_override`
- optional `config_override`
- optional `mission_timeline`

The current `mission_timeline` form is:

```yaml
mission_timeline:
  tick_period_s: 1.0
  steps:
    - {"repeats": 1, "gnss_condition": "denied"}
    - {"repeats": 2, "gnss_condition": "nominal", "vio": {"profile_id": "nominal_v1"}}
```

Rules for the current slice:

- If `mission_timeline` is omitted, the top-level manifest values are executed as a single deterministic tick.
- `evaluation_profile` is required and must reference a named profile from `configs/eval/default.yaml`.
- Each step must include `repeats >= 1`.
- Step fields are overrides; omitted fields inherit from the top-level manifest.
- `runtime_health.sync_quality` defaults to `1.0`.
- P9 EW risk-map generation derives deterministic pseudo-position samples from `vehicle_spawn`, `route_waypoints`, and the resolved `mission_timeline`.
