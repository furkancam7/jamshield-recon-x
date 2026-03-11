# JamShield Recon-X Sim Documentation

JamShield Recon-X Sim is a simulation-first autonomy stack for GNSS-degraded and electronic warfare-like environments. The documentation in this directory defines the system as a hardware-portable software architecture with deterministic mission continuity, dedicated GNSS trust management, confidence-aware localization, deterministic replay, and evaluation-only ground truth.

## Scope

This documentation covers:

- runtime autonomy behavior in simulation
- tactical intelligence outputs derived from runtime signals
- replay and evaluation workflows
- ROS2 topic and message contracts
- deterministic scenario design
- architectural decisions that constrain implementation

This documentation does not claim hardware validation. Any reference to hardware portability describes interface boundaries intended for a Future hardware integration phase.

## Non-negotiable Constraints

- The system is simulation-first.
- Ground truth is evaluation-only ground truth.
- Runtime autonomy must not subscribe to `/truth/*`.
- Mission continuity is deterministic and explainable.
- GNSS trust is produced by a dedicated subsystem.
- Deterministic replay and evaluation are first-class capabilities.

## Directory Map

- `architecture/`: runtime structure, data flow, ROS2 node decomposition, mission state machine
- `interfaces/`: topic contracts, message schemas, reason codes
- `scenario-design/`: scenario manifest, event injection model, baseline scenario definitions
- `evaluation/`: metrics, acceptance criteria, regression protocol
- `runbooks/`: local setup, simulation execution, replay analysis, troubleshooting
- `decisions/`: architecture decision records
- `roadmap/`: phase-based master plan and live progress tracker

## Reading Order

1. `architecture/01-system-overview.md`
2. `architecture/02-runtime-dataflow.md`
3. `interfaces/topic-contracts.md`
4. `scenario-design/scenario-manifest-spec.md`
5. `evaluation/metrics.md`
6. `roadmap/master-plan.md`
7. `roadmap/phase-03-closure.md`
8. `roadmap/phase-04-backlog.md`
9. `decisions/ADR-001-ground-truth-is-evaluation-only.md`

## Terminology

The following terms are normative across this repository:

- simulation-first
- hardware-portable
- GNSS trust
- confidence-aware localization
- mission continuity
- deterministic replay
- evaluation-only ground truth
- scenario manifest
