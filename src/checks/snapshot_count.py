"""
Snapshot count compliance check.
"""

from checks.base import Check
from core.models import CheckResult, CheckStatus, Inventory


class SnapshotCountCheck(Check):
    """Check snapshot count."""

    NAME = "Snapshot Count"

    DESCRIPTION = "Checks snapshot count."

    def run(self, inventory: Inventory) -> CheckResult:

        return CheckResult(
            name=self.NAME,
            status=CheckStatus.PASS,
            severity="INFO",
            message="Not implemented yet."
        )
