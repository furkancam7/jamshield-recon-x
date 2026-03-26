# Evaluation Metrics

- Run ID: `p16_a1_baseline_20260326T1410Z`

| Scenario | Profile | ATE | RPE | Drift % | Continuity % | Fallback s | Success | Failed Metrics |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| s1_nominal | baseline_nominal_profile_v1 | 0.500 | 0.000 | 0.406 | 100.000 | 0.000 | True | - |
| s2_gnss_degraded_corridor | urban_canyon_profile_v1 | 3.000 | 0.000 | 2.039 | 100.000 | 0.000 | True | - |
| s3_gnss_denied_zone | denial_corridor_profile_v1 | 8.000 | 0.000 | 5.485 | 100.000 | 0.000 | True | - |
| s4_denied_vio_good | denial_corridor_profile_v1 | 8.000 | 0.000 | 5.485 | 100.000 | 0.000 | True | - |
| s5_denied_vio_weak | denial_corridor_profile_v1 | 8.000 | 0.000 | 5.485 | 100.000 | 0.000 | False | MISSION_SUCCESS |
| s6_denied_vio_lost | denial_corridor_profile_v1 | 8.000 | 0.000 | 5.485 | 0.000 | 0.000 | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s7_conflict_score_dominates | spoof_like_drift_profile_v1 | 8.000 | 0.000 | 5.485 | 0.000 | 0.000 | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s8_conflict_state_dominates | spoof_like_drift_profile_v1 | 8.000 | 0.000 | 5.485 | 0.000 | 0.000 | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s9_fusion_gnss_primary | baseline_nominal_profile_v1 | 0.500 | 0.000 | 0.406 | 100.000 | 0.000 | True | - |
| s10_fusion_degraded_fused | urban_canyon_profile_v1 | 3.000 | 0.000 | 2.434 | 100.000 | 0.000 | True | - |
| s11_fusion_denied_vio_only | denial_corridor_profile_v1 | 8.000 | 0.000 | 6.491 | 100.000 | 0.000 | True | - |
| s12_fusion_dead_reckoning | denial_corridor_profile_v1 | 8.000 | 0.000 | 6.491 | 0.000 | 0.000 | False | LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s13_sync_low_nominal | comms_instability_profile_v1 | 0.500 | 0.000 | 0.406 | 100.000 | 0.000 | True | - |
| s14_sync_low_denied_good | comms_instability_profile_v1 | 8.000 | 0.000 | 5.485 | 100.000 | 0.000 | True | - |
| s15_safe_hold_timeout_abort | denial_corridor_profile_v1 | 8.000 | 0.000 | 5.485 | 100.000 | 0.000 | False | MISSION_SUCCESS |
| s16_recovery_dwell_delays_resume | baseline_nominal_profile_v1 | 4.637 | 5.162 | 0.371 | 100.000 | 0.000 | True | ATE_RMSE_M, RPE_RMSE_M |
| s17_state_oscillation_safe_hold | urban_canyon_profile_v1 | 2.151 | 1.983 | 3.048 | 100.000 | 0.000 | False | MISSION_SUCCESS |
| s18_abort_terminal | baseline_nominal_profile_v1 | 4.637 | 5.132 | 0.331 | 0.000 | 0.000 | False | ATE_RMSE_M, RPE_RMSE_M, LOCALIZATION_CONTINUITY_PCT, MISSION_SUCCESS |
| s19_ew_mid_route_denial_hotspot | denial_corridor_profile_v1 | 4.637 | 4.521 | 0.342 | 100.000 | 0.000 | True | RPE_RMSE_M |
| s20_ew_decay_after_recovery | denial_corridor_profile_v1 | 3.298 | 3.293 | 0.342 | 100.000 | 0.000 | True | RPE_RMSE_M |
