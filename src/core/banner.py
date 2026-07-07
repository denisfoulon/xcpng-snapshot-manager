"""
Application banner.
"""

from core.version import APP_NAME, VERSION
from version import VERSION

def display_banner() -> None:
    """Display the application banner."""

    print()

    print("══════════════════════════════════════════════════════════════════════")
    print(f" {APP_NAME}")
    print()
    print(" Observe • Evaluate • Report • Remediate • Verify")
    print()
    print(f" Version : {VERSION}")
    print("══════════════════════════════════════════════════════════════════════")
