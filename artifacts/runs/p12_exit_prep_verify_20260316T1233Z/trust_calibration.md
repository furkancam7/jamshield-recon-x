# Trust Calibration

- Run ID: `p12_exit_prep_verify_20260316T1233Z`

| Scenario | GNSS | VIO | Sync | Loc Conf | Mission Conf | Primary Reason | Expected | Observed | Failed Checks |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| s10_fusion_degraded_fused | 0.590 | 0.823 | 1.000 | 0.702 | 0.676 | trust_inputs_nominal | medium | medium | - |
| s11_fusion_denied_vio_only | 0.050 | 0.825 | 1.000 | 0.760 | 0.450 | gnss_denial_suspected | medium | medium | - |
| s12_fusion_dead_reckoning | 0.050 | 0.092 | 1.000 | 0.073 | 0.098 | localization_confidence_low | low | low | - |
| s13_sync_low_nominal | 0.960 | 0.833 | 0.200 | 0.913 | 0.882 | sync_quality_low | high | high | - |
| s14_sync_low_denied_good | 0.050 | 0.823 | 0.200 | 0.758 | 0.409 | sync_quality_low | medium | low | band_mismatch |
| s15_safe_hold_timeout_abort | 0.050 | 0.759 | 1.000 | 0.695 | 0.433 | gnss_denial_suspected | low | low | - |
| s16_recovery_dwell_delays_resume | 0.960 | 0.825 | 1.000 | 0.911 | 0.920 | trust_inputs_nominal | high | high | - |
| s17_state_oscillation_safe_hold | 0.590 | 0.833 | 1.000 | 0.708 | 0.695 | trust_inputs_nominal | medium | medium | - |
| s18_abort_terminal | 0.960 | 0.823 | 1.000 | 0.910 | 0.920 | trust_inputs_nominal | high | high | - |
| s19_ew_mid_route_denial_hotspot | 0.960 | 0.822 | 1.000 | 0.910 | 0.904 | trust_inputs_nominal | high | high | - |
| s1_nominal | 0.960 | 0.799 | 1.000 | 0.903 | 0.913 | trust_inputs_nominal | high | high | - |
| s20_ew_decay_after_recovery | 0.960 | 0.833 | 1.000 | 0.913 | 0.922 | trust_inputs_nominal | high | high | - |
| s2_gnss_degraded_corridor | 0.590 | 0.796 | 1.000 | 0.688 | 0.666 | trust_inputs_nominal | medium | medium | - |
| s3_gnss_denied_zone | 0.050 | 0.825 | 1.000 | 0.760 | 0.450 | gnss_denial_suspected | medium | medium | - |
| s4_denied_vio_good | 0.050 | 0.806 | 1.000 | 0.742 | 0.441 | gnss_denial_suspected | medium | low | band_mismatch |
| s5_denied_vio_weak | 0.050 | 0.611 | 1.000 | 0.550 | 0.345 | gnss_denial_suspected | low | low | - |
| s6_denied_vio_lost | 0.050 | 0.092 | 1.000 | 0.073 | 0.098 | localization_confidence_low | low | low | - |
| s7_conflict_score_dominates | 0.050 | 0.073 | 1.000 | 0.061 | 0.090 | localization_confidence_low | low | low | - |
| s8_conflict_state_dominates | 0.050 | 0.825 | 1.000 | 0.760 | 0.450 | gnss_denial_suspected | low | medium | band_mismatch |
| s9_fusion_gnss_primary | 0.960 | 0.825 | 1.000 | 0.911 | 0.920 | trust_inputs_nominal | high | high | - |
