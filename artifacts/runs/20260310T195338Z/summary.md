# Regression Summary

- Run ID: `20260310T195338Z`
- Overall result: `PASS`

## Scenario Results

| Scenario | GNSS State | Trust Score | Mission State | ATE RMSE |
| --- | --- | ---: | --- | ---: |
| s1_nominal | nominal | 0.960 | MISSION_NORMAL | 0.500 |
| s2_gnss_degraded_corridor | degraded | 0.590 | MISSION_DEGRADED | 3.000 |
| s3_gnss_denied_zone | denied | 0.050 | MISSION_EMERGENCY_LAND | 8.000 |

## Checks

- `trust_ordering`: PASS - Expected nominal trust score > degraded trust score > denied trust score.
- `denied_not_normal`: PASS - Denied scenario must not end in MISSION_NORMAL.
- `degraded_not_denied`: PASS - Degraded scenario must not be classified as denied.
- `nominal_not_emergency`: PASS - Nominal scenario must not collapse to MISSION_EMERGENCY_LAND.
