# Evaluation Documentation

This section defines how JamShield Recon-X Sim runs are measured and judged.

## Contents

- `metrics.md`: metric definitions and formulas
- `acceptance-criteria.md`: scenario-specific thresholds and invalid run rules
- `regression-protocol.md`: deterministic regression and replay procedure

## Evaluation Rules

- Evaluation uses evaluation-only ground truth.
- Runtime autonomy outputs are frozen before evaluation begins.
- Deterministic replay is required for benchmarked scenarios.
- A run can pass metrics and still be invalid if replay or logging requirements fail.
