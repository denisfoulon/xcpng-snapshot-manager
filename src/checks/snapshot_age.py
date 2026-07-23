"""Snapshot age compliance check."""

from datetime import datetime, timezone

from checks.base import Check
from core.models import CheckResult, CheckStatus, Inventory


class SnapshotAgeCheck(Check):
    """Check the age of the oldest snapshot."""

    NAME = "Snapshot Age"
    DESCRIPTION = "Checks snapshot age."

    def __init__(self, policy=None, now: datetime | None = None) -> None:
        self.policy = policy
        self.now = now

    def run(self, inventory: Inventory) -> CheckResult:
        if not inventory.snapshots:
            return CheckResult(self.NAME, CheckStatus.PASS, "INFO", "No snapshots found.")

        warning_days = getattr(self.policy, "warning_days", 7)
        critical_days = getattr(self.policy, "critical_days", 30)
        reference = self.now or datetime.now(timezone.utc)
        dated_snapshots = []
        for snapshot in inventory.snapshots:
            if not snapshot.created_at:
                continue
            try:
                if isinstance(snapshot.created_at, (int, float)):
                    timestamp = float(snapshot.created_at)
                    if timestamp > 100_000_000_000:
                        timestamp /= 1000
                    created_at = datetime.fromtimestamp(timestamp, timezone.utc)
                elif isinstance(snapshot.created_at, str):
                    created_at = datetime.fromisoformat(
                        snapshot.created_at.replace("Z", "+00:00")
                    )
                else:
                    continue
            except (TypeError, ValueError, OverflowError):
                continue
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            age_days = max(0.0, (reference - created_at).total_seconds() / 86400)
            dated_snapshots.append((age_days, snapshot))

        if not dated_snapshots:
            return CheckResult(
                self.NAME,
                CheckStatus.SKIPPED,
                "INFO",
                "Snapshot creation dates are unavailable.",
            )

        oldest_age, oldest_snapshot = max(dated_snapshots, key=lambda value: value[0])
        if oldest_age >= critical_days:
            status = CheckStatus.CRITICAL
        elif oldest_age >= warning_days:
            status = CheckStatus.WARNING
        else:
            status = CheckStatus.PASS
        severity = "INFO" if status is CheckStatus.PASS else status.value
        message = (
            f"Oldest snapshot '{oldest_snapshot.name}' is {oldest_age:.1f} days old "
            f"(warning: {warning_days}d, critical: {critical_days}d)."
        )
        return CheckResult(self.NAME, status, severity, message)
