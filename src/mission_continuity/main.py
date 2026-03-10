"""CLI entry point for mission continuity state evaluation."""

from __future__ import annotations

import argparse

from .state_machine import MissionStateMachine


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate mission continuity state.")
    parser.add_argument("mission_confidence", type=float)
    parser.add_argument("gnss_state", choices=["nominal", "degraded", "denied"])
    parser.add_argument(
        "--vio-unhealthy",
        action="store_true",
        help="Force the simplified VIO health input to false.",
    )
    args = parser.parse_args()

    state = MissionStateMachine().update(
        mission_confidence=args.mission_confidence,
        gnss_state=args.gnss_state,
        vio_healthy=not args.vio_unhealthy,
    )
    print(state.value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

