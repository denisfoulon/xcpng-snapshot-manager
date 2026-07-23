"""Snapshot count compliance check."""

from checks.base import Check
from core.models import CheckResult, CheckStatus, Inventory


class SnapshotCountCheck(Check):
    """Check the maximum number of snapshots attached to one VM."""

    NAME = "Snapshot Count"
    DESCRIPTION = "Checks snapshot count."

    def __init__(self, policy=None) -> None:
        self.policy = policy

    def run(self, inventory: Inventory) -> CheckResult:
        if not inventory.snapshots:
            return CheckResult(self.NAME, CheckStatus.PASS, "INFO", "No snapshots found.")

        warning = getattr(self.policy, "warning", 3)
        critical = getattr(self.policy, "critical", 5)
        counts = {}
        names = {}
        for snapshot in inventory.snapshots:
            key = snapshot.vm_uuid or f"snapshot:{snapshot.uuid}"
            counts[key] = counts.get(key, 0) + 1
            names[key] = snapshot.vm_name or "unknown VM"

        vm_key, maximum = max(counts.items(), key=lambda item: item[1])
        if maximum >= critical:
            status = CheckStatus.CRITICAL
        elif maximum >= warning:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.PASS
        severity = "INFO" if status is CheckStatus.PASS else status.value
        message = (
            f"'{names[vm_key]}' has {maximum} snapshots "
            f"(warning: {warning}, critical: {critical})."
        )
        return CheckResult(self.NAME, status, severity, message)
