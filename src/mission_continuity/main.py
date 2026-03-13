"""CLI entry point for mission continuity state evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

from common.config import resolve_app_config
from .state_machine import MissionStateMachine

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "sim" / "default.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate mission continuity state.")
    parser.add_argument("mission_confidence", type=float)
    parser.add_argument("gnss_state", choices=["nominal", "degraded", "denied"])
    parser.add_argument(
        "--effective-vio-state",
        choices=["good", "weak", "lost"],
        default="good",
        help="Effective VIO state after conflict resolution.",
    )
    parser.add_argument(
        "--vio-unhealthy",
        action="store_true",
        help="(Deprecated) Sets effective_vio_state=lost.",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to the simulation config file.",
    )
    parser.add_argument(
        "--config-override",
        help="Optional CLI override config applied after the base config.",
    )
    args = parser.parse_args()

    effective_vio_state = args.effective_vio_state
    if args.vio_unhealthy:
        effective_vio_state = "lost"

    config = resolve_app_config(
        base_path=args.config,
        cli_override_path=args.config_override,
    )
    decision = MissionStateMachine(config=config.mission).update(
        mission_confidence=args.mission_confidence,
        gnss_state=args.gnss_state,
        effective_vio_state=effective_vio_state,
    )
    print(decision.final_state.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
