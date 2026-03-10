# ADR-003: Trust Engine as Separate Service

## Status

Accepted

## Context

GNSS degradation handling requires at least three distinct concerns:

- measuring GNSS reliability
- assessing non-GNSS estimator health
- deciding how localization sources may contribute to fusion and mission continuity

Embedding all of this logic directly inside `fusion_node` would couple estimation and trust policy, reduce observability, and make tactical reporting harder.

## Decision

Trust management is implemented as a dedicated subsystem composed of:

- `gnss_trust_node` for GNSS trust estimation
- `trust_engine_node` for source confidence and gating decisions

`fusion_node` consumes trust outputs but does not own trust policy.

## Consequences

- Trust logic is observable, testable, and replayable as a first-class subsystem.
- Tactical products such as the EW risk map can use trust outputs directly without reverse-engineering fusion internals.
- Localization and trust can evolve independently as long as topic contracts remain stable.
- A Future hardware integration phase can preserve the same trust subsystem while replacing only the sensor adapters.
