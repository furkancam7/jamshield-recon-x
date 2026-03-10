# Baseline Scenarios

## Purpose

Baseline scenarios define deterministic simulation cases used to validate JamShield Recon-X Sim under controlled conditions.

Each scenario separates:

- scenario events
- localization mode progression
- mission state progression

## Nominal Mission

Scenario events:

- no GNSS degradation

Expected localization modes:

- `GNSS_PRIMARY`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_COMPLETE`

## GNSS Degraded Corridor

Scenario events:

- temporary GNSS degradation zone

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_DEGRADED -> MISSION_EXECUTE -> MISSION_COMPLETE`

## GNSS Denied Zone

Scenario events:

- hard GNSS denial region

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED -> VIO_PRIMARY`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_FALLBACK -> MISSION_EXECUTE -> MISSION_COMPLETE`

## Spoof-like Drift Scenario

Scenario events:

- gradual GNSS drift

Expected localization modes:

- `GNSS_PRIMARY -> BLENDED`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_DEGRADED`

## GNSS Denied + Communication Degradation

Scenario events:

- GNSS denial
- communication degradation

Expected localization modes:

- `GNSS_PRIMARY -> VIO_PRIMARY`

Expected mission states:

- `MISSION_PREPARE -> MISSION_EXECUTE -> MISSION_FALLBACK -> MISSION_SAFE_HOLD`
