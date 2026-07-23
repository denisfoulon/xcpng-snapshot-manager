"""Storage Repository usage compliance check."""

from checks.base import Check
from core.models import CheckResult, CheckStatus, Inventory


class StorageRepositoryUsageCheck(Check):
    """Check the most heavily used Storage Repository."""

    NAME = "Storage Repository Usage"
    DESCRIPTION = "Checks SR usage."

    def __init__(self, policy=None) -> None:
        self.policy = policy

    def run(self, inventory: Inventory) -> CheckResult:
        if not inventory.storage_repositories:
            return CheckResult(
                self.NAME,
                CheckStatus.PASS,
                "INFO",
                "No Storage Repositories found.",
            )

        warning = getattr(self.policy, "warning_percent", 80.0)
        critical = getattr(self.policy, "critical_percent", 90.0)
        usages = [
            (
                repository.used_bytes / repository.total_bytes * 100,
                repository,
            )
            for repository in inventory.storage_repositories
            if repository.total_bytes > 0
        ]
        if not usages:
            return CheckResult(
                self.NAME,
                CheckStatus.SKIPPED,
                "INFO",
                "Storage Repository capacity data is unavailable.",
            )

        maximum, repository = max(usages, key=lambda value: value[0])
        if maximum >= critical:
            status = CheckStatus.CRITICAL
        elif maximum >= warning:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.PASS
        severity = "INFO" if status is CheckStatus.PASS else status.value
        message = (
            f"'{repository.name}' is using {maximum:.1f}% "
            f"({repository.used_bytes} / {repository.total_bytes} bytes; "
            f"warning: {warning:.0f}%, critical: {critical:.0f}%)."
        )
        return CheckResult(self.NAME, status, severity, message)
