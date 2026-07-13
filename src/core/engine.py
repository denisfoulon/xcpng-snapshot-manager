"""
Core execution engine.
"""

from core.discovery import CheckDiscovery
from core.models import ComplianceReport, Inventory
from providers.xo_provider import XOProvider
from reports.console import ConsoleInventoryReport, ConsoleReport


class Engine:
    """Main execution engine."""

    def __init__(self, config) -> None:
        self.config = config
        self.inventory = Inventory()
        self.discovery = CheckDiscovery()
        self.provider = None
        self.compliance_report = None

    def run(self):
        print("\nObserve\n")
        self.observe()

        print("\nEvaluate\n")
        self.compliance_report = self.evaluate()

        print("\nReport\n")
        self.report(self.compliance_report)

        print("\nRemediation\n")
        self.remediate()

        print("\nVerify\n")
        self.verify()

    def observe(self):
        print("Loading provider.................... ", end="")
        self.provider = XOProvider(
            url=self.config.xo.url,
            username=self.config.xo.username,
            password=self.config.xo.password,
            verify_ssl=self.config.xo.verify_ssl,
        )

        print("OK")
        print("Connecting.......................... ", end="")
        self.provider.connect()
        print("OK")

        try:
            print("Collecting inventory................ ", end="")
            self.inventory = self.provider.collect()
            print("OK")
        finally:
            print("Disconnecting....................... ", end="")
            self.provider.disconnect()
            print("OK")

        if self.config.report.console:
            ConsoleInventoryReport().display(self.inventory)

    def evaluate(self) -> ComplianceReport:
        """
        Run all compliance checks against the inventory.
        
        Returns:
            ComplianceReport with all check results.
        """
        checks = self.discovery.discover()

        # Inject policies into checks that support them
        policies = self.config.policies
        for check in checks:
            check_class_name = check.__class__.__name__
            
            # Map check classes to their respective policies
            if check_class_name == "SnapshotAgeCheck" and policies:
                check.policy = policies.snapshot_age
            elif check_class_name == "SnapshotCountCheck" and policies:
                check.policy = policies.snapshot_count
            elif check_class_name == "StorageRepositoryUsageCheck" and policies:
                check.policy = policies.storage_repository

        results = []
        for check in checks:
            results.append(check.run(self.inventory))

        return ComplianceReport(check_results=results)

    def report(self, compliance_report: ComplianceReport):
        """Display compliance report."""
        if self.config.report.console:
            ConsoleReport().display(compliance_report)
        else:
            # Fallback simple report
            for result in compliance_report.check_results:
                print(
                    f"[{result.status.value}]"
                    f" {result.name} - "
                    f"{result.message}"
                )
            
            print(f"\nOverall: {compliance_report.overall_status.value}")
            print(f"Risk Score: {compliance_report.total_risk_score}")
            print(f"Risk Level: {compliance_report.risk_level}")

    def remediate(self):
        print("Nothing to do.")

    def verify(self):
        print("Nothing to verify.")
