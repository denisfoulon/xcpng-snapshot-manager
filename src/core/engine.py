"""
Core execution engine.
"""

from core.discovery import CheckDiscovery
from core.models import Inventory
from providers.xo_provider import XOProvider
from reports.console import ConsoleCheckReport, ConsoleInventoryReport
from reports.html_report import HtmlReport
from reports.json_report import JsonReport
from reports.serialization import build_report

class Engine:
    """Main execution engine."""

    def __init__(self, config) -> None:
        self.config = config
        self.inventory = Inventory()
        self.discovery = CheckDiscovery(config.compliance)
        self.provider = None

    def run(self):
        print("\nObserve\n")
        self.observe()

        print("\nEvaluate\n")
        results = self.evaluate()

        print("\nReport\n")
        self.report(results)

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

    def evaluate(self):
        checks = self.discovery.discover()

        results = []

        for check in checks:
            results.append(check.run(self.inventory))

        return results

    def report(self, results):
        payload = build_report(self.inventory, results)
        if self.config.report.console:
            ConsoleCheckReport().display(results)
        if self.config.report.json:
            path = JsonReport().write(payload, self.config.report.json_path)
            print(f"JSON report written to {path}")
        if self.config.report.html:
            path = HtmlReport().write(payload, self.config.report.html_path)
            print(f"HTML report written to {path}")

    def remediate(self):
        print("Nothing to do.")

    def verify(self):
        print("Nothing to verify.")
