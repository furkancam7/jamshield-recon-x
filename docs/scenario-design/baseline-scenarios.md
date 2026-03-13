# Baseline Scenarios

## Purpose

Baseline scenarios define deterministic simulation cases used to validate JamShield Recon-X Sim under controlled conditions.

Each scenario separates:

- scenario events
- localization mode progression
- mission state progression

Each baseline scenario is authored as a `scenario_manifest` and executed as a `deterministic_run`.

## Nominal Mission

Scenario events:

- no GNSS degradation

Expected localization modes:

- `GNSS_PRIMARY`

Expected mission states:

- Current executable slice: `MISSION_EXECUTE`

## GNSS Degraded Corridor

Scenario events:

- `gnss_degraded_corridor`

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED`

Expected mission states:

- Current executable slice: `MISSION_EXECUTE -> MISSION_DEGRADED -> MISSION_EXECUTE`

## GNSS Denied Zone

Scenario events:

- `gnss_denied_zone`

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED -> VIO_PRIMARY`

Expected mission states:

- Current executable slice: `MISSION_EXECUTE -> MISSION_FALLBACK`

## Spoof-like Drift Scenario

Scenario events:

- `spoof_like_drift`

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED`

Expected mission states:

- Current executable slice: `MISSION_DEGRADED` or `MISSION_FALLBACK`, depending on resolved trust and VIO state

## GNSS Denied + Communication Degradation

Scenario events:

- `gnss_denied_zone`
- communication degradation

Expected localization modes:

- `GNSS_PRIMARY -> VIO_PRIMARY`

Expected mission states:

- Current executable slice: `MISSION_FALLBACK -> MISSION_SAFE_HOLD` or `MISSION_ABORT`, depending on continuity guards
