# Mission State Machine

## Purpose

`mission_continuity_node` implements deterministic mission continuity. In the current executable slice it consumes mission confidence, GNSS state, effective VIO state, and scenario progression derived from the manifest-driven timeline.

## States

| State | Meaning | Current Slice Action |
| --- | --- | --- |
| `MISSION_EXECUTE` | Mission is proceeding with acceptable confidence | `CONTINUE_ROUTE` |
| `MISSION_DEGRADED` | Mission remains active but under reduced confidence | `REDUCE_SPEED` |
| `MISSION_FALLBACK` | Mission is continuing on fallback localization authority | `CONTINUE_ROUTE` |
| `MISSION_SAFE_HOLD` | Forward progress is halted until continuity recovers or timeout escalates | `HOLD_POSITION` |
| `MISSION_ABORT` | Mission continuity entered a terminal unsafe state | `TERMINATE_MISSION` |

Current slice note:

- `MISSION_PREPARE`, `MISSION_COMPLETE`, and `LOCALIZATION_CONTINGENCY` remain architecture goals but are not emitted by the current executable implementation.

## Transition Inputs

The current executable state machine uses only:

- `mission_confidence`
- `gnss_state`
- `effective_vio_state`
- scenario route progress from the manifest-driven timeline

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

The current executable implementation does not expose the full architecture transition table. Instead it evaluates a candidate state from trust and VIO inputs, then applies:

- recovery dwell before returning to a safer state
- safe-hold escalation timeout to `MISSION_ABORT`
- terminal abort latching
- oscillation detection that forces `MISSION_SAFE_HOLD`

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
- `MISSION_ABORT` is terminal for the run.
- `MISSION_SAFE_HOLD` is the executable holding state that may delay abort in the current slice.

## Tactical Coupling

`ew_risk_map_node` and `tactical_summary_node` may consume mission state, but they may not trigger state transitions. The mission state machine is the sole authority for mission continuity decisions.
