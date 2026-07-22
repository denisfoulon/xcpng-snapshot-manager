"""
Core execution engine.
"""

from core.discovery import CheckDiscovery
from core.models import Inventory
from providers.xo_provider import XOProvider
from reports.console import ConsoleInventoryReport

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
        for result in results:
            print(
                f"[{result.status.value}]"
                f"{result.name} - "
                f"{result.message}"
            )

    def remediate(self):
        print("Nothing to do.")

    def verify(self):
        print("Nothing to verify.")
