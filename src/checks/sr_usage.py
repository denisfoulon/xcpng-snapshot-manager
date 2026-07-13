"""
Storage Repository usage compliance check.

Checks if Storage Repositories exceed the configured usage threshold.
"""

from checks.base import Check
from core.models import (
    CheckItem,
    CheckResult,
    CheckStatus,
    Inventory,
    Severity,
)
from core.config_models import StorageRepositoryPolicy


class StorageRepositoryUsageCheck(Check):
    """Check Storage Repository usage against policy."""

    NAME = "Storage Repository Usage"
    DESCRIPTION = "Checks if SRs exceed the configured maximum usage percentage"

    def __init__(self, policy: StorageRepositoryPolicy = None) -> None:
        self.policy = policy or StorageRepositoryPolicy()
        self._severity_map = {
            "INFO": Severity.INFO,
            "LOW": Severity.LOW,
            "MEDIUM": Severity.MEDIUM,
            "HIGH": Severity.HIGH,
            "CRITICAL": Severity.CRITICAL,
        }

    def run(self, inventory: Inventory) -> CheckResult:
        """
        Check all Storage Repositories for usage compliance.
        
        Args:
            inventory: Infrastructure inventory containing SRs.
            
        Returns:
            CheckResult with details of SRs exceeding usage thresholds.
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
            self.policy.severity, Severity.CRITICAL
        )
        
        max_usage_percent = self.policy.max_usage_percent
        warning_percent = self.policy.warning_percent
        
        critical_srs = []
        warning_srs = []
        passed_srs = []
        
        for sr in inventory.storage_repositories:
            usage_percent = sr.usage_percent
            
            if usage_percent > max_usage_percent:
                critical_srs.append(sr)
            elif usage_percent > warning_percent:
                warning_srs.append(sr)
            else:
                passed_srs.append(sr)

        # Determine overall status
        if critical_srs:
            status = CheckStatus.CRITICAL
            message = f"Found {len(critical_srs)} SRs exceeding {max_usage_percent}% usage"
        elif warning_srs:
            status = CheckStatus.WARNING
            message = f"Found {len(warning_srs)} SRs approaching {max_usage_percent}% usage"
        else:
            status = CheckStatus.PASS
            message = f"All {len(passed_srs)} SRs are within usage limits"

        # Build affected items list
        affected_items = []
        for sr in critical_srs:
            affected_items.append(CheckItem(
                identifier=sr.uuid,
                name=sr.name,
                details={
                    "usage_percent": round(sr.usage_percent, 2),
                    "used_bytes": sr.used_bytes,
                    "total_bytes": sr.total_bytes,
                    "free_bytes": sr.free_bytes,
                    "max_allowed_percent": max_usage_percent,
                    "excess_percent": round(sr.usage_percent - max_usage_percent, 2),
                }
            ))

        for sr in warning_srs:
            affected_items.append(CheckItem(
                identifier=sr.uuid,
                name=sr.name,
                details={
                    "usage_percent": round(sr.usage_percent, 2),
                    "used_bytes": sr.used_bytes,
                    "total_bytes": sr.total_bytes,
                    "free_bytes": sr.free_bytes,
                    "warning_threshold_percent": warning_percent,
                    "max_allowed_percent": max_usage_percent,
                    "status": "warning",
                }
            ))

        return CheckResult(
            name=self.NAME,
            description=self.DESCRIPTION,
            status=status,
            severity=severity,
            message=message,
            passed_items=len(passed_srs),
            failed_items=len(critical_srs) + len(warning_srs),
            affected_items=affected_items,
            remediation_hint=(
                f"Free up space on SRs exceeding {max_usage_percent}% usage. "
                f"Consider deleting old snapshots, moving data, or adding storage."
            ),
        )
