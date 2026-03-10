# ADR-001: Ground Truth Is Evaluation Only

## Status

Accepted

## Context

Simulation provides exact vehicle pose, velocity, and environment state that are unavailable in real deployment. Using that information inside runtime autonomy would produce an unrealistic system architecture and invalidate mission continuity behavior under GNSS degradation. The project is simulation-first, but it must remain hardware-portable and must not encode assumptions that depend on simulator omniscience.

## Decision

Ground truth is classified as evaluation-only ground truth.

- `ground_truth_adapter_node` may publish `/truth/pose`.
- Only `logger_node` and `evaluation_node` may consume `/truth/*`.
- Runtime autonomy and tactical nodes must not subscribe to `/truth/*`.
- All metrics that require truth are computed offline by `evaluation_node`.

## Consequences

- Runtime behavior remains representative of deployable autonomy logic.
- Deterministic replay can compare runtime outputs against truth without contaminating the runtime path.
- Debugging requires clear separation between runtime evidence and evaluation evidence.
- Any future attempt to use truth in runtime autonomy requires a superseding ADR and would contradict the current architecture.
