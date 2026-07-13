"""
Snapshot count compliance check.

Checks if VMs have more snapshots than the configured maximum.
"""

from collections import defaultdict

from checks.base import Check
from core.models import (
    CheckItem,
    CheckResult,
    CheckStatus,
    Inventory,
    Severity,
)
from core.config_models import SnapshotCountPolicy


class SnapshotCountCheck(Check):
    """Check snapshot count per VM against policy."""

    NAME = "Snapshot Count"
    DESCRIPTION = "Checks if VMs exceed the configured maximum snapshot count"

    def __init__(self, policy: SnapshotCountPolicy = None) -> None:
        self.policy = policy or SnapshotCountPolicy()
        self._severity_map = {
            "INFO": Severity.INFO,
            "LOW": Severity.LOW,
            "MEDIUM": Severity.MEDIUM,
            "HIGH": Severity.HIGH,
            "CRITICAL": Severity.CRITICAL,
        }

    def run(self, inventory: Inventory) -> CheckResult:
        """
        Check all VMs for snapshot count compliance.
        
        Args:
            inventory: Infrastructure inventory containing snapshots and VMs.
            
        Returns:
            CheckResult with details of VMs with too many snapshots.
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
        
        max_snapshots = self.policy.max_snapshots_per_vm
        warning_count = self.policy.warning_count
        
        # Group snapshots by VM
        snapshots_by_vm: dict[str, list] = defaultdict(list)
        for snapshot in inventory.snapshots:
            snapshots_by_vm[snapshot.vm_uuid].append(snapshot)
        
        # Find VM details
        vm_map = {vm.uuid: vm for vm in inventory.virtual_machines}
        
        critical_vms = []
        warning_vms = []
        passed_vms = []
        
        for vm_uuid, snapshots in snapshots_by_vm.items():
            count = len(snapshots)
            vm_name = vm_map.get(vm_uuid, {}).name or f"Unknown VM ({vm_uuid[:8]})"
            
            if count > max_snapshots:
                critical_vms.append((vm_uuid, vm_name, count, snapshots))
            elif count > warning_count:
                warning_vms.append((vm_uuid, vm_name, count, snapshots))
            else:
                passed_vms.append((vm_uuid, vm_name, count))

        # Determine overall status
        if critical_vms:
            status = CheckStatus.CRITICAL
            message = f"Found {len(critical_vms)} VMs exceeding {max_snapshots} snapshots"
        elif warning_vms:
            status = CheckStatus.WARNING
            message = f"Found {len(warning_vms)} VMs approaching {max_snapshots} snapshots"
        else:
            status = CheckStatus.PASS
            message = f"All {len(passed_vms)} VMs are within snapshot count limits"

        # Build affected items list
        affected_items = []
        for vm_uuid, vm_name, count, snapshots in critical_vms:
            affected_items.append(CheckItem(
                identifier=vm_uuid,
                name=vm_name,
                details={
                    "snapshot_count": count,
                    "max_allowed": max_snapshots,
                    "excess": count - max_snapshots,
                    "snapshots": [
                        {"uuid": s.uuid, "name": s.name, "created_at": s.created_at}
                        for s in snapshots
                    ],
                }
            ))

        for vm_uuid, vm_name, count, snapshots in warning_vms:
            affected_items.append(CheckItem(
                identifier=vm_uuid,
                name=vm_name,
                details={
                    "snapshot_count": count,
                    "warning_threshold": warning_count,
                    "max_allowed": max_snapshots,
                    "snapshots": [
                        {"uuid": s.uuid, "name": s.name, "created_at": s.created_at}
                        for s in snapshots
                    ],
                    "status": "warning",
                }
            ))

        return CheckResult(
            name=self.NAME,
            description=self.DESCRIPTION,
            status=status,
            severity=severity,
            message=message,
            passed_items=len(passed_vms),
            failed_items=len(critical_vms) + len(warning_vms),
            affected_items=affected_items,
            remediation_hint=(
                f"Delete excess snapshots on VMs with more than {max_snapshots} snapshots. "
                f"Consider consolidating or archiving old snapshots."
            ),
        )
