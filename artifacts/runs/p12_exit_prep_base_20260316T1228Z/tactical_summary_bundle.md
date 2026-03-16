# Tactical Summary Bundle

- Run ID: `p12_exit_prep_base_20260316T1228Z`

| Scenario | Mission State | Tactical Reason | Advisory | Failed Checks |
| --- | --- | --- | --- | --- |
| s10_fusion_degraded_fused | MISSION_DEGRADED | tactical_mission_degraded | operator_continue_with_caution | - |
| s11_fusion_denied_vio_only | MISSION_FALLBACK | tactical_fallback_active | operator_avoid_high_risk_corridor | - |
| s12_fusion_dead_reckoning | MISSION_ABORT | tactical_abort_active | operator_abort_and_retask | - |
| s13_sync_low_nominal | MISSION_EXECUTE | tactical_sync_risk_observed | operator_continue_with_caution | - |
| s14_sync_low_denied_good | MISSION_FALLBACK | tactical_fallback_active | operator_avoid_high_risk_corridor | - |
| s15_safe_hold_timeout_abort | MISSION_ABORT | tactical_abort_active | operator_abort_and_retask | - |
| s16_recovery_dwell_delays_resume | MISSION_EXECUTE | tactical_ew_hotspot_detected | operator_avoid_high_risk_corridor | - |
| s17_state_oscillation_safe_hold | MISSION_SAFE_HOLD | tactical_safe_hold_active | operator_hold_position_and_investigate | - |
| s18_abort_terminal | MISSION_ABORT | tactical_abort_active | operator_abort_and_retask | - |
| s19_ew_mid_route_denial_hotspot | MISSION_EXECUTE | tactical_ew_hotspot_detected | operator_avoid_high_risk_corridor | - |
| s1_nominal | MISSION_EXECUTE | tactical_nominal_overview | operator_continue_nominal | - |
| s20_ew_decay_after_recovery | MISSION_EXECUTE | tactical_localization_instability_observed | operator_continue_with_caution | - |
| s2_gnss_degraded_corridor | MISSION_DEGRADED | tactical_mission_degraded | operator_continue_with_caution | - |
| s3_gnss_denied_zone | MISSION_FALLBACK | tactical_fallback_active | operator_avoid_high_risk_corridor | - |
| s4_denied_vio_good | MISSION_FALLBACK | tactical_fallback_active | operator_avoid_high_risk_corridor | - |
| s5_denied_vio_weak | MISSION_SAFE_HOLD | tactical_safe_hold_active | operator_hold_position_and_investigate | - |
| s6_denied_vio_lost | MISSION_ABORT | tactical_abort_active | operator_abort_and_retask | - |
| s7_conflict_score_dominates | MISSION_ABORT | tactical_abort_active | operator_abort_and_retask | - |
| s8_conflict_state_dominates | MISSION_SAFE_HOLD | tactical_safe_hold_active | operator_hold_position_and_investigate | - |
| s9_fusion_gnss_primary | MISSION_EXECUTE | tactical_nominal_overview | operator_continue_nominal | - |
