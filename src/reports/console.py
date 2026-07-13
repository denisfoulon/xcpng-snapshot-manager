"""
Console reporters for inventory and compliance results.
"""

from core.models import (
    ComplianceReport,
    CheckResult,
    CheckStatus,
    Inventory,
    Severity,
)


class ConsoleInventoryReport:
    """Display inventory in console."""

    def display(self, inventory: Inventory) -> None:
        """Display inventory summary."""
        print("\n" + "=" * 60)
        print("INVENTORY SUMMARY")
        print("=" * 60)
        
        print(f"\nPools: {len(inventory.pools)}")
        for pool in inventory.pools:
            print(f"  - {pool.name} ({pool.uuid[:8]})")
        
        print(f"\nHosts: {len(inventory.hosts)}")
        for host in inventory.hosts:
            status = "enabled" if host.enabled else "disabled"
            print(f"  - {host.name} ({host.address}) [{status}]")
        
        print(f"\nVirtual Machines: {len(inventory.virtual_machines)}")
        for vm in inventory.virtual_machines:
            print(f"  - {vm.name} ({vm.uuid[:8]}) [{vm.power_state}]")
        
        print(f"\nSnapshots: {len(inventory.snapshots)}")
        for snapshot in inventory.snapshots:
            print(f"  - {snapshot.vm_name}/{snapshot.name} ({snapshot.created_at})")
        
        print(f"\nStorage Repositories: {len(inventory.storage_repositories)}")
        for sr in inventory.storage_repositories:
            usage = f"{sr.usage_percent:.1f}%"
            print(f"  - {sr.name}: {sr.used_bytes / (1024**3):.2f} GB / {sr.total_bytes / (1024**3):.2f} GB ({usage})")
        
        print("=" * 60 + "\n")


class ConsoleReport:
    """Display compliance report in console."""

    def display(self, compliance_report: ComplianceReport) -> None:
        """Display compliance report."""
        print("\n" + "=" * 60)
        print("COMPLIANCE REPORT")
        print("=" * 60)
        
        # Header
        print(f"\nTotal Checks: {compliance_report.total_checks}")
        print(f"  Passed: {compliance_report.passed_checks}")
        print(f"  Warnings: {compliance_report.warning_checks}")
        print(f"  Critical: {compliance_report.critical_checks}")
        
        # Overall status
        status_icon = {
            CheckStatus.PASS: "[OK]",
            CheckStatus.WARNING: "[WARN]",
            CheckStatus.CRITICAL: "[CRIT]",
            CheckStatus.ERROR: "[ERR]",
        }
        
        overall_icon = status_icon.get(
            compliance_report.overall_status, "[???]"
        )
        print(f"\nOverall Status: {overall_icon} {compliance_report.overall_status.value}")
        print(f"Risk Score: {compliance_report.total_risk_score}")
        print(f"Risk Level: {compliance_report.risk_level}")
        
        # Individual check results
        print("\n" + "-" * 60)
        print("CHECK RESULTS")
        print("-" * 60)
        
        for result in compliance_report.check_results:
            self._display_check_result(result)
        
        print("=" * 60 + "\n")

    def _display_check_result(self, result: CheckResult) -> None:
        """Display a single check result."""
        severity_color = {
            Severity.INFO: "",
            Severity.LOW: "",
            Severity.MEDIUM: "",
            Severity.HIGH: "",
            Severity.CRITICAL: "",
        }
        
        status_icon = {
            CheckStatus.PASS: "[PASS]",
            CheckStatus.WARNING: "[WARN]",
            CheckStatus.CRITICAL: "[CRIT]",
            CheckStatus.ERROR: "[ERR]",
            CheckStatus.SKIPPED: "[SKIP]",
        }
        
        icon = status_icon.get(result.status, "[???]")
        
        print(f"\n{icon} {result.name}")
        print(f"   Severity: {result.severity.value}")
        print(f"   Status: {result.status.value}")
        print(f"   Risk Score: {result.risk_score}")
        print(f"   Message: {result.message}")
        
        if result.passed_items > 0:
            print(f"   Passed: {result.passed_items}")
        if result.failed_items > 0:
            print(f"   Failed: {result.failed_items}")
        
        if result.remediation_hint:
            print(f"   Remediation: {result.remediation_hint}")
        
        # Display affected items
        if result.affected_items:
            print(f"   Affected Items ({len(result.affected_items)}):")
            for item in result.affected_items[:5]:  # Limit to first 5
                print(f"     - {item.name} ({item.identifier[:8]})")
                if item.details:
                    for key, value in item.details.items():
                        if key not in ["snapshots"]:  # Skip verbose details
                            print(f"       {key}: {value}")
            
            if len(result.affected_items) > 5:
                print(f"     ... and {len(result.affected_items) - 5} more")
