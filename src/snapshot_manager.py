#!/usr/bin/env python3
"""XCP-ng Snapshot Manager main application entry point."""

import argparse
import sys

from core.banner import display_banner
from core.version import VERSION


def main() -> int:
    """Application entry point."""

    parser = argparse.ArgumentParser(description="XCP-ng Snapshot Manager")
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="path to the YAML configuration file (default: %(default)s)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.add_argument(
        "--run-scheduled-snapshots",
        action="store_true",
        help="execute due snapshot request files and exit",
    )
    args = parser.parse_args()

    # Delay optional runtime dependencies so --help/--version remain available.
    from core.config import ConfigLoader
    from core.engine import Engine

    display_banner()

    print("Loading configuration............... ", end="")

    try:
        config = ConfigLoader(args.config).load()
    except (FileNotFoundError, ValueError, TypeError, KeyError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    print("OK")

    engine = Engine(config)
    if args.run_scheduled_snapshots:
        engine.run_scheduled_snapshots()
    else:
        engine.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
