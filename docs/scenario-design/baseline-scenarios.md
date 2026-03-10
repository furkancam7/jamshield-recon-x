# Baseline Scenarios

## Purpose

Baseline scenarios are deterministic simulation cases used to validate JamShield Recon-X Sim under controlled conditions.

Each baseline scenario defines injected scenario conditions, expected localization response, and expected mission state progression for simulation-first verification.

## Scenario Modeling Principles

Baseline scenario documentation separates three concepts:

- scenario events
- localization response
- mission state progression

These concepts must not appear in the same state chain.

### Scenario events

Scenario events define what the simulation injects into the run, such as GNSS degradation, GNSS denial, spoof-like drift, communication degradation, or sensor noise conditions.

### Localization response

Localization response describes the expected runtime progression of localization modes:

- `GNSS_PRIMARY`
- `BLENDED`
- `VIO_PRIMARY`
- `HOLD_LAST_SAFE`

### Mission state progression

Mission state progression describes the expected deterministic mission continuity behavior:

- `MISSION_PREPARE`
- `MISSION_EXECUTE`
- `MISSION_DEGRADED`
- `MISSION_FALLBACK`
- `MISSION_SAFE_HOLD`
- `MISSION_ABORT`
- `MISSION_COMPLETE`

## Scenario Manifest Structure

Each baseline scenario is defined by a `scenario_manifest` with stable scenario-definition fields.

Typical fields include:

- `scenario_id`
- `map_name`
- `vehicle_spawn`
- `route_waypoints`
- `gnss_event_timeline`
- `comm_event_timeline`
- `sensor_noise_profile`
- `run_seed`

These fields describe scenario setup and deterministic event scheduling. They do not directly define mission states or localization modes.

## Baseline Scenario Set

### Nominal Mission

Scenario events:

- no GNSS degradation

Expected localization modes:

- `GNSS_PRIMARY`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_COMPLETE`

### GNSS Degraded Corridor

Scenario events:

- temporary GNSS degradation zone

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_DEGRADED -> MISSION_EXECUTE -> MISSION_COMPLETE`

### GNSS Denied Zone

Scenario events:

- GNSS denied region

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED -> VIO_PRIMARY`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_FALLBACK -> MISSION_EXECUTE -> MISSION_COMPLETE`

### Spoof-Like Drift Scenario

Scenario events:

- gradual GNSS drift

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_DEGRADED`

### GNSS Denied + Communication Degradation

Scenario events:

- GNSS denial
- communication degradation

Expected localization modes:

- `GNSS_PRIMARY -> VIO_PRIMARY`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_FALLBACK -> MISSION_SAFE_HOLD`

## Deterministic Execution

Each baseline scenario must be reproducible using:

- a `scenario_manifest`
- a fixed `run_seed`
- fixed simulator timing
- fixed runtime configuration

Deterministic execution means the same scenario inputs reproduce the same scenario event ordering and replay-compatible evaluation outcome.

## Scenario Evaluation Role

Baseline scenarios validate:

- localization resilience
- trust behavior
- mission continuity decisions

They define the minimum scenario set used for acceptance testing and deterministic regression in simulation.
