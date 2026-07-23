"""
Core execution engine.
"""

from core.discovery import CheckDiscovery
from core.models import Inventory
from core.remediation import select_expired_snapshots
from providers.xo_provider import XOProvider
from reports.console import ConsoleCheckReport, ConsoleInventoryReport
from reports.html_report import HtmlReport
from reports.json_report import JsonReport
from reports.serialization import build_report
from reports.serialization import snapshot_age_days

class Engine:
    """Main execution engine."""

    def __init__(self, config) -> None:
        self.config = config
        self.inventory = Inventory()
        self.discovery = CheckDiscovery(config.compliance)
        self.provider = None
        self._remediation_target_ids: list[str] = []
        self._remediation_errors: list[str] = []

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
        self.provider = self._create_provider()
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
            inventory_report = ConsoleInventoryReport()
            inventory_report.display(self.inventory)
            inventory_report.display_snapshots(self.inventory)

    def _create_provider(self) -> XOProvider:
        """Create the configured inventory provider."""

        return XOProvider(
            url=self.config.xo.url,
            username=self.config.xo.username,
            password=self.config.xo.password,
            verify_ssl=self.config.xo.verify_ssl,
        )

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
        policy = self.config.remediation
        mode = policy.mode.strip().lower().replace("-", "_")
        candidates = select_expired_snapshots(
            self.inventory,
            min_age_days=policy.min_age_days,
            blacklist_max_age_days=policy.blacklist_max_age_days,
            blacklist_tags=policy.blacklist_tags,
            include_orphans=policy.include_orphans,
        )
        self._remediation_target_ids = []
        self._remediation_errors = []

        print(f"Remediation mode.................... {mode}")
        print(f"Eligible snapshots.................. {len(candidates)}")
        for snapshot in candidates:
            age = snapshot_age_days(snapshot.created_at)
            age_text = f"{age:.1f}d" if age is not None else "unknown age"
            print(
                f"- {snapshot.name or snapshot.uuid} | "
                f"VM: {snapshot.vm_name or 'unknown VM'} | {age_text}"
            )

        if not candidates:
            print("Nothing to remediate.")
            return
        if mode == "audit":
            print("Audit only: no snapshots were modified.")
            return
        if mode == "dry_run":
            print("Dry run: no snapshots were modified.")
            return
        if mode != "execute":
            print(f"Unknown remediation mode '{policy.mode}'. No action taken.")
            return
        if not policy.confirm:
            print("Execution blocked: set remediation.confirm=true to authorize deletion.")
            return

        provider = self._create_provider()
        print("Connecting for remediation............ ", end="")
        provider.connect()
        print("OK")
        try:
            for snapshot in candidates:
                try:
                    provider.delete_snapshot(snapshot.uuid)
                    self._remediation_target_ids.append(snapshot.uuid)
                    print(f"Deleted.............................. {snapshot.name or snapshot.uuid}")
                except Exception as exc:
                    self._remediation_errors.append(snapshot.uuid)
                    print(f"Delete failed......................... {snapshot.name or snapshot.uuid}: {exc}")
            if self._remediation_target_ids:
                self.inventory = provider.collect()
        finally:
            print("Disconnecting after remediation..... ", end="")
            provider.disconnect()
            print("OK")

    def verify(self):
        if not self._remediation_target_ids:
            print("Nothing to verify.")
            return
        remaining = {
            snapshot.uuid
            for snapshot in self.inventory.snapshots
        }.intersection(self._remediation_target_ids)
        if remaining:
            print(
                f"[ERROR] Remediation verification failed: "
                f"{len(remaining)} snapshot(s) still present."
            )
        else:
            print(
                f"Verified........................... "
                f"{len(self._remediation_target_ids)} snapshot(s) removed."
            )
