# Event Injection Model

## Purpose

Event injection modifies simulator outputs in a deterministic way to test GNSS trust, confidence-aware localization, mission continuity, and tactical reporting.

## Event Processing Order

For each simulation tick, event effects are applied in this order:

1. base simulator state update
2. sensor noise model application
3. spatial zone effects
4. temporal drift or bias effects
5. communication degradation effects
6. event lifecycle publication on `/events/scenario`

This order is fixed and part of the deterministic replay contract.

## Supported Event Types

### `gnss_degradation_zone`

Applies a bounded reduction in GNSS quality within a spatial volume.

Required parameters:

- zone geometry
- HDOP multiplier
- satellite loss count
- optional jitter amplitude

Expected runtime effect:

- lower `measurement_quality`
- increased covariance in GNSS-derived estimates
- possible transition from `GNSS_PRIMARY` to `GNSS_DEGRADED`

### `gnss_denial_zone`

Applies severe or total GNSS loss within a spatial volume.

Required parameters:

- zone geometry
- drop probability
- reacquisition delay

Expected runtime effect:

- `GNSS_DENIAL_SUSPECT`
- hard gating of GNSS in `trust_engine_node`
- transition to `VIO_PRIMARY` if VIO remains healthy

### `gnss_spoof_like_drift`

Applies a deterministic bias drift to GNSS position and velocity without changing true motion.

Required parameters:

- start bias
- drift rate
- axis selection
- ramp duration
- hold duration
- recovery mode

Expected runtime effect:

- growing innovation mismatch between GNSS and VIO
- `GNSS_SPOOF_LIKE_DRIFT`
- rapid GNSS rejection if thresholds are exceeded

### `communication_degradation`

Applies delay, jitter, or loss to simulator telemetry channels that affect topic freshness.

Required parameters:

- affected topic family
- delay mean
- delay bound
- drop rate

Expected runtime effect:

- `HEALTH_SYNC_STALE` or estimator freshness warnings
- possible transition to `LOCALIZATION_CONTINGENCY` if data age exceeds limits

### `sensor_noise_override`

Overrides a sensor noise model for a fixed interval.

Required parameters:

- sensor target
- noise model identifier

Expected runtime effect:

- controlled change in estimator quality
- no direct state change without passing through trust or health logic

## Spatial Zone Model

Spatial zones are defined in manifest coordinates and support:

- circle
- polygon
- corridor

Zone membership is evaluated from the simulated vehicle pose at each tick. Zones do not read evaluation-only ground truth at runtime; they use simulator-native state within the orchestrator.

## Drift Model

Spoof-like drift follows a four-phase profile:

1. `ramp_in`
2. `hold`
3. `ramp_out`
4. `recovered`

Bias magnitude is deterministic for each tick:

`bias(t) = configured_profile(seed, elapsed_time)`

The profile function must be pure with respect to manifest parameters and seed.

## Event Composition Rules

- Multiple events on different targets may overlap.
- Multiple events on the same target are allowed only if their effect operators are commutative or explicitly prioritized.
- Denial supersedes degradation on GNSS targets.
- Spoof-like drift composes after degradation so that quality reduction and bias can coexist.
- Communication degradation cannot alter scenario event publication ordering.

## Lifecycle Publication

Each event publishes:

- `START` at activation
- `ACTIVE` on each state change of internal parameters, if any
- `END` at completion

These lifecycle messages are part of the replay evidence and must be identical across reruns with the same manifest.
