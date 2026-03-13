# Reason Codes

## Usage Rules

- Reason codes are stable identifiers, not free text.
- `primary_reason_code` is the first causal explanation for a decision.
- `reason_codes` may include supporting context in deterministic order.
- Codes are shared across runtime logs, replay, tactical artifacts, and evaluation outputs.
- Canonical format is always `snake_case`.

## GNSS Trust Codes

| Code | Meaning |
| --- | --- |
| `trust_inputs_nominal` | Trust inputs remained inside nominal bounds. |
| `gnss_measurement_quality_low` | GNSS quality degraded below the configured low threshold. |
| `gnss_denial_suspected` | GNSS behavior matches a denial-like outage pattern. |
| `vio_trust_low` | VIO health degraded below the configured low threshold. |
| `sync_quality_low` | Timing alignment or freshness degraded below the configured threshold. |
| `localization_confidence_low` | Fused localization confidence fell below the configured low threshold. |

## Mission Continuity Codes

| Code | Meaning |
| --- | --- |
| `mission_execute_nominal` | Mission continues under nominal localization conditions. |
| `mission_degraded_gnss_reduced` | Mission continues in degraded mode because GNSS trust dropped. |
| `mission_fallback_vio_primary` | Mission continues under VIO-led fallback localization. |
| `mission_safe_hold_vio_weak` | Mission holds because denied GNSS coincided with weak VIO. |
| `mission_safe_hold_localization_unstable` | Mission holds because localization continuity is insufficient. |
| `mission_recovery_dwell_active` | Recovery is delayed until the configured dwell requirement is satisfied. |
| `mission_state_oscillation_detected` | State flapping exceeded the configured oscillation window limit. |
| `mission_abort_safe_hold_timeout` | Mission aborted after persistent safe hold exceeded timeout. |
| `mission_abort_vio_lost` | Mission aborted because fallback localization was lost. |
| `mission_abort_terminal_latched` | Mission remained aborted because abort is terminal within the run. |

## EW Risk Map Codes

| Code | Meaning |
| --- | --- |
| `ew_risk_nominal` | No material EW-style risk evidence accumulated in the current run. |
| `ew_gnss_denial_hotspot` | Risk map is primarily shaped by denial-like GNSS loss evidence. |
| `ew_sync_instability_corridor` | Risk map is primarily shaped by low sync-quality evidence along the route. |
| `ew_localization_instability` | Risk map is primarily shaped by localization instability evidence. |
| `ew_gnss_degraded_corridor` | Risk map is primarily shaped by degraded-but-not-denied GNSS evidence. |

## EW Evidence Codes

| Code | Meaning |
| --- | --- |
| `gnss_denial_suspected` | Denial-like GNSS evidence was observed while stamping the grid. |
| `gnss_measurement_quality_low` | Degraded GNSS quality evidence was observed while stamping the grid. |
| `sync_quality_low` | Low sync-quality evidence was observed while stamping the grid. |
| `localization_confidence_low` | Localization confidence evidence was observed while stamping the grid. |
| `vio_primary_active` | Risk evidence occurred while localization was running in `VIO_PRIMARY`. |
| `hold_last_safe_active` | Risk evidence occurred while localization was running in `HOLD_LAST_SAFE`. |

## Tactical Summary Reason Codes

| Code | Meaning |
| --- | --- |
| `tactical_nominal_overview` | Tactical summary reports a nominal mission and localization picture. |
| `tactical_mission_degraded` | Tactical summary is primarily driven by mission degradation. |
| `tactical_fallback_active` | Tactical summary is primarily driven by fallback navigation. |
| `tactical_safe_hold_active` | Tactical summary is primarily driven by safe-hold behavior. |
| `tactical_abort_active` | Tactical summary is primarily driven by an abort condition. |
| `tactical_ew_hotspot_detected` | Tactical summary is primarily driven by elevated EW route risk. |
| `tactical_sync_risk_observed` | Tactical summary is primarily driven by sync-quality risk. |
| `tactical_localization_instability_observed` | Tactical summary is primarily driven by localization instability. |

## Tactical Advisory Codes

| Code | Meaning |
| --- | --- |
| `operator_continue_nominal` | Operator may continue on the current route under nominal conditions. |
| `operator_continue_with_caution` | Operator may continue but should monitor confidence and timing risk. |
| `operator_avoid_high_risk_corridor` | Operator should avoid the highlighted route corridor due to elevated tactical risk. |
| `operator_prepare_manual_review` | Operator should prepare for manual review of navigation quality and route safety. |
| `operator_hold_position_and_investigate` | Operator should hold position and investigate before resuming. |
| `operator_abort_and_retask` | Operator should abort the current route and retask. |

## Evaluation Codes

| Code | Meaning |
| --- | --- |
| `evaluation_pending` | Scenario report was generated before replay/evaluation verdict materialization. |
| `evaluation_acceptance_passed` | Replay and acceptance thresholds passed for the scenario. |
| `evaluation_threshold_exceeded` | Replay was valid but one or more acceptance thresholds failed. |
| `evaluation_profile_missing` | Scenario referenced an unknown evaluation profile. |
| `deterministic_replay_failed` | Replay diverged from the original runtime artifacts and invalidated the run. |

## Legacy Rule

- Uppercase reason-code forms in older artifacts are legacy and must not be reused in current interfaces.
