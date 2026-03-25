# Local Setup

## Purpose

This runbook defines the expected local environment for simulation-first development and evaluation.

## Baseline Environment

- operating system: Linux or WSL2
- shell: `bash`
- language runtime: Python (repo scripts default to `python3`)
- required Python package: `pyyaml`
- log/artifact output: file-based artifacts under `artifacts/runs/<run_id>/`

Default execution path is repo-local/file-based (`scripts/run_scenario.sh`, `scripts/run_regression.sh`).

Optional ROS2/colcon backend:

- middleware: ROS2
- build system: `colcon`
- package: `jamshield_recon_x_sim`
- launch backend env: `ROS2_LAUNCH_BACKEND=colcon`

## Required Capabilities

- deterministic simulator clock control
- offline replay support
- access to scenario manifest files
- storage capacity for full-fidelity runtime and truth logs
- ability to run repo shell scripts from project root

## Canonical Setup Steps

1. Ensure a Python interpreter is available (`python3` by default or set `PYTHON_BIN`).
2. Run `bash scripts/bootstrap.sh` from repo root to standardize `PYTHONPATH` and validate dependencies.
3. Verify baseline commands work:
   - `bash scripts/run_scenario.sh scenarios/baseline/s1_nominal.yaml artifacts/runs/<run_id>`
   - `bash scripts/check_artifacts.sh artifacts/runs/<run_id>`
4. For optional ROS2 `colcon` backend, build and source workspace:
   - `colcon build --symlink-install`
   - `source install/setup.bash`
5. Use launch backend explicitly when needed:
   - default: `ROS2_LAUNCH_BACKEND=repo_wrapper`
   - optional ROS2: `ROS2_LAUNCH_BACKEND=colcon`

## Setup Validation

A local environment is considered ready when:

- `bash scripts/bootstrap.sh` completes without dependency or interpreter errors
- baseline scenario run creates expected artifacts
- `bash scripts/check_artifacts.sh` passes on the produced run directory
- if `ROS2_LAUNCH_BACKEND=colcon` is used, package discovery and launch succeed

## Non-Scope

- USB device setup
- hardware timestamping
- real GNSS receiver configuration
- ROS2 installation for users who stay on repo-wrapper default backend

These belong to the Future hardware integration phase.
