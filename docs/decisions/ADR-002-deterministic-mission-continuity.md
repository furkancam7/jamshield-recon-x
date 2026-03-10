# ADR-002: Deterministic Mission Continuity

## Status

Accepted

## Context

The system must continue operating through GNSS degradation, denial, and spoof-like behavior while remaining explainable and testable. A mission continuity policy based on opaque learned behavior would be difficult to audit, difficult to replay deterministically, and difficult to certify against scenario-specific acceptance thresholds.

## Decision

Mission continuity is implemented as a deterministic state machine in `mission_continuity_node`.

- State transitions use fixed thresholds, dwell timers, and explicit reason codes.
- Mission actions are constrained to a bounded command set.
- The operator interface is read-only during deterministic runs.
- Deterministic replay must reproduce the same state and action sequence for the same recorded inputs.

## Consequences

- Mission decisions are explainable from logs and reason codes.
- Regression testing can detect behavioral drift precisely.
- The system may be less adaptive than a learned policy in edge cases, but its behavior remains auditable.
- Any adaptive mission policy introduced later would be a Future system extension and would require a new ADR describing how determinism and explainability are preserved.
