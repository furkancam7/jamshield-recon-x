# Phase 12 - ROS2 Runtime Migration Backlog

## Goal

Open Phase 12 to migrate the current executable slice from script-driven file orchestration toward a node-based ROS2 runtime while preserving deterministic behavior and evaluation boundaries.

## Scope

- Define migration steps from current file-based execution to ROS2 node orchestration with parity gates.
- Keep runtime autonomy and evaluation boundaries intact during migration.
- Preserve current trust/fusion/mission/tactical decision semantics while changing runtime wiring.
- Establish a first executable ROS2 runtime loop with deterministic topic contracts.
- Maintain file-based replay/evaluation as the authoritative fallback until ROS2 parity checks pass.

## Current Slice Decisions

- This phase does not expand mission lifecycle states.
- The executable mission-state set remains:
  - `MISSION_EXECUTE`
  - `MISSION_DEGRADED`
  - `MISSION_FALLBACK`
  - `MISSION_SAFE_HOLD`
  - `MISSION_ABORT`
- `/truth/*` remains evaluation-only and must not be consumed by runtime autonomy nodes.
- `logger_node` and `evaluation_node` are migration targets; they are not considered complete at phase kickoff.

## Verification Targets

- Deterministic parity checks between ROS2 runtime outputs and the current file-based baseline on representative baseline scenarios.
- Runtime autonomy nodes must remain independent from `/truth/*` and `/evaluation/*`.
- Mission continuity remains the sole decision authority for mission state/action outputs.
- Regression and artifact gates continue to pass with schema `2.4` until a future, explicit schema bump.

## Landed Increment (2026-03-14, P12-A)

`P12-A parity slice` was landed as an in-process node-oriented runtime probe while keeping file-based execution as the authoritative fallback.

Delivered:

- `src/runtime/node_runner.py` with node wrappers for:
  - `scenario_orchestrator_node`
  - `vio_node`
  - `gnss_trust_node`
  - `fusion_node`
  - `trust_engine_node`
  - `mission_continuity_node`
- `scripts/run_node_scenario.sh` for single-scenario node-run execution
- `scripts/run_node_parity.sh` for baseline-vs-node parity probes
- `src/evaluation/node_parity_compare.py` for deterministic parity comparison artifacts
- `scripts/run_regression.sh` supports `ENABLE_NODE_PARITY=true` to run node parity as an optional gate
- `scripts/check_artifacts.sh` validates `node_parity_results.json/.md/.csv` when present (or required)
- Unit tests:
  - `tests/unit/test_node_runtime_parity.py`
  - `tests/unit/test_truth_boundary.py`

Residual after this increment:

- ROS2 launch/colcon runtime wiring is still not landed.
- `logger_node` and `evaluation_node` remain migration targets (file-based flow is still authoritative).
- `health_monitor_node` publication remains deferred.

## Landed Increment (2026-03-14, P12-B)

`P12-B launch-wired probe` was landed to introduce a ROS2 launch-style wiring artifact while keeping node execution deterministic and file-based replay/evaluation authoritative.

Delivered:

- `src/runtime/ros2_launch_runner.py`:
  - launch-plan generation for runtime/tactical/verification/operator node sets
  - launch-wiring boundary validation (`/truth/*` and `/evaluation/*` runtime isolation)
  - mission decision authority lock (`mission_continuity_node`)
  - `ros2_launch_plan.json/.md` artifact emission per launch probe run
- `scripts/run_ros2_launch_scenario.sh` for launch-wired single-scenario execution
- Unit tests:
  - `tests/unit/test_ros2_launch_runner.py`

Residual after this increment:

- Launch wiring is currently a probe artifact; ROS2 `launch.py` + colcon packaging is not landed yet.
- ROS2-native `logger_node` and `evaluation_node` execution remains deferred (file-based observer flow is authoritative).
- `health_monitor_node` publication remains deferred.

## Landed Increment (2026-03-14, P12-C)

`P12-C launch.py wiring + optional regression gate` was landed to make launch-probe execution first-class in scripts/regression without changing file-based baseline authority.

Delivered:

- `launch/runtime_probe.launch.py` repo-local launch wrapper with one-to-one runtime probe parameters:
  - `scenario_path`
  - `output_dir`
  - `config_path`
  - `run_id`
  - `enable_verification_nodes`
  - VIO overrides (`vio_state`, `vio_health_score`, `vio_unhealthy`)
