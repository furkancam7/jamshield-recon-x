# Reason Codes

## Usage Rules

- Reason codes are stable identifiers, not free text.
- `primary_reason_code` is the first causal explanation for a decision.
- `reason_codes` may include supporting context in deterministic order.
- Codes are shared across runtime logs, replay, and evaluation.

## GNSS Trust Codes

| Code | Meaning |
| --- | --- |
| `GNSS_OK` | GNSS behavior is within nominal limits |
| `GNSS_HDOP_HIGH` | Horizontal dilution of precision exceeded threshold |
| `GNSS_SAT_COUNT_LOW` | Satellite count dropped below minimum requirement |
| `GNSS_TEMPORAL_JITTER` | Fix-to-fix variation exceeded temporal stability limit |
| `GNSS_KINEMATIC_MISMATCH` | GNSS motion estimate disagrees with inertial or VIO motion |
| `GNSS_DENIAL_SUSPECT` | GNSS signal loss pattern matches denial behavior |
| `GNSS_SPOOF_LIKE_DRIFT` | GNSS bias drift pattern matches spoof-like behavior |
| `GNSS_RECOVERY_STABLE` | GNSS recovered and remained stable for recovery dwell |

## Trust Engine Codes

| Code | Meaning |
| --- | --- |
| `TRUST_GNSS_PRIMARY` | GNSS selected as primary source |
| `TRUST_BLEND_ALLOWED` | GNSS and VIO both allowed in blended mode |
| `TRUST_VIO_PRIMARY` | VIO selected as primary source |
| `TRUST_GNSS_GATED` | GNSS excluded from fusion update |
| `TRUST_VIO_GATED` | VIO excluded from fusion update |
| `TRUST_HYSTERESIS_HOLD` | Transition delayed by dwell or hysteresis rule |
| `TRUST_NO_VALID_SOURCE` | No localization source satisfies minimum confidence |

## Mission Continuity Codes

| Code | Meaning |
| --- | --- |
| `MISSION_PREPARE_WAITING_FOR_LOCK` | Mission is waiting for an initial valid localization source |
| `MISSION_CONTINUE_NOMINAL` | Mission continues under nominal localization conditions |
| `MISSION_REDUCE_SPEED_GNSS_DEGRADED` | Mission speed reduced because GNSS trust dropped |
| `MISSION_SWITCH_TO_VIO` | Mission switched to VIO-led localization |
| `MISSION_HOLD_LOCALIZATION_CONTINGENCY` | Mission holding because no source satisfies continuity criteria |
| `MISSION_ABORT_HEALTH_CRITICAL` | Mission aborted because health severity became critical |
| `MISSION_ABORT_TIMEOUT` | Mission aborted after contingency timeout |
| `MISSION_COMPLETE_ROUTE_FINISHED` | Mission reached the terminal waypoint |

## Health Codes

| Code | Meaning |
| --- | --- |
| `HEALTH_OK` | Subsystem nominal |
| `HEALTH_SYNC_STALE` | Sync status is stale or missing |
| `HEALTH_VIO_STALLED` | VIO estimate not updating at required rate |
| `HEALTH_FUSION_INVALID` | Fused estimate invalid or stale |
| `HEALTH_TRUST_STALE` | Trust decision not updating at required rate |
| `HEALTH_NODE_HEARTBEAT_LOST` | Node heartbeat timeout occurred |

## Evaluation Codes

| Code | Meaning |
| --- | --- |
| `EVAL_PASS` | Run passed all acceptance checks |
| `EVAL_FAIL_METRIC_THRESHOLD` | One or more metrics violated scenario acceptance thresholds |
| `EVAL_FAIL_MISSION_SUCCESS` | Mission success criteria were not satisfied |
| `EVAL_INVALID_TRUTH_MISSING` | Evaluation-only ground truth missing or incomplete |
| `EVAL_INVALID_REPLAY_DIVERGENCE` | Deterministic replay diverged from recorded runtime outputs |
| `EVAL_INVALID_MANIFEST_HASH` | Manifest hash does not match recorded run metadata |
| `EVAL_INVALID_LOG_CORRUPTION` | Required log artifacts are corrupt or unreadable |
