# Runbooks

This section defines operational workflows for local simulation, replay, and investigation.

## Contents

- `local-setup.md`: expected local environment and dependency baseline
- `run-simulation.md`: simulation execution workflow
- `release-ops.md`: release template, checklist, and gate decision policy
- `known-limitations.md`: current-slice operational limits and deferred items
- `replay-analysis.md`: deterministic replay and metrics extraction workflow
- `troubleshooting.md`: failure investigation patterns

## Runbook Rules

- Runbooks describe simulation-only operation.
- Any hardware-specific procedure belongs to the Future hardware integration phase.
- Evaluation commands must remain separate from runtime autonomy commands.
- Release decisions must be evidence-driven (CI + regression + artifact validation).
