# JamShield Recon-X Progress Tracker

## Usage Rules

- This file is the living phase tracker for the repo.
- Each phase may be only one of: `Not Started`, `In Progress`, `Blocked`, `Completed`.
- A phase is not considered closed until its exit checks are verified.
- Code and artifacts describe current behavior; docs describe intended architecture. Any drift must be called out explicitly.

## Current Status

- Last updated: `2026-03-25`
- Working reference: `P12 completed / P13 in progress`
- Active phase: `Phase 13 - Deployment and Ops Hardening`
- Program goal: `Simulation Production`

## Phase Table

| Phase | Name | Status | Last Update | Evidence | Open Gap |
| --- | --- | --- | --- | --- | --- |
| 0 | Architecture Lock | Completed | 2026-03-11 | `docs/architecture/terminology-lock.md`, `docs/decisions/ADR-001..003` | Periodic docs drift review |
| 1 | First Executable Vertical Slice | Completed | 2026-03-11 | `src/scenario_orchestrator/main.py`, `scripts/smoke_test.sh` | Smoke re-validation after major refactors |
| 2 | Determinism and Regression Baseline | Completed | 2026-03-11 | `scripts/run_regression.sh`, `src/evaluation/summary_report.py` | Scenario breadth should keep expanding |
| 3 | Config and Artifact Hardening | Completed | 2026-03-11 | `docs/roadmap/phase-03-closure.md`, `artifacts/runs/phase3_validation/` | Schema drift review remains ongoing |
| 4 | VIO Health Upgrade | Completed | 2026-03-11 | `docs/roadmap/phase-04-backlog.md`, `docs/roadmap/phase-05-closure.md` | Compatibility cleanup follow-up |
| 5 | Real VIO Metric Skeleton | Completed | 2026-03-11 | `docs/roadmap/phase-05-closure.md`, `artifacts/runs/p5_validation/` | Fusion follow-up completed later |
| 6 | Localization Fusion | Completed | 2026-03-13 | `src/localization_fusion/`, `tests/unit/test_localization_fusion.py` | Periodic fusion drift review |
| 7 | Trust Engine Maturity | Completed | 2026-03-13 | `docs/roadmap/phase-07-closure.md`, `artifacts/runs/20260313T091105Z/` | Calibration tuning residual gap |
| 8 | Mission Continuity V2 | Completed | 2026-03-13 | `docs/roadmap/phase-08-closure.md`, `artifacts/runs/20260313T093610Z/` | Tactical-layer consumption was deferred |
| 9 | EW Risk Map | Completed | 2026-03-13 | `docs/roadmap/phase-09-closure.md`, `artifacts/runs/20260313T100900Z/` | Tactical summary integration |
| 10 | Tactical Summary | Completed | 2026-03-13 | `docs/roadmap/phase-10-closure.md`, `artifacts/runs/20260313T105100Z/` | Health-driven wording still deferred |
| 11 | Replay and Evaluation Hardening | Completed | 2026-03-13 | `docs/roadmap/phase-11-closure.md`, `artifacts/runs/20260313T1325Z_plan_probe/` | ROS2 node-based runtime migration deferred to Phase 12 |
| 12 | ROS2 Runtime Migration | Completed | 2026-03-18 | `launch/runtime_probe.launch.py`, `launch/runtime_probe_colcon.launch.py`, `package.xml`, `setup.py`, `setup.cfg`, `src/runtime/node_runner.py`, `src/runtime/ros2_launch_runner.py`, `src/runtime/verification_nodes.py`, `src/health_monitor/service.py`, `src/health_monitor/artifacts.py`, `scripts/run_node_scenario.sh`, `scripts/run_node_parity.sh`, `scripts/run_ros2_launch_scenario.sh`, `scripts/run_regression.sh`, `scripts/check_artifacts.sh`, `src/evaluation/node_parity_compare.py`, `src/evaluation/ros2_launch_probe_compare.py`, `src/evaluation/ros2_verification_probe_compare.py`, `src/evaluation/health_monitor_probe_compare.py`, `tests/unit/test_node_runtime_parity.py`, `tests/unit/test_node_parity_compare.py`, `tests/unit/test_ros2_launch_runner.py`, `tests/unit/test_ros2_launch_probe_compare.py`, `tests/unit/test_verification_nodes.py`, `tests/unit/test_ros2_verification_probe_compare.py`, `tests/unit/test_health_monitor_node.py`, `tests/unit/test_health_monitor_probe_compare.py`, `docs/roadmap/phase-12-backlog.md`, `artifacts/runs/p12_exit_reval_health_20260318T1303Z/` | Cross-phase trust calibration tuning residual remains |
| 13 | Deployment and Operations Hardening | In Progress | 2026-03-25 | `.github/workflows/ci-minimum-gate.yml`, `.gitignore`, `scripts/bootstrap.sh`, `docs/runbooks/local-setup.md`, `docs/runbooks/run-simulation.md`, `docs/runbooks/release-ops.md`, `docs/runbooks/known-limitations.md`, `docs/runbooks/troubleshooting.md`, `docs/roadmap/progress-tracker.md` | Phase completion review tracking remains on epic `#14` |
| 14 | Hardware-Portability Layer | Not Started | - | - | Phase not started |
| 15 | Field Transition Preparation | Not Started | - | - | Phase not started |

