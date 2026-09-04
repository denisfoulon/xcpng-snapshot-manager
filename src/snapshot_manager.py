#!/usr/bin/env python3
"""XCP-ng Snapshot Manager main application entry point."""

import argparse

from core.banner import display_banner
from core.config import ConfigLoader
from core.engine import Engine


def main() -> None:
    """Application entry point."""

    parser = argparse.ArgumentParser(description="XCP-ng Snapshot Manager")
    parser.add_argument(
        "--run-scheduled-snapshots",
        action="store_true",
        help="execute due snapshot request files and exit",
    )
    args = parser.parse_args()

    display_banner()

    print("Loading configuration............... ", end="")

    config = ConfigLoader().load()

    print("OK")

    engine = Engine(config)
    if args.run_scheduled_snapshots:
        engine.run_scheduled_snapshots()
    else:
        engine.run()


if __name__ == "__main__":
    main()
