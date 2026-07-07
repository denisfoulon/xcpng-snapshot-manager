#!/usr/bin/env python3
"""
XCP-ng Snapshot Manager

Main application entry point.
"""

from core.banner import display_banner
from core.config import ConfigLoader
from core.engine import Engine


def main() -> None:
    """Application entry point."""

    display_banner()

    print("Loading configuration............... ", end="")

    config = ConfigLoader().load()

    print("OK")

    engine = Engine(config)
    engine.run()


if __name__ == "__main__":
    main()
