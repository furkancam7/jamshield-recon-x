# Phase 14 - Hardware-Portability Layer Backlog

## Goal

Start Phase 14 with a documentation-first portability contract baseline that prepares simulator-first runtime boundaries for future hardware integration.

## Scope (P14-A)

- Define sensor adapter interface boundaries for camera, IMU, and GNSS ingress.
- Define timing/rate assumptions and validation notes required for portable execution contracts.
- Define onboard-vs-ground split notes for future deployment topology decisions.
- Produce portability-facing runbook/mapping documentation without changing runtime behavior.

## Non-Goals (P14-A)

- No runtime mission/trust/tactical logic changes.
- No ROS2 message/schema/API bump.
- No real hardware driver implementation.
- No modification of `/truth/*` evaluation-only boundaries or mission authority ownership.

## Child Issue Set

- `#71` P14-A1 Adapter interface contracts
- `#72` P14-A2 Timing/rate assumptions and validation notes
- `#73` P14-A3 Portability runbook + mapping matrix

## Landed Evidence

- `#71` landed via `docs/interfaces/sensor-adapter-contracts.md` with cross-links in interface and architecture docs.

## Acceptance Gates

- Sensor adapter boundaries are decision-complete and traceable to current interfaces.
- Timing/rate assumptions include measurable validation checks.
- Portability runbook baseline and mapping matrix are linked and consistent with current-slice constraints.
- Deferred items are explicit and separated from current-slice deliverables.

## Residual Boundaries

- Cross-phase trust calibration tuning remains a residual from prior phases and is not a P14-A blocker.
- Runtime authority model is unchanged:
  - file-based replay/evaluation fallback remains valid
  - mission decision authority remains `mission_continuity_node`
  - `/truth/*` remains evaluation-only
