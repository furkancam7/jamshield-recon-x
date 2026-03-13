# Regression Summary

- Run ID: `p5_validation`
- Overall result: `PASS`

## Scenario Results

- Config ID: `sim-v1`
- Software revision: `2e31a5ba1f7682acf36fe0201cdbf92769173b61`

| Scenario | GNSS State | Trust Score | Mission Confidence | Effective VIO | Mission State | VIO Profile | ATE RMSE |
| --- | --- | ---: | ---: | --- | --- | --- | ---: |
| s1_nominal | nominal | 0.960 | 0.970 | good | MISSION_NORMAL | nominal_v1 | 0.500 |
| s2_gnss_degraded_corridor | degraded | 0.590 | 0.693 | good | MISSION_DEGRADED | nominal_v1 | 3.000 |
| s3_gnss_denied_zone | denied | 0.050 | 0.287 | good | MISSION_FALLBACK | nominal_v1 | 8.000 |
| s4_denied_vio_good | denied | 0.050 | 0.287 | good | MISSION_FALLBACK | nominal_v1 | 8.000 |
| s5_denied_vio_weak | denied | 0.050 | 0.287 | weak | MISSION_SAFE_HOLD | weak_texture_v1 | 8.000 |
| s6_denied_vio_lost | denied | 0.050 | 0.038 | lost | MISSION_EMERGENCY_LAND | lost_tracking_v1 | 8.000 |
| s7_conflict_score_dominates | denied | 0.050 | 0.038 | lost | MISSION_EMERGENCY_LAND | lost_tracking_v1 | 8.000 |
| s8_conflict_state_dominates | denied | 0.050 | 0.038 | lost | MISSION_EMERGENCY_LAND | nominal_v1 | 8.000 |

## Checks

- `trust_ordering`: PASS - Expected nominal trust score > degraded trust score > denied trust score.
- `denied_not_normal`: PASS - Denied scenario must not end in MISSION_NORMAL.
- `degraded_not_denied`: PASS - Degraded scenario must not be classified as denied.
- `nominal_not_emergency`: PASS - Nominal scenario must not collapse to MISSION_EMERGENCY_LAND.
- `nominal_minimum_trust_threshold`: PASS - Nominal scenario trust score must remain at or above 0.90.
- `denied_allowed_mission_states`: PASS - Denied scenario must end in the allowed denied-state set.
- `p4_vio_good_fallback`: PASS - Denied + nominal VIO pipeline must stay in fallback-capable state.
- `p4_vio_weak_safe_hold`: PASS - Denied + weak-texture VIO pipeline must produce weak VIO and safe hold.
- `p4_vio_lost_emergency`: PASS - Denied + lost-tracking VIO pipeline must force emergency landing path.
- `p4_conflict_score_dominates`: PASS - Conflict case with reported good state and lost pipeline score must resolve to lost.
- `p4_conflict_state_dominates`: PASS - Conflict case with lost reported state must preserve lost effective state.
- `vio_metrics_source_pipeline_v1`: PASS - All regression artifacts must record pipeline_v1 VIO metrics.
