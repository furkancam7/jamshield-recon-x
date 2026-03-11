"""CLI entry point for GNSS trust evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.config import load_app_config
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator

from .trust_service import TrustService

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "sim" / "default.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate GNSS trust for a scenario.")
    parser.add_argument("scenario", help="Path to the scenario YAML file.")
    parser.add_argument(
        "--vio-unhealthy",
        action="store_true",
        help="Force the simplified VIO health input to false.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the simulation config file.",
    )
    args = parser.parse_args()

    config = load_app_config(args.config)
    manifest = load_manifest(args.scenario)
    snapshot = ScenarioOrchestrator(manifest).build_snapshot()
    assessment = TrustService(config.trust).evaluate(
        snapshot, vio_healthy=not args.vio_unhealthy
    )

    print(json.dumps(assessment.__dict__, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