## Active Phase Detail

### Phase 13 - Deployment and Ops Hardening

Purpose:

- Establish reproducible CI and ops baseline gates on `main` and `prod` without changing runtime contracts.

Status:

- `In Progress`

Initial scope in this phase:

- Land `P13-A` minimum CI gate (unit tests, shell syntax smoke, artifact contract smoke).
- Add optional full-matrix CI lane for scheduled/manual regression gates.
- Close generated-file tracking drift (`__pycache__` and transient P12 run outputs) using forward cleanup.
- Keep runtime/evaluation authority boundaries unchanged while improving deployment hygiene.

Phase 13 progress update (2026-03-25):

- `P13-A` closure hygiene completed with issue evidence and closure (`#68`).
- `P13-B` bootstrap/environment standardization landed:
  - `scripts/bootstrap.sh` now validates `PYTHON_BIN`, standardizes `PYTHONPATH`, and fail-fast checks `pyyaml`.
  - runbook alignment completed for default file-based flow and optional `ROS2_LAUNCH_BACKEND=colcon`.
- `P13-C` release/runbook hardening landed:
  - release template/checklist and decision policy documented in `docs/runbooks/release-ops.md`.
  - current-slice operational limits documented in `docs/runbooks/known-limitations.md`.
  - release preflight order and CI lane interpretation clarified in `docs/runbooks/run-simulation.md`.
  - rollback/recovery playbook documented in `docs/runbooks/troubleshooting.md`.
- Child issues for this phase are now closed; epic-level phase completion review remains tracked on `#14`.

### Phase 12 - ROS2 Runtime Migration (Closed)

Purpose:

- Migrate from the file-driven current slice toward a ROS2 node-based runtime while preserving deterministic behavior, trust/mission authority boundaries, and evaluation isolation.

Status:

- `Completed`

Scope in this phase:

- Open a parity-first migration path from script orchestration to ROS2 node execution.
- Keep mission-state and localization semantics unchanged from the Phase 11 baseline.
- Enforce `/truth/*` evaluation-only boundaries during runtime migration.
- Stage `logger_node` and `evaluation_node` integration behind deterministic parity checks.
- Keep current file-based replay/evaluation flow available until ROS2 parity gates are satisfied.

Phase 12-A landed:

- In-process node-oriented runtime probe is available through `src/runtime/node_runner.py`.
- Deterministic parity tooling for baseline-vs-node comparison is available through `src/evaluation/node_parity_compare.py`.
- Baseline scripts now include node-run helpers (`scripts/run_node_scenario.sh`, `scripts/run_node_parity.sh`).
- Baseline regression can run an optional node parity gate via `ENABLE_NODE_PARITY=true`.

