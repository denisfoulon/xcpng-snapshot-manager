"""
Snapshot age compliance check.

Checks if snapshots exceed the configured maximum age.
"""

from datetime import datetime, timedelta

from checks.base import Check
from core.models import (
    CheckItem,
    CheckResult,
    CheckStatus,
    Inventory,
    Severity,
)
from core.config_models import SnapshotAgePolicy


class SnapshotAgeCheck(Check):
    """Check snapshot age against policy."""

    NAME = "Snapshot Age"
    DESCRIPTION = "Checks if snapshots exceed the configured maximum age"

    def __init__(self, policy: SnapshotAgePolicy = None) -> None:
        self.policy = policy or SnapshotAgePolicy()
        self._severity_map = {
            "INFO": Severity.INFO,
            "LOW": Severity.LOW,
            "MEDIUM": Severity.MEDIUM,
            "HIGH": Severity.HIGH,
            "CRITICAL": Severity.CRITICAL,
        }

    def run(self, inventory: Inventory) -> CheckResult:
        """
        Check all snapshots for age compliance.
        
        Args:
            inventory: Infrastructure inventory containing snapshots.
            
        Returns:
            CheckResult with details of non-compliant snapshots.
        """
        if not self.policy.enabled:
            return CheckResult(
                name=self.NAME,
                description=self.DESCRIPTION,
                status=CheckStatus.SKIPPED,
                severity=Severity.INFO,
                message="Check disabled by policy",
                risk_score=0,
            )

        severity = self._severity_map.get(
            self.policy.severity, Severity.MEDIUM
        )
        
        max_age_days = self.policy.max_age_days
        warning_days = self.policy.warning_days
        
        now = datetime.now()
        
        critical_snapshots = []
        warning_snapshots = []
        passed_snapshots = []
        
        for snapshot in inventory.snapshots:
            try:
                # Parse created_at timestamp
                created_at = datetime.fromisoformat(
                    snapshot.created_at.replace("Z", "+00:00")
                )
                
                age_days = (now - created_at).days
                
                if age_days > max_age_days:
                    # Critical: exceeds maximum age
                    critical_snapshots.append(snapshot)
                elif age_days > warning_days:
                    # Warning: approaching maximum age
                    warning_snapshots.append(snapshot)
                else:
                    # Pass: within acceptable range
                    passed_snapshots.append(snapshot)
                    
            except (ValueError, TypeError):
                # Unable to parse date, skip this snapshot
                continue

        # Determine overall status
        if critical_snapshots:
            status = CheckStatus.CRITICAL
            message = f"Found {len(critical_snapshots)} snapshots exceeding {max_age_days} days"
        elif warning_snapshots:
            status = CheckStatus.WARNING
            message = f"Found {len(warning_snapshots)} snapshots approaching {max_age_days} days"
        else:
            status = CheckStatus.PASS
            message = f"All {len(passed_snapshots)} snapshots are within age limits"

        # Build affected items list
        affected_items = []
        for snapshot in critical_snapshots:
            try:
                created_at = datetime.fromisoformat(
                    snapshot.created_at.replace("Z", "+00:00")
                )
                age_days = (now - created_at).days
                affected_items.append(CheckItem(
                    identifier=snapshot.uuid,
                    name=f"{snapshot.vm_name}/{snapshot.name}",
                    details={
                        "age_days": age_days,
                        "vm_uuid": snapshot.vm_uuid,
                        "vm_name": snapshot.vm_name,
                        "sr_name": snapshot.sr_name,
                        "created_at": snapshot.created_at,
                    }
                ))
            except (ValueError, TypeError):
                continue

        for snapshot in warning_snapshots:
            try:
                created_at = datetime.fromisoformat(
                    snapshot.created_at.replace("Z", "+00:00")
                )
                age_days = (now - created_at).days
                affected_items.append(CheckItem(
                    identifier=snapshot.uuid,
                    name=f"{snapshot.vm_name}/{snapshot.name}",
                    details={
                        "age_days": age_days,
                        "vm_uuid": snapshot.vm_uuid,
                        "vm_name": snapshot.vm_name,
                        "sr_name": snapshot.sr_name,
                        "created_at": snapshot.created_at,
                        "status": "warning",
                    }
                ))
            except (ValueError, TypeError):
                continue

        return CheckResult(
            name=self.NAME,
            description=self.DESCRIPTION,
            status=status,
            severity=severity,
            message=message,
            passed_items=len(passed_snapshots),
            failed_items=len(critical_snapshots) + len(warning_snapshots),
            affected_items=affected_items,
            remediation_hint=(
                f"Delete snapshots older than {max_age_days} days. "
                f"Consider setting up automated cleanup."
            ),
        )
