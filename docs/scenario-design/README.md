# Scenario Design Documentation

This section defines how deterministic scenarios are authored and replayed.

## Contents

- `scenario-manifest-spec.md`: normative scenario manifest schema
- `event-injection-model.md`: deterministic event model for navigation degradation
- `baseline-scenarios.md`: baseline scenarios for validation and regression

## Scenario Rules

- Every run is defined by a single scenario manifest.
- The scenario manifest must include a fixed seed.
- Event ordering must be deterministic.
- Ground truth may exist in simulation, but it remains evaluation-only ground truth.
- Scenario events may degrade runtime sensors but may not inject decisions directly into runtime autonomy nodes.