- `scripts/run_ros2_launch_scenario.sh` now runs the launch wrapper by default.
- Optional regression gate:
  - `ENABLE_ROS2_LAUNCH_PROBE`
  - `ROS2_LAUNCH_SCENARIOS`
- New comparison artifacts from `src/evaluation/ros2_launch_probe_compare.py`:
  - `ros2_launch_probe_results.json/.md/.csv`
- Artifact checker and schema validation support:
  - `REQUIRE_ROS2_LAUNCH_PROBE`
  - `validate_ros2_launch_probe_results(...)` in `artifact_schema.py`
- Unit tests:
  - `tests/unit/test_ros2_launch_probe_compare.py`
  - launch-wrapper execution coverage in `tests/unit/test_ros2_launch_runner.py`

Residual after this increment:

- Launch wrapper is repo-local; ROS2 `launch.py` + colcon packaging is still not landed.
- ROS2-native `logger_node` and `evaluation_node` execution remains deferred (file-based observer flow is authoritative).
- `health_monitor_node` publication remains deferred.

## Landed Increment (2026-03-14, P12-D)

`P12-D colcon packaging + launch backend selection` was landed to close the ROS2 launch packaging gap while preserving P12-C baseline authority and optional-gate behavior.

Delivered:

- Minimal `ament_python` package skeleton at repo root for package name `jamshield_recon_x_sim`:
  - `package.xml`
  - `setup.py`
  - `setup.cfg`
  - `resource/jamshield_recon_x_sim`
- New ROS2-native launch entrypoint:
  - `launch/runtime_probe_colcon.launch.py`
  - launch arguments include `scenario_path`, `output_dir`, `config_path`, `run_id`, `enable_verification_nodes`, `vio_state`, `vio_health_score`, `vio_unhealthy`
  - runtime probe execution remains delegated to `runtime.ros2_launch_runner`
- `scripts/run_ros2_launch_scenario.sh` now supports explicit backend selection:
  - `ROS2_LAUNCH_BACKEND=repo_wrapper|colcon` (default `repo_wrapper`)
  - `colcon` backend calls `ros2 launch jamshield_recon_x_sim runtime_probe_colcon.launch.py ...`
  - fast-fail validation for missing `ros2` CLI or missing package prefix
- `scripts/run_regression.sh` forwards `ROS2_LAUNCH_BACKEND` into launch-probe gate execution.
- Unit coverage extended in `tests/unit/test_ros2_launch_runner.py` for:
  - repo-wrapper backend script execution
  - invalid backend rejection
  - missing-`ros2` fail-fast behavior for `colcon` backend

Residual after this increment:

- ROS2-native `logger_node` and `evaluation_node` execution remains deferred (file-based observer flow is authoritative).
- `health_monitor_node` publication remains deferred.

## Landed Increment (2026-03-16, P12-E)

`P12-E logger/evaluation hybrid bridge + optional verification gate` was landed to close the Phase 12 verification-node execution gap without changing file-based baseline authority.

Delivered:

- `src/runtime/verification_nodes.py` now executes:
  - `logger_node` hybrid checks over runtime/tactical/truth artifacts
  - `evaluation_node` hybrid replay + verdict checks for selected scenarios
  - per-scenario verification artifact: `<scenario>_verification_node_results.json`
- `src/runtime/ros2_launch_runner.py` now treats `enable_verification_nodes` as an execution trigger (not wiring-only).
- Optional regression verification gate:
  - `ENABLE_ROS2_VERIFICATION_PROBE`
  - `ROS2_VERIFICATION_SCENARIOS`
  - gate requires `ENABLE_ROS2_LAUNCH_PROBE=true`
- New comparison module and artifacts:
  - `src/evaluation/ros2_verification_probe_compare.py`
  - `ros2_verification_probe_results.json/.md/.csv`
- Artifact checker and schema validation support:
  - `REQUIRE_ROS2_VERIFICATION_PROBE`
  - `validate_ros2_verification_probe_results(...)` in `artifact_schema.py`
- Unit coverage:
  - `tests/unit/test_verification_nodes.py`
  - `tests/unit/test_ros2_verification_probe_compare.py`
  - regression gate guard coverage in `tests/unit/test_ros2_launch_runner.py`