Phase 12-B landed:

- Launch-wired runtime probe is available through `src/runtime/ros2_launch_runner.py`.
- Launch probe script `scripts/run_ros2_launch_scenario.sh` writes `ros2_launch_plan.json/.md`.
- Launch-plan validation enforces runtime truth boundary and mission decision authority lock.
- Unit coverage for launch-plan validation/runtime parity is available in `tests/unit/test_ros2_launch_runner.py`.

Phase 12-C landed:

- Repo-local launch wrapper `launch/runtime_probe.launch.py` is wired for runtime probe parameters.
- Baseline regression can run an optional ROS2 launch probe gate via `ENABLE_ROS2_LAUNCH_PROBE=true`.
- Launch probe comparison artifacts `ros2_launch_probe_results.json/.md/.csv` are emitted and schema-validated.
- Unit coverage for launch-probe comparison is available in `tests/unit/test_ros2_launch_probe_compare.py`.

Phase 12-D landed:

- Minimal `ament_python` package skeleton (`package.xml`, `setup.py`, `setup.cfg`, `resource/jamshield_recon_x_sim`) was added for package name `jamshield_recon_x_sim`.
- ROS2-native launch entrypoint `launch/runtime_probe_colcon.launch.py` now runs the runtime probe through package launch args.
- `scripts/run_ros2_launch_scenario.sh` supports explicit `ROS2_LAUNCH_BACKEND=repo_wrapper|colcon` (default `repo_wrapper`) with fail-fast checks for missing `ros2`/package.
- `scripts/run_regression.sh` forwards `ROS2_LAUNCH_BACKEND` when ROS2 launch probe gate is enabled.

Phase 12-E landed:

- Hybrid bridge verification-node runners are available through `src/runtime/verification_nodes.py`.
- `enable_verification_nodes` now triggers verification execution in `src/runtime/ros2_launch_runner.py`.
- Baseline regression can run an optional verification gate via `ENABLE_ROS2_VERIFICATION_PROBE=true`.
- Verification probe comparison artifacts `ros2_verification_probe_results.json/.md/.csv` are emitted and schema-validated.
- Unit coverage for verification runners and probe comparison is available in `tests/unit/test_verification_nodes.py` and `tests/unit/test_ros2_verification_probe_compare.py`.

Open issue closure sweep (pre P12-F):

- Completed P12-E scope items were closed in tracker/backlog references:
  - ROS2 `logger_node`/`evaluation_node` execution gap
  - launch/probe migration items already delivered by P12-C/P12-D/P12-E
- Remaining open target for Phase 12 implementation was narrowed to `health_monitor_node` runtime publication.

Phase 12-F landed:

- Deterministic `health_monitor_node` publication is now integrated in `src/runtime/node_runner.py`.
- Scenario-level health artifacts are emitted:
  - `<scenario>_mission_health.json`
  - `<scenario>_fault_events.json`
- `ros2_launch_plan` wiring now includes `health_monitor_node` in runtime nodes.
- Baseline regression supports optional health-monitor gate:
  - `ENABLE_HEALTH_MONITOR_PROBE`
  - `HEALTH_MONITOR_SCENARIOS`
  - `REQUIRE_HEALTH_MONITOR_PROBE`
- Health-monitor comparison artifacts `health_monitor_probe_results.json/.md/.csv` are emitted and schema-validated.
- Unit coverage is available in `tests/unit/test_health_monitor_node.py` and `tests/unit/test_health_monitor_probe_compare.py`.

Exit checks:

- A first ROS2 runtime loop executes representative baseline scenarios with deterministic outputs.
- Runtime autonomy remains independent from `/truth/*` and `/evaluation/*`.
- Mission continuity remains the only mission decision authority in the runtime graph.
- File-based fallback flow remains usable until ROS2 parity and stability checks pass.

Known residuals:

