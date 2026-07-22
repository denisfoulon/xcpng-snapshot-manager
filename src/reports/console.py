"""Console presentation for an infrastructure inventory."""

from core.models import Inventory
from core.models import CheckResult
from rich.console import Console


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
