# Known Limitations

## Purpose

This runbook captures current-slice operational limits so release and regression decisions are made against explicit constraints.

## Current-Slice Limits

1. File-based runtime artifacts remain the operational authority for replay/evaluation in the default flow.
2. ROS2 launch execution defaults to `ROS2_LAUNCH_BACKEND=repo_wrapper`.
3. `ROS2_LAUNCH_BACKEND=colcon` is optional and requires ROS2 install, workspace build, and package discovery.
4. `logger_node` and `evaluation_node` are exercised via hybrid bridge flows for launch/verification probes, not full ROS2-native end-to-end runtime ownership.
5. Trust calibration tuning remains a cross-phase residual and may require targeted follow-up despite green baseline gates.

## Deferred or Future Items

- Full hardware-portability implementation belongs to Phase 14.
- Field-transition and HIL preparation belongs to Phase 15.
- Any runtime behavior changes to mission authority or `/truth/*` boundaries require explicit architecture decision and are out of this slice.

## Operational Impact

- Release decisions must treat missing full-matrix evidence as a blocker.
- Failures in optional probe lanes should be tracked with explicit scope notes (launch, verification, or health).
- Drift between docs and runtime behavior must be logged in tracker/issue notes before phase closure.
