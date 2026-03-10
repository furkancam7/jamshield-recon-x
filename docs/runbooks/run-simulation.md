# Run Simulation

## Purpose

This runbook describes the canonical simulation execution workflow for a deterministic scenario run.

## Inputs

- built workspace
- sourced runtime environment
- selected scenario manifest
- writable log output directory

## Canonical Command Contract

The repository should expose an entry point equivalent to:

```bash
ros2 launch jamshield_recon_x_sim sim.launch.py \
  scenario_manifest:=docs/scenario-design/manifests/<scenario>.yaml \
  record:=true \
  output_dir:=<run_dir>
```

If this launch contract is not yet implemented, treat the missing wrapper as a Future system extension and run the equivalent simulator, adapter, autonomy, and logger processes manually.

## Execution Procedure

1. Select a single scenario manifest and record its hash.
2. Ensure the output directory is empty or versioned by `run_id`.
3. Start the simulation with recording enabled.
4. Confirm that the following topic families are active: `/sensors/*`, `/sync/*`, `/localization/*`, `/trust/*`, `/mission/*`, `/tactical/*`, `/events/*`, and `/truth/*`.
5. Observe the live mission state for expected startup sequence: `PREPARE` followed by a valid primary localization mode.
6. Allow the scenario to run to `MISSION_COMPLETE` or `MISSION_ABORT`.
7. Stop the run only after logger finalization completes.

## Required Runtime Checks

- `scenario_orchestrator_node` published manifest and event lifecycle messages
- `time_sync_node` remained monotonic
- `logger_node` recorded `/truth/pose`
- no runtime node subscribed to `/truth/*`
- mission state transitions were explained on `/mission/explanation`

## Expected Outputs

- recorded runtime log bundle
- recorded evaluation-only ground truth
- manifest hash or manifest copy
- run metadata with seed and clock rate

## Immediate Triage Rules

Stop the run and mark it suspect if:

- `/truth/pose` is absent
- `MISSION_ABORT` occurs in a scenario that does not allow abort
- topic freshness warnings appear before any injected event justifies them
- the simulation clock is non-monotonic
