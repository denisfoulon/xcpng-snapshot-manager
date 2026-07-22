"""Console presentation for an infrastructure inventory."""

from core.models import Inventory
from core.models import CheckResult
from rich.console import Console
from reports.serialization import snapshot_age_days, snapshot_created_at_iso


class ConsoleInventoryReport:
    """Render a compact inventory summary to the console."""

    def display(self, inventory: Inventory) -> None:
        """Print the collected inventory counts."""

        print("Infrastructure Summary\n")
        print(f"Pools............................... {len(inventory.pools)}")
        print(f"Hosts............................... {len(inventory.hosts)}")
        print(f"Storage repositories................ {len(inventory.storage_repositories)}")
        print(f"Virtual machines.................... {len(inventory.virtual_machines)}")
        print(f"Snapshots........................... {len(inventory.snapshots)}")

    def display_snapshots(self, inventory: Inventory) -> None:
        """Print snapshot ownership, age and storage details."""

        print("\nSnapshot Details\n")
        for snapshot in inventory.snapshots:
            age = snapshot_age_days(snapshot.created_at)
            age_text = f"{age:.1f} days" if age is not None else "unknown age"
            created_text = snapshot_created_at_iso(snapshot.created_at) or "unknown date"
            vm_name = snapshot.vm_name or "unknown VM"
            sr_name = snapshot.sr_name or "unknown SR"
            print(
                f"- VM: {vm_name} | Age: {age_text} | "
                f"Created: {created_text} | "
                f"Comment: {snapshot.description or 'none'} | "
                f"Snapshot: {snapshot.name or snapshot.uuid} | SR: {sr_name}"
            )


class ConsoleCheckReport:
    """Render compliance results to the console."""

    _styles = {
        "PASS": "green",
        "WARNING": "yellow",
        "CRITICAL": "red",
        "ERROR": "red",
        "SKIPPED": "dim",
    }

    def __init__(self) -> None:
        self.console = Console()

    def display(self, results: list[CheckResult]) -> None:
        """Print one line per compliance check."""

        for result in results:
            status = result.status.value
            style = self._styles.get(status, "white")
            self.console.print(
                f"[{style}][{status}][/{style}] "
                f"{result.name} - {result.message}"
            )
