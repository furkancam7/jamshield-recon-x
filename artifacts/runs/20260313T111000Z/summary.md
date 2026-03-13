# Regression Summary

- Run ID: `20260313T111000Z`
- Overall result: `PASS`

## Scenario Results

- Config ID: `sim-v1`
- Evaluation Profiles: `baseline_nominal_profile_v1, comms_instability_profile_v1, denial_corridor_profile_v1, spoof_like_drift_profile_v1, urban_canyon_profile_v1`
- Software revision: `2e31a5ba1f7682acf36fe0201cdbf92769173b61`

| Scenario | GNSS State | GNSS | VIO | Sync | Mission | EW Level | Tactical | Advisory | Eval Verdict | Replay | Eval Reason | Transitions | Effective VIO | Mission State | Loc Mode | Loc Conf | VIO Profile | ATE RMSE |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | ---: | --- | ---: |
| s1_nominal | nominal | 0.960 | 0.799 | 1.000 | 0.913 | none | tactical_nominal_overview | operator_continue_nominal | PASS | True | evaluation_acceptance_passed | 0 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.903 | nominal_v1 | 0.500 |
| s2_gnss_degraded_corridor | degraded | 0.590 | 0.796 | 1.000 | 0.666 | medium | tactical_mission_degraded | operator_continue_with_caution | PASS | True | evaluation_acceptance_passed | 1 | good | MISSION_DEGRADED | BLENDED | 0.688 | nominal_v1 | 3.000 |
| s3_gnss_denied_zone | denied | 0.050 | 0.825 | 1.000 | 0.450 | high | tactical_fallback_active | operator_avoid_high_risk_corridor | PASS | True | evaluation_acceptance_passed | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.760 | nominal_v1 | 8.000 |
| s4_denied_vio_good | denied | 0.050 | 0.806 | 1.000 | 0.441 | high | tactical_fallback_active | operator_avoid_high_risk_corridor | PASS | True | evaluation_acceptance_passed | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.742 | nominal_v1 | 8.000 |
| s5_denied_vio_weak | denied | 0.050 | 0.611 | 1.000 | 0.345 | high | tactical_safe_hold_active | operator_hold_position_and_investigate | FAIL | True | evaluation_threshold_exceeded | 1 | weak | MISSION_SAFE_HOLD | VIO_PRIMARY | 0.550 | weak_texture_v1 | 8.000 |
| s6_denied_vio_lost | denied | 0.050 | 0.092 | 1.000 | 0.098 | high | tactical_abort_active | operator_abort_and_retask | FAIL | True | evaluation_threshold_exceeded | 1 | lost | MISSION_ABORT | HOLD_LAST_SAFE | 0.073 | lost_tracking_v1 | 8.000 |
| s7_conflict_score_dominates | denied | 0.050 | 0.073 | 1.000 | 0.090 | high | tactical_abort_active | operator_abort_and_retask | FAIL | True | evaluation_threshold_exceeded | 1 | lost | MISSION_ABORT | HOLD_LAST_SAFE | 0.061 | lost_tracking_v1 | 8.000 |
| s8_conflict_state_dominates | denied | 0.050 | 0.825 | 1.000 | 0.450 | high | tactical_safe_hold_active | operator_hold_position_and_investigate | FAIL | True | evaluation_threshold_exceeded | 1 | lost | MISSION_SAFE_HOLD | HOLD_LAST_SAFE | 0.760 | nominal_v1 | 8.000 |
| s9_fusion_gnss_primary | nominal | 0.960 | 0.825 | 1.000 | 0.920 | none | tactical_nominal_overview | operator_continue_nominal | PASS | True | evaluation_acceptance_passed | 0 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.911 | nominal_v1 | 0.500 |
| s10_fusion_degraded_fused | degraded | 0.590 | 0.823 | 1.000 | 0.676 | medium | tactical_mission_degraded | operator_continue_with_caution | PASS | True | evaluation_acceptance_passed | 1 | good | MISSION_DEGRADED | BLENDED | 0.702 | nominal_v1 | 3.000 |
| s11_fusion_denied_vio_only | denied | 0.050 | 0.825 | 1.000 | 0.450 | high | tactical_fallback_active | operator_avoid_high_risk_corridor | PASS | True | evaluation_acceptance_passed | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.760 | nominal_v1 | 8.000 |
| s12_fusion_dead_reckoning | denied | 0.050 | 0.092 | 1.000 | 0.098 | high | tactical_abort_active | operator_abort_and_retask | FAIL | True | evaluation_threshold_exceeded | 1 | lost | MISSION_ABORT | HOLD_LAST_SAFE | 0.073 | lost_tracking_v1 | 8.000 |
| s13_sync_low_nominal | nominal | 0.960 | 0.833 | 0.200 | 0.882 | low | tactical_sync_risk_observed | operator_continue_with_caution | PASS | True | evaluation_acceptance_passed | 0 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.913 | nominal_v1 | 0.500 |
| s14_sync_low_denied_good | denied | 0.050 | 0.823 | 0.200 | 0.409 | high | tactical_fallback_active | operator_avoid_high_risk_corridor | PASS | True | evaluation_acceptance_passed | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.758 | nominal_v1 | 8.000 |
| s15_safe_hold_timeout_abort | denied | 0.050 | 0.759 | 1.000 | 0.433 | high | tactical_abort_active | operator_abort_and_retask | FAIL | True | evaluation_threshold_exceeded | 2 | weak | MISSION_ABORT | VIO_PRIMARY | 0.695 | weak_texture_v1 | 8.000 |
| s16_recovery_dwell_delays_resume | nominal | 0.960 | 0.825 | 1.000 | 0.920 | high | tactical_ew_hotspot_detected | operator_avoid_high_risk_corridor | FAIL | True | evaluation_threshold_exceeded | 2 | good | MISSION_EXECUTE | VIO_PRIMARY | 0.911 | nominal_v1 | 0.500 |
| s17_state_oscillation_safe_hold | degraded | 0.590 | 0.833 | 1.000 | 0.695 | medium | tactical_safe_hold_active | operator_hold_position_and_investigate | FAIL | True | evaluation_threshold_exceeded | 3 | good | MISSION_SAFE_HOLD | BLENDED | 0.708 | nominal_v1 | 3.000 |
| s18_abort_terminal | nominal | 0.960 | 0.823 | 1.000 | 0.920 | high | tactical_abort_active | operator_abort_and_retask | FAIL | True | evaluation_threshold_exceeded | 1 | good | MISSION_ABORT | HOLD_LAST_SAFE | 0.910 | nominal_v1 | 0.500 |
| s19_ew_mid_route_denial_hotspot | nominal | 0.960 | 0.822 | 1.000 | 0.904 | high | tactical_ew_hotspot_detected | operator_avoid_high_risk_corridor | FAIL | True | evaluation_threshold_exceeded | 2 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.910 | nominal_v1 | 0.500 |
| s20_ew_decay_after_recovery | nominal | 0.960 | 0.833 | 1.000 | 0.922 | medium | tactical_localization_instability_observed | operator_continue_with_caution | FAIL | True | evaluation_threshold_exceeded | 2 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.913 | nominal_v1 | 0.500 |

