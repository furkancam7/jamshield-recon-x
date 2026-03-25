# Troubleshooting

## Scope

This runbook covers simulation, replay, and evaluation failures. It does not cover real hardware, which belongs to the Future hardware integration phase.

Current-slice note:

- Troubleshooting is artifact-first (`*_report.json`, `*_runtime_trace.json`, `*_mission_audit.json`, replay/evaluation bundles).
- ROS2 `logger_node` and `evaluation_node` run through the hybrid bridge in launch probe flows.
- `health_monitor_node` publication is available through node and launch probe execution (`*_mission_health.json`, `*_fault_events.json`).

## Symptom: No Fused Localization Output

Check:

1. `<scenario>_runtime_trace.json` for persistent `localization_mode=HOLD_LAST_SAFE`
2. `<scenario>_report.json` for low `localization_confidence`
3. `<scenario>_report.json` `trust_primary_reason_code` for `localization_confidence_low` or `sync_quality_low`
4. `<scenario>_mission_audit.json` for forced holds and transition history

Likely causes:

- camera or IMU stream missing
- GNSS and VIO both below confidence thresholds
- sync drift exceeded continuity limit

## Symptom: Unexpected `MISSION_ABORT`

Check:

1. `<scenario>_report.json` and `<scenario>_mission_audit.json` primary reason codes
2. `<scenario>_mission_audit.json` for transition ordering and timeout escalation
3. `<scenario>_runtime_trace.json` for per-tick `mission_state`
4. whether `mission_abort_safe_hold_timeout`, `mission_abort_vio_lost`, or `mission_abort_terminal_latched` was triggered

Likely causes:

- prolonged `MISSION_SAFE_HOLD`
- critical health fault
- scenario manifest inconsistent with route duration or sensor profile

## Symptom: Replay Marked `INVALID`

Check:

1. manifest hash equality
2. availability and completeness of `<scenario>_truth_trace.json`
3. first divergence in `replay_results.json`
4. profile and artifact presence in `evaluation_verdicts.json` and `evaluation_metrics.json`

Likely causes:

- log bundle incomplete
- replay configuration differs from original run
- nondeterministic behavior introduced in runtime nodes

## Symptom: GNSS Not Rejected During Spoof-Like Drift

Check:

1. `<scenario>_report.json` `gnss_state` and `gnss_trust`
2. `<scenario>_runtime_trace.json` for tick-level trust drop timing
3. `<scenario>_report.json` `trust_primary_reason_code` and `trust_reason_codes`
4. final localization mode (`BLENDED`, `VIO_PRIMARY`, or `HOLD_LAST_SAFE`) in report/runtime trace

Likely causes:

- drift magnitude too small for configured thresholds
- VIO quality too poor to support confident rejection
- trust hysteresis preventing transition due to configuration mismatch

## Symptom: Continuity Breaks During Denial Corridor

Check:

1. `evaluation_metrics.json` for `FALLBACK_REACTION_TIME_S`
2. `<scenario>_runtime_trace.json` for denied ticks and mission transition timing
3. manifest `mission_timeline` overrides and route geometry assumptions
4. mission/trust reason codes for `sync_quality_low`, `localization_confidence_low`, and denied-state transitions

Likely causes:

- VIO underperforming due to visual texture or sensor noise
- delay or loss on required sensor streams
- denial event overlapping with unsupported sensor degradation

## Escalation Rule

If troubleshooting identifies a structural mismatch between architecture intent and runtime behavior, record the issue with:

- scenario id
- run id
- first divergence timestamp
- relevant reason codes
- whether the issue is runtime, replay, or evaluation

## Rollback and Recovery Playbook

### Gate Failed (`FAIL`)

1. Stop release promotion for the candidate commit.
2. Create or update a blocker issue with:
   - failing gate name
   - run id / CI run URL
   - first failing check and related reason codes
3. Keep `target_commit` unchanged while reproducing once with the same inputs.
4. Promote only after blocker is resolved and evidence is refreshed.

### Evidence Invalid (`INVALID`)

1. Stop release promotion immediately.
2. Record integrity failure details:
   - missing artifact or hash mismatch
   - first divergence timestamp (if replay-related)
3. Open blocker issue and label it as evidence-integrity.
4. Re-run from clean output directory and re-attach complete evidence bundle before retry.

### Blocker Logging Standard

Every blocker entry must include:

- candidate `release_id`
- commit SHA
- failing command or workflow run URL
- artifact/run path
- explicit next action owner
