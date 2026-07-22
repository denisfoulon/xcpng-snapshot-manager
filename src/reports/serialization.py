"""Serialization helpers shared by report writers."""

from dataclasses import asdict
from datetime import datetime, timezone

from core.models import CheckResult, Inventory


def build_report(inventory: Inventory, results: list[CheckResult]) -> dict:
    """Build a JSON-serializable report payload."""

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inventory": {
            "pools": [asdict(item) for item in inventory.pools],
            "hosts": [asdict(item) for item in inventory.hosts],
            "storage_repositories": [
                asdict(item) for item in inventory.storage_repositories
            ],
            "virtual_machines": [asdict(item) for item in inventory.virtual_machines],
            "snapshots": [asdict(item) for item in inventory.snapshots],
        },
        "checks": [
            {
                "name": result.name,
                "status": result.status.value,
                "severity": result.severity,
                "message": result.message,
            }
            for result in results
        ],
    }
