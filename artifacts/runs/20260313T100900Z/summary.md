# Regression Summary

- Run ID: `20260313T100900Z`
- Overall result: `PASS`

## Scenario Results

- Config ID: `sim-v1`
- Software revision: `2e31a5ba1f7682acf36fe0201cdbf92769173b61`

| Scenario | GNSS State | GNSS | VIO | Sync | Mission | EW Level | EW Max | EW Cells | EW Cost | Trust Reason | Mission Reason | EW Reason | Transitions | Effective VIO | Mission State | Loc Mode | Loc Conf | VIO Profile | ATE RMSE |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- | --- | --- | ---: | --- | --- | --- | ---: | --- | ---: |
| s1_nominal | nominal | 0.960 | 0.799 | 1.000 | 0.913 | none | 0.000 | 0 | 0.000 | trust_inputs_nominal | mission_execute_nominal | ew_risk_nominal | 0 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.903 | nominal_v1 | 0.500 |
| s2_gnss_degraded_corridor | degraded | 0.590 | 0.796 | 1.000 | 0.666 | medium | 0.350 | 1 | 0.042 | trust_inputs_nominal | mission_degraded_gnss_reduced | ew_gnss_degraded_corridor | 1 | good | MISSION_DEGRADED | BLENDED | 0.688 | nominal_v1 | 3.000 |
| s3_gnss_denied_zone | denied | 0.050 | 0.825 | 1.000 | 0.450 | high | 0.950 | 1 | 0.113 | gnss_denial_suspected | mission_fallback_vio_primary | ew_gnss_denial_hotspot | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.760 | nominal_v1 | 8.000 |
| s4_denied_vio_good | denied | 0.050 | 0.806 | 1.000 | 0.441 | high | 0.950 | 1 | 0.113 | gnss_denial_suspected | mission_fallback_vio_primary | ew_gnss_denial_hotspot | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.742 | nominal_v1 | 8.000 |
| s5_denied_vio_weak | denied | 0.050 | 0.611 | 1.000 | 0.345 | high | 0.950 | 1 | 0.113 | gnss_denial_suspected | mission_safe_hold_vio_weak | ew_gnss_denial_hotspot | 1 | weak | MISSION_SAFE_HOLD | VIO_PRIMARY | 0.550 | weak_texture_v1 | 8.000 |
| s6_denied_vio_lost | denied | 0.050 | 0.092 | 1.000 | 0.098 | high | 0.950 | 1 | 0.113 | localization_confidence_low | mission_abort_vio_lost | ew_gnss_denial_hotspot | 1 | lost | MISSION_ABORT | HOLD_LAST_SAFE | 0.073 | lost_tracking_v1 | 8.000 |
| s7_conflict_score_dominates | denied | 0.050 | 0.073 | 1.000 | 0.090 | high | 0.950 | 1 | 0.113 | localization_confidence_low | mission_abort_vio_lost | ew_gnss_denial_hotspot | 1 | lost | MISSION_ABORT | HOLD_LAST_SAFE | 0.061 | lost_tracking_v1 | 8.000 |
| s8_conflict_state_dominates | denied | 0.050 | 0.825 | 1.000 | 0.450 | high | 0.950 | 1 | 0.113 | gnss_denial_suspected | mission_safe_hold_localization_unstable | ew_gnss_denial_hotspot | 1 | lost | MISSION_SAFE_HOLD | HOLD_LAST_SAFE | 0.760 | nominal_v1 | 8.000 |
| s9_fusion_gnss_primary | nominal | 0.960 | 0.825 | 1.000 | 0.920 | none | 0.000 | 0 | 0.000 | trust_inputs_nominal | mission_execute_nominal | ew_risk_nominal | 0 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.911 | nominal_v1 | 0.500 |
| s10_fusion_degraded_fused | degraded | 0.590 | 0.823 | 1.000 | 0.676 | medium | 0.350 | 1 | 0.048 | trust_inputs_nominal | mission_degraded_gnss_reduced | ew_gnss_degraded_corridor | 1 | good | MISSION_DEGRADED | BLENDED | 0.702 | nominal_v1 | 3.000 |
| s11_fusion_denied_vio_only | denied | 0.050 | 0.825 | 1.000 | 0.450 | high | 0.950 | 1 | 0.129 | gnss_denial_suspected | mission_fallback_vio_primary | ew_gnss_denial_hotspot | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.760 | nominal_v1 | 8.000 |
| s12_fusion_dead_reckoning | denied | 0.050 | 0.092 | 1.000 | 0.098 | high | 0.950 | 1 | 0.129 | localization_confidence_low | mission_abort_vio_lost | ew_gnss_denial_hotspot | 1 | lost | MISSION_ABORT | HOLD_LAST_SAFE | 0.073 | lost_tracking_v1 | 8.000 |
| s13_sync_low_nominal | nominal | 0.960 | 0.833 | 0.200 | 0.882 | low | 0.200 | 0 | 0.027 | sync_quality_low | mission_execute_nominal | ew_sync_instability_corridor | 0 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.913 | nominal_v1 | 0.500 |
| s14_sync_low_denied_good | denied | 0.050 | 0.823 | 0.200 | 0.409 | high | 1.000 | 1 | 0.119 | sync_quality_low | mission_fallback_vio_primary | ew_gnss_denial_hotspot | 1 | good | MISSION_FALLBACK | VIO_PRIMARY | 0.758 | nominal_v1 | 8.000 |
| s15_safe_hold_timeout_abort | denied | 0.050 | 0.759 | 1.000 | 0.433 | high | 0.950 | 4 | 0.314 | gnss_denial_suspected | mission_abort_safe_hold_timeout | ew_gnss_denial_hotspot | 2 | weak | MISSION_ABORT | VIO_PRIMARY | 0.695 | weak_texture_v1 | 8.000 |
| s16_recovery_dwell_delays_resume | nominal | 0.960 | 0.825 | 1.000 | 0.920 | high | 0.686 | 1 | 0.139 | trust_inputs_nominal | mission_execute_nominal | ew_localization_instability | 2 | good | MISSION_EXECUTE | VIO_PRIMARY | 0.911 | nominal_v1 | 0.500 |
| s17_state_oscillation_safe_hold | degraded | 0.590 | 0.833 | 1.000 | 0.695 | medium | 0.251 | 1 | 0.095 | trust_inputs_nominal | mission_state_oscillation_detected | ew_gnss_degraded_corridor | 3 | good | MISSION_SAFE_HOLD | BLENDED | 0.708 | nominal_v1 | 3.000 |
| s18_abort_terminal | nominal | 0.960 | 0.823 | 1.000 | 0.920 | high | 0.686 | 1 | 0.136 | trust_inputs_nominal | mission_abort_terminal_latched | ew_localization_instability | 1 | good | MISSION_ABORT | HOLD_LAST_SAFE | 0.910 | nominal_v1 | 0.500 |
| s19_ew_mid_route_denial_hotspot | nominal | 0.960 | 0.822 | 1.000 | 0.904 | high | 0.552 | 4 | 0.191 | trust_inputs_nominal | mission_execute_nominal | ew_gnss_denial_hotspot | 2 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.910 | nominal_v1 | 0.500 |
| s20_ew_decay_after_recovery | nominal | 0.960 | 0.833 | 1.000 | 0.922 | medium | 0.422 | 1 | 0.083 | trust_inputs_nominal | mission_execute_nominal | ew_localization_instability | 2 | good | MISSION_EXECUTE | GNSS_PRIMARY | 0.913 | nominal_v1 | 0.500 |

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
- `calibration_bundle_present`: PASS - trust_calibration.json/.md/.csv must all be present.
- `ew_metrics_bundle_present`: PASS - ew_metrics.json/.md/.csv must all be present.
