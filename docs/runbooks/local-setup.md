# Local Setup

## Purpose

This runbook defines the expected local environment for simulation-first development and evaluation.

## Baseline Environment

- operating system: Linux or WSL2
- middleware: ROS2
- language runtime: Python for orchestration and evaluation tooling
- build system: `colcon`
- log format: ROS2 bag or equivalent deterministic event log

If the repository has not yet provisioned these components, that gap is a Future system extension rather than a runtime exception.

## Required Capabilities

- deterministic simulator clock control
- ROS2 topic recording
- offline replay support
- access to scenario manifest files
- storage capacity for full-fidelity runtime and truth logs

## Canonical Setup Steps

1. Install the ROS2 distribution supported by the repository.
2. Install Python dependencies required for scenario orchestration and evaluation.
3. Build the workspace with `colcon build --symlink-install`.
4. Source the generated workspace environment before any run or replay command.
5. Verify that scenario manifests and acceptance profiles are readable from `docs/`.

## Setup Validation

A local environment is considered ready when:

- the workspace builds without missing ROS2 packages
- the simulator can run with a fixed seed
- bag recording starts successfully
- replay tooling can read a recorded run without schema errors

## Non-Scope

- USB device setup
- hardware timestamping
- real GNSS receiver configuration

These belong to the Future hardware integration phase.
