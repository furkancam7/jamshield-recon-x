# Mission State Machine

## Purpose

`mission_continuity_node` implements deterministic mission continuity. It consumes localization confidence, trust decisions, and health status, then emits a single mission state, a bounded mission action, and an explanation with reason codes.

## States

| State | Meaning | Default Action |
| --- | --- | --- |
| `PREPARE` | Sensors are starting, route is loaded, localization authority not yet declared | `HOLD_POSITION` |
| `GNSS_PRIMARY` | GNSS trust is high enough for GNSS-led localization | `CONTINUE_ROUTE` |
| `GNSS_DEGRADED` | GNSS trust is reduced but not yet fully rejected | `REDUCE_SPEED` |
| `VIO_PRIMARY` | GNSS is untrusted and VIO is the active localization source | `CONTINUE_ROUTE` |
| `LOCALIZATION_CONTINGENCY` | Neither GNSS nor VIO currently satisfies operational confidence limits | `HOLD_POSITION` |
| `MISSION_ABORT` | Localization or system health is insufficient to continue safely | `TERMINATE_MISSION` |
| `MISSION_COMPLETE` | Route completed without violating terminal conditions | `HOLD_POSITION` |

## Transition Inputs

The state machine uses only:

- `/trust/decision`
- `/localization/fused/estimate`
- `/mission/health`
- scenario route progress from `/events/scenario`

Operator commands are intentionally excluded from deterministic runs.

## Deterministic Thresholds

| Condition | Threshold |
| --- | --- |
| GNSS nominal entry | `c_gnss >= 0.75` for `3.0 s` |
| GNSS degrade entry | `c_gnss < 0.75` for `1.0 s` |
| VIO fallback entry | `c_gnss < 0.45` and `c_vio >= 0.55` for `0.5 s` |
| Recovery from VIO | `c_gnss >= 0.85` and innovation stable for `5.0 s` |
| Contingency entry | `c_gnss < 0.20` and `c_vio < 0.55`, or sync lost for `> 0.25 s` |
| Abort entry | contingency persists for `10.0 s`, or health state becomes `CRITICAL` |

## Transition Table

| From | To | Trigger |
| --- | --- | --- |
| `PREPARE` | `GNSS_PRIMARY` | GNSS nominal entry threshold satisfied |
| `PREPARE` | `VIO_PRIMARY` | VIO fallback entry threshold satisfied before GNSS nominal entry |
| `GNSS_PRIMARY` | `GNSS_DEGRADED` | GNSS degrade entry threshold satisfied |
| `GNSS_DEGRADED` | `GNSS_PRIMARY` | GNSS nominal entry threshold satisfied |
| `GNSS_DEGRADED` | `VIO_PRIMARY` | VIO fallback entry threshold satisfied |
| `GNSS_PRIMARY` | `VIO_PRIMARY` | Immediate fallback if spoof-like behavior is confirmed and VIO is healthy |
| `GNSS_PRIMARY` | `LOCALIZATION_CONTINGENCY` | Contingency entry threshold satisfied |
| `GNSS_DEGRADED` | `LOCALIZATION_CONTINGENCY` | Contingency entry threshold satisfied |
| `VIO_PRIMARY` | `GNSS_PRIMARY` | Recovery from VIO threshold satisfied |
| `VIO_PRIMARY` | `LOCALIZATION_CONTINGENCY` | VIO freshness, tracking, or sync health drops below limits |
| `LOCALIZATION_CONTINGENCY` | `VIO_PRIMARY` | VIO becomes healthy before abort timeout |
| `LOCALIZATION_CONTINGENCY` | `GNSS_PRIMARY` | GNSS becomes healthy before abort timeout |
| `LOCALIZATION_CONTINGENCY` | `MISSION_ABORT` | Abort entry threshold satisfied |
| any non-terminal state | `MISSION_COMPLETE` | Final waypoint reached with valid localization |

## Explainability Requirements

Every state transition must publish:

- previous state
- new state
- primary reason code
- supporting reason codes
- source confidence snapshot
- simulation timestamp

This record is emitted on `/mission/explanation` and must be stable under deterministic replay.

## Safety Rules

- State transitions are edge-triggered and monotonic with respect to simulation time.
- A single timestamp cannot produce more than one state transition.
- `MISSION_ABORT` and `MISSION_COMPLETE` are terminal states for the run.
- `LOCALIZATION_CONTINGENCY` is the only holding state allowed to delay abort.

## Tactical Coupling

`ew_risk_map_node` and `tactical_summary_node` may consume mission state, but they may not trigger state transitions. The mission state machine is the sole authority for mission continuity decisions.