- Phase 11 file-based replay/evaluation remains the authoritative fallback during migration.
- Full lifecycle mission-state expansion remains deferred and is not part of this phase kickoff.
- Trust calibration tuning remains a cross-phase residual and is unaffected by P12-F.

## Completed Phase Notes

### Phase 9 - EW Risk Map

- Deterministic route-progress-based EW risk map is complete.
- Schema `2.2`, EW map artifacts, and EW metrics bundle were verified.
- Reference run: `artifacts/runs/20260313T100900Z/`.

### Phase 11 - Replay and Evaluation Hardening

- Runtime trace, pseudo-truth trace, deterministic replay, and offline evaluation bundles are complete in the file-based slice.
- Schema `2.4` and replay/evaluation gates were verified.
- Reference run: `artifacts/runs/20260313T1325Z_plan_probe/`.

### Phase 8 - Mission Continuity V2

- Stateful mission continuity, dwell, timeout, oscillation guard, and mission audit artifacts are complete.
- Schema `2.1` was verified.
- Reference run: `artifacts/runs/20260313T093610Z/`.

### Phase 7 - Trust Engine Maturity

- Central trust engine, schema `2.0`, and trust calibration bundle are complete.
- Reference run: `artifacts/runs/20260313T091105Z/`.

## Open Items

- Trust calibration residual band mismatches still need a future tuning pass.

## Decision Notes

- `Simulation Production first` remains the governing rule.
- Phase transitions require verified gates, not just code presence.
- ROS2 migration remains intentionally deferred until the simulation slice is hardened.
- `/mission/health` remains under `health_monitor_node` publication; mission decision authority remains `mission_continuity_node`.

## Change Log

| Date | Change |
| --- | --- |
| 2026-03-11 | Initial tracker created in alignment with the master roadmap. |
| 2026-03-13 | Phases 6, 7, 8, and 9 were marked completed with supporting closure artifacts. |
| 2026-03-13 | Phase 10 was closed and active phase moved to Phase 11 with file-based replay/evaluation hardening. |
| 2026-03-13 | Phase 11 was closed with reference replay/evaluation evidence and active phase moved to Phase 12 kickoff. |
| 2026-03-14 | Phase 12-A parity slice landed with in-process node runtime probe, node parity compare tooling, and unit coverage. |
| 2026-03-14 | Node parity gate was integrated into `run_regression.sh` as an optional Phase 12 migration check. |
| 2026-03-14 | Phase 12-B launch-wired probe landed with `ros2_launch_plan` artifacts and launch-plan boundary validation. |
| 2026-03-14 | Phase 12-C landed with `launch/runtime_probe.launch.py` wiring and optional regression gate for ROS2 launch probe comparison. |
| 2026-03-14 | Phase 12-D landed with `ament_python`/colcon packaging and `ROS2_LAUNCH_BACKEND` selection for launch probe execution. |
| 2026-03-16 | Phase 12-E landed with hybrid `logger_node`/`evaluation_node` execution and optional ROS2 verification probe gate. |
| 2026-03-16 | Phase 12 issue-closure sweep was completed and P12-F landed `health_monitor_node` publication/wiring with optional health-monitor regression gate. |
| 2026-03-18 | Phase 12 exit matrix was revalidated on `prod` HEAD and Phase 12 was moved to `Completed`; active phase moved to Phase 13. |
| 2026-03-18 | P13-A kickoff landed `.gitignore` forward-cleanup policy and `main+prod` CI minimum gate workflow with full-matrix manual/scheduled lane. |
| 2026-03-25 | P13-A issue closure hygiene was completed (`#68`) with CI evidence and epic sync update on `#14`. |
| 2026-03-25 | P13-B landed bootstrap/env standardization (`scripts/bootstrap.sh`) and runbook alignment for file-based default plus optional `colcon` backend. |
| 2026-03-25 | P13-C landed release template/checklist, known-limitations runbook, CI-gated release preflight notes, and rollback/recovery troubleshooting playbook. |
