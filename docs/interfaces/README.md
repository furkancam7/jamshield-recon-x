# Interface Documentation

This section defines the ROS2 communication contracts used by JamShield Recon-X Sim.

## Contents

- `topic-contracts.md`: topic-level publishers, subscribers, and separation rules
- `message-schemas.md`: normative field definitions for all message families
- `reason-codes.md`: enumerated reason codes for trust, mission continuity, health, and evaluation
- `sensor-adapter-contracts.md`: Phase 14-A adapter ownership boundaries and simulator-to-hardware mapping contracts

## Interface Rules

- Topic families are fixed to `/sensors/*`, `/sync/*`, `/localization/*`, `/trust/*`, `/mission/*`, `/tactical/*`, `/events/*`, `/truth/*`, and `/evaluation/*`.
- Evaluation-only ground truth is isolated to `/truth/*`.
- Runtime autonomy must not depend on `/truth/*` or `/evaluation/*`.
- Message fields that affect mission continuity must be deterministic and explicitly typed.
