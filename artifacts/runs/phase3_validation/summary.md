# Regression Summary

- Run ID: `phase3_validation`
- Overall result: `PASS`

## Scenario Results

- Config ID: `sim-v1`
- Software revision: `25d5a04269334b183a581013344975665e41765c`

| Scenario | GNSS State | Trust Score | Mission Confidence | Mission State | ATE RMSE |
| --- | --- | ---: | ---: | --- | ---: |
| s1_nominal | nominal | 0.960 | 0.970 | MISSION_NORMAL | 0.500 |
| s2_gnss_degraded_corridor | degraded | 0.590 | 0.693 | MISSION_DEGRADED | 3.000 |
| s3_gnss_denied_zone | denied | 0.050 | 0.038 | MISSION_EMERGENCY_LAND | 8.000 |

## Checks

- `trust_ordering`: PASS - Expected nominal trust score > degraded trust score > denied trust score.
- `denied_not_normal`: PASS - Denied scenario must not end in MISSION_NORMAL.
- `degraded_not_denied`: PASS - Degraded scenario must not be classified as denied.
- `nominal_not_emergency`: PASS - Nominal scenario must not collapse to MISSION_EMERGENCY_LAND.
- `nominal_minimum_trust_threshold`: PASS - Nominal scenario trust score must remain at or above 0.90.
- `denied_allowed_mission_states`: PASS - Denied scenario must end in the allowed denied-state set.
