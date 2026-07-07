"""
Snapshot age compliance check.
"""

from checks.base import Check
from core.models import CheckResult, CheckStatus, Inventory


class SnapshotAgeCheck(Check):
    """Check snapshot age."""

    NAME = "Snapshot Age"

    DESCRIPTION = "Checks snapshot age."

    def run(self, inventory: Inventory) -> CheckResult:

        return CheckResult(
            name=self.NAME,
            status=CheckStatus.PASS,
            severity="INFO",
            message="Not implemented yet."
        )
