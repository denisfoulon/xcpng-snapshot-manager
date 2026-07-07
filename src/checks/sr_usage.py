"""
Storage Repository usage compliance check.
"""

from checks.base import Check
from core.models import CheckResult, CheckStatus, Inventory


class StorageRepositoryUsageCheck(Check):
    """Check Storage Repository usage."""

    NAME = "Storage Repository Usage"

    DESCRIPTION = "Checks SR usage."

    def run(self, inventory: Inventory) -> CheckResult:

        return CheckResult(
            name=self.NAME,
            status=CheckStatus.PASS,
            severity="INFO",
            message="Not implemented yet."
        )
