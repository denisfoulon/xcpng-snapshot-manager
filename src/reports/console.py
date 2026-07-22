"""Console presentation for an infrastructure inventory."""

from core.models import Inventory


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