Residual after this increment:

- `health_monitor_node` runtime publication remains deferred.
- File-based replay/evaluation remains the authoritative fallback path.

## Open Issue Closure Sweep (2026-03-16, Pre P12-F)

Source reconciliation was completed against `docs/roadmap/progress-tracker.md` and this backlog before landing P12-F implementation work.

Closed items during sweep:

- ROS2-native `logger_node`/`evaluation_node` execution gap was confirmed closed by P12-E evidence.
- Launch/probe migration gaps from P12-C/P12-D/P12-E were confirmed closed where still referenced as open in intermediate notes.

Open items after sweep:

- `health_monitor_node` runtime publication (P12-F target in this increment).
- Trust calibration tuning residual (tracked as cross-phase residual).

## Landed Increment (2026-03-16, P12-F)

`P12-F issue-closure sweep + health_monitor publisher/wiring` was landed to close the remaining Phase 12 runtime publication gap while preserving file-based baseline authority.

Delivered:

- Runtime health monitor publication in `src/runtime/node_runner.py` via deterministic `health_monitor_node` execution:
  - scenario health timeline artifact: `<scenario>_mission_health.json`
  - fault event artifact: `<scenario>_fault_events.json`
- Launch-plan wiring update in `src/runtime/ros2_launch_runner.py`:
  - `health_monitor_node` now appears in `ros2_launch_plan.json/.md` runtime node set.
- Optional health-monitor regression gate:
  - `ENABLE_HEALTH_MONITOR_PROBE`
  - `HEALTH_MONITOR_SCENARIOS`
  - `REQUIRE_HEALTH_MONITOR_PROBE`
- New health-monitor probe comparison module and artifacts:
  - `src/evaluation/health_monitor_probe_compare.py`
  - `health_monitor_probe_results.json/.md/.csv`
- Schema/checker support:
  - `validate_mission_health_timeline(...)`
  - `validate_fault_events(...)`
  - `validate_health_monitor_probe_results(...)`
  - conditional checker support in `scripts/check_artifacts.sh`
- Unit coverage:
  - `tests/unit/test_health_monitor_node.py`
  - `tests/unit/test_health_monitor_probe_compare.py`
  - launch wiring extension checks in `tests/unit/test_ros2_launch_runner.py`

Residual after this increment:

- File-based replay/evaluation remains the authoritative fallback path during migration.
- Trust calibration tuning remains a cross-phase residual and is not changed by P12-F.
- Consumer-side mission/trust/tactical decision semantics remain unchanged by design; this increment only adds health publication/observation artifacts.

## Phase 12 Exit Closure (2026-03-18)

Phase 12 exit checks were rerun on `prod` HEAD (`software_revision=dd46183357c63c5f5cf6ac937355c3ed1ca57b88`) and recorded as final closure evidence.

Validation matrix (PASS):

- `python -m unittest discover -s tests/unit` (executed with `PYTHONPATH=src`)
- `bash scripts/run_regression.sh p12_exit_reval_base_20260318T1257Z`
- `ENABLE_ROS2_LAUNCH_PROBE=true ... bash scripts/run_regression.sh p12_exit_reval_launch_20260318T1259Z`
- `ENABLE_ROS2_LAUNCH_PROBE=true ENABLE_ROS2_VERIFICATION_PROBE=true ... bash scripts/run_regression.sh p12_exit_reval_verify_20260318T1301Z`
- `ENABLE_HEALTH_MONITOR_PROBE=true ... bash scripts/run_regression.sh p12_exit_reval_health_20260318T1303Z`
- `bash scripts/check_artifacts.sh artifacts/runs/p12_exit_reval_health_20260318T1303Z`

Closure outcome:

- Phase 12 is considered complete and handed off to `Phase 13 - Deployment and Ops Hardening`.
- Runtime/evaluation boundaries and mission authority lock remain unchanged.
- Residual remains: cross-phase trust calibration tuning.

## Non-Goals

- Implementing hardware drivers or field-integration behaviors
- Feeding ground truth into runtime autonomy decisions
- Rewriting mission lifecycle to include `MISSION_PREPARE` or `MISSION_COMPLETE` in the executable slice
