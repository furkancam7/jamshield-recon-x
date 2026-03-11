"""CLI entry point for mission continuity state evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

from common.config import load_app_config
from .state_machine import MissionStateMachine

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "sim" / "default.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate mission continuity state.")
    parser.add_argument("mission_confidence", type=float)
    parser.add_argument("gnss_state", choices=["nominal", "degraded", "denied"])
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
    state = MissionStateMachine(config=config.mission).update(
        mission_confidence=args.mission_confidence,
        gnss_state=args.gnss_state,
        vio_healthy=not args.vio_unhealthy,
    )
    print(state.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
