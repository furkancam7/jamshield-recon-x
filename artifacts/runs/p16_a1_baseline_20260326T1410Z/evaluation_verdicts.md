# Evaluation Verdicts

- Run ID: `p16_a1_baseline_20260326T1410Z`

| Scenario | Profile | Verdict | Primary Reason | Mission Success | Invalid | Failed Checks |
| --- | --- | --- | --- | --- | --- | --- |
| s1_nominal | baseline_nominal_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s2_gnss_degraded_corridor | urban_canyon_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s3_gnss_denied_zone | denial_corridor_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s4_denied_vio_good | denial_corridor_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s5_denied_vio_weak | denial_corridor_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | MISSION_SUCCESS |
| s6_denied_vio_lost | denial_corridor_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s7_conflict_score_dominates | spoof_like_drift_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s8_conflict_state_dominates | spoof_like_drift_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s9_fusion_gnss_primary | baseline_nominal_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s10_fusion_degraded_fused | urban_canyon_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s11_fusion_denied_vio_only | denial_corridor_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s12_fusion_dead_reckoning | denial_corridor_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s13_sync_low_nominal | comms_instability_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s14_sync_low_denied_good | comms_instability_profile_v1 | PASS | evaluation_acceptance_passed | True | False | - |
| s15_safe_hold_timeout_abort | denial_corridor_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | MISSION_SUCCESS |
| s16_recovery_dwell_delays_resume | baseline_nominal_profile_v1 | FAIL | evaluation_threshold_exceeded | True | False | ATE_RMSE_M, RPE_RMSE_M |
| s17_state_oscillation_safe_hold | urban_canyon_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | MISSION_SUCCESS |
| s18_abort_terminal | baseline_nominal_profile_v1 | FAIL | evaluation_threshold_exceeded | False | False | ATE_RMSE_M, RPE_RMSE_M, LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s19_ew_mid_route_denial_hotspot | denial_corridor_profile_v1 | FAIL | evaluation_threshold_exceeded | True | False | RPE_RMSE_M |
| s20_ew_decay_after_recovery | denial_corridor_profile_v1 | FAIL | evaluation_threshold_exceeded | True | False | RPE_RMSE_M |