## Checks

- `gnss_trust_ordering`: PASS - Expected nominal gnss_trust > degraded gnss_trust > denied gnss_trust.
- `denied_not_execute`: PASS - Denied scenario must not end in MISSION_EXECUTE.
- `degraded_not_denied`: PASS - Degraded scenario must not be classified as denied.
- `nominal_not_abort`: PASS - Nominal scenario must not collapse to MISSION_ABORT.
- `nominal_minimum_gnss_trust_threshold`: PASS - Nominal scenario gnss_trust must remain at or above 0.90.
- `denied_allowed_mission_states`: PASS - Denied scenario must end in the allowed denied-state set.
- `p4_vio_good_fallback`: PASS - Denied + nominal VIO pipeline must stay in fallback-capable state.
- `p4_vio_weak_safe_hold`: PASS - Denied + weak-texture VIO pipeline must produce weak VIO and safe hold.
- `p4_vio_lost_emergency`: PASS - Denied + lost-tracking VIO pipeline must force abort path.
- `p4_conflict_score_dominates`: PASS - Conflict case with reported good state and lost pipeline score must resolve to lost.
- `p4_conflict_state_dominates`: PASS - Conflict case with lost reported state must preserve lost effective state.
- `vio_metrics_source_pipeline_v1`: PASS - All regression artifacts must record pipeline_v1 VIO metrics.
- `p6_fusion_gnss_primary`: PASS - Nominal GNSS + good VIO must produce GNSS_PRIMARY localization mode.
- `p6_fusion_degraded_blended`: PASS - Degraded GNSS + good VIO must produce BLENDED localization mode.
- `p6_fusion_denied_vio_primary`: PASS - Denied GNSS + good VIO must produce VIO_PRIMARY localization mode.
- `p6_fusion_hold_last_safe`: PASS - Denied GNSS + lost VIO must produce HOLD_LAST_SAFE localization mode.
- `p6_fusion_confidence_ordering`: PASS - Localization confidence must decrease: GNSS_PRIMARY > BLENDED > HOLD_LAST_SAFE.
- `p6_fusion_fields_present`: PASS - All reports must include fusion fields: localization_mode, localization_confidence, gnss_weight, vio_weight.
- `vio_trust_ordering`: PASS - VIO trust must decrease across good > weak > lost scenarios.
- `mission_confidence_ordering`: PASS - Mission confidence must monotonically degrade across nominal > degraded > denied-good > denied-lost.
- `sync_quality_response`: PASS - Low-sync scenarios must surface reduced sync_quality and sync_quality_low reasoning.
- `reason_code_coverage`: PASS - Trust and mission reason codes must be present and snake_case across all reports.
- `no_legacy_enum_values`: PASS - Reports must not contain legacy mission-state or localization-mode values.
- `mission_recovery_dwell_respected`: PASS - Recovery from a degraded state must honor recovery_dwell_ticks before resuming safer mission states.
- `mission_safe_hold_timeout_abort`: PASS - Persistent safe hold must escalate to mission abort after the configured timeout.
- `mission_oscillation_detection`: PASS - State flapping beyond the sliding-window threshold must force MISSION_SAFE_HOLD.
- `mission_abort_terminal`: PASS - Once mission abort is entered, later ticks must remain terminal within the same scenario run.
- `mission_audit_present`: PASS - Every scenario must emit a mission audit artifact aligned with the final report state.
- `ew_map_artifact_present`: PASS - Every scenario must emit an EW risk-map artifact aligned with the final report values.
- `ew_nominal_false_marking_ceiling`: PASS - Nominal scenario must remain below the configured EW false-marking floor.
- `ew_corridor_cost_ordering`: PASS - EW corridor cost must increase from nominal to degraded to denied scenarios.
- `ew_denial_hotspot_localized`: PASS - Mid-route denial scenario must produce a high-risk but localized EW hotspot.
- `ew_temporal_decay_observed`: PASS - Recovery scenario must show EW risk decay after the denial interval ends.
- `ew_reason_code_coverage`: PASS - EW report, reason, and evidence codes must be present and snake_case across all scenarios.
- `tactical_summary_artifact_present`: PASS - Every scenario must emit a tactical summary artifact aligned with the final report values.
- `tactical_summary_runtime_consistency`: PASS - Tactical summary artifacts must stay consistent with report mission and EW fields.
- `tactical_advisory_coverage`: PASS - Key baseline scenarios must map to the expected operator advisory codes and texts.
- `tactical_text_determinism`: PASS - Tactical summary text must remain deterministic and constrained to the fixed two-sentence template.
- `no_legacy_tactical_reason_codes`: PASS - Tactical reason and advisory codes must be present and snake_case across all scenarios.
- `calibration_bundle_present`: PASS - trust_calibration.json/.md/.csv must all be present.
- `ew_metrics_bundle_present`: PASS - ew_metrics.json/.md/.csv must all be present.
- `tactical_bundle_present`: PASS - tactical_summary_bundle.json/.md/.csv must all be present.
- `runtime_trace_present`: PASS - Every scenario must emit a runtime trace artifact.
- `truth_trace_present`: PASS - Every scenario must emit a pseudo-truth trace artifact.
- `replay_results_present`: PASS - replay_results.json/.md/.csv must all be present.
- `evaluation_metrics_bundle_present`: PASS - evaluation_metrics.json/.md/.csv must all be present.
- `evaluation_verdicts_present`: PASS - evaluation_verdicts.json/.md/.csv must all be present.
- `deterministic_replay_passed`: PASS - All baseline scenarios must match deterministic replay.
- `manifest_hash_recorded`: PASS - All reports must record manifest_hash.
- `config_hash_recorded`: PASS - All reports must record config_hash.
