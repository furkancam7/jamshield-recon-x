# Architecture Documentation

This section defines the runtime structure of JamShield Recon-X Sim.

## Contents

- `01-system-overview.md`: system purpose, boundaries, layers, and design principles
- `02-runtime-dataflow.md`: runtime data flow and replay flow
- `03-ros2-node-architecture.md`: ROS2 node responsibilities and communication map
- `04-mission-state-machine.md`: deterministic mission continuity state machine

## Architecture Rules

- Runtime autonomy, tactical intelligence, evaluation systems, and operator interface are distinct concerns.
- GNSS trust is computed before localization mode selection.
- Confidence-aware localization uses deterministic thresholds and hysteresis.
- Evaluation-only ground truth is isolated to `/truth/*` and `/evaluation/*`.
- Mission continuity decisions are explainable through explicit reason codes.
