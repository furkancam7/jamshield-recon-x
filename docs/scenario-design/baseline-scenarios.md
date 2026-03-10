# Baseline Scenarios

## Purpose

Baseline scenarios are deterministic simulation cases used to validate JamShield Recon-X Sim behavior under controlled conditions.

These scenarios define environmental and sensor conditions through scenario events. They do not directly define mission states. Mission states and localization modes are runtime outcomes produced by the autonomy stack during a deterministic run.

## Scenario Modeling Principles

Baseline scenario documentation separates three concepts:

- scenario events
- localization response
- mission state transitions

These concepts must not be merged into a single path expression.

### Scenario events

Scenario events define what the simulation injects, such as GNSS degradation, GNSS denial, communication degradation, or sensor noise changes.

### Localization response

Localization response describes how confidence-aware localization is expected to behave in terms of localization modes:

- `GNSS_PRIMARY`
- `BLENDED`
- `VIO_PRIMARY`
- `HOLD_LAST_SAFE`

### Mission state transitions

Mission state transitions describe deterministic mission continuity behavior in terms of mission states:

- `MISSION_PREPARE`
- `MISSION_EXECUTE`
- `MISSION_DEGRADED`
- `MISSION_FALLBACK`
- `MISSION_SAFE_HOLD`
- `MISSION_ABORT`
- `MISSION_COMPLETE`

### Deterministic runs

Each baseline scenario is executed as a deterministic run defined by a `scenario_manifest` and a fixed `run_seed`. The same manifest and seed must reproduce the same scenario event timeline and the same mission-level evaluation outcome.

## Scenario Definition Structure

Each baseline scenario is defined by a scenario manifest with a stable structure.

Typical scenario-definition fields are:

- `scenario_id`
- `map_name`
- `vehicle_spawn`
- `route_waypoints`
- `gnss_event_timeline`
- `comm_event_timeline`
- `sensor_noise_profile`
- `run_seed`

These fields describe scenario setup and event scheduling. They do not define runtime mission states or localization modes directly.

## Baseline Scenario Set

### Nominal Mission

Scenario description:

- Nominal route execution with no induced GNSS degradation and nominal sensor conditions.

Scenario events:

- no GNSS degradation
- nominal sensor noise

Expected localization behavior:

- localization remains `GNSS_PRIMARY`

Expected mission state behavior:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_COMPLETE`

### GNSS Degraded Corridor

Scenario description:

- Route passes through a temporary region of reduced GNSS quality without full GNSS denial.

Scenario events:

- `gnss_degraded_corridor`

Expected localization behavior:

- `GNSS_PRIMARY -> BLENDED`

Expected mission state behavior:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_DEGRADED -> MISSION_EXECUTE -> MISSION_COMPLETE`

### GNSS Denied Zone

Scenario description:

- Route intersects a hard GNSS denial region that requires non-GNSS localization continuity.

Scenario events:

- `gnss_denied_zone`

Expected localization behavior:

- `GNSS_PRIMARY -> BLENDED -> VIO_PRIMARY`

Expected mission state behavior:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_FALLBACK -> MISSION_EXECUTE -> MISSION_COMPLETE`

### Spoof-Like Drift Scenario

Scenario description:

- GNSS observations experience a gradual spoof-like drift while the route remains otherwise executable.

Scenario events:

- `spoof_like_drift`

Expected localization behavior:

- `GNSS_PRIMARY -> BLENDED`

Expected mission state behavior:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_DEGRADED -> MISSION_EXECUTE`

### GNSS Denied + Communication Degradation

Scenario description:

- GNSS denial is combined with degraded communication timing or freshness to stress localization resilience and mission continuity.

Scenario events:

- `gnss_denied_zone`
- communication degradation

Expected localization behavior:

- `GNSS_PRIMARY -> VIO_PRIMARY`

Expected mission state behavior:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_FALLBACK -> MISSION_SAFE_HOLD`

## Deterministic Execution

Each baseline scenario must be reproducible from:

- a `scenario_manifest`
- a fixed `run_seed`
- fixed runtime configuration
- fixed simulator timing configuration

Deterministic execution means that the same scenario inputs reproduce the same scenario event ordering and replay-compatible evaluation outcome.

## Scenario Evaluation Role

Baseline scenarios exist to test:

- localization resilience
- trust behavior
- mission continuity decisions

They provide the minimum scenario set for acceptance testing and deterministic regression in simulation-first development.
