"""Serialization helpers shared by report writers."""

from dataclasses import asdict
from datetime import datetime, timezone

from core.models import CheckResult, Inventory


def snapshot_age_days(created_at, now: datetime | None = None) -> float | None:
    """Return a snapshot age in days for ISO or Unix timestamps."""

    if not created_at:
        return None
    try:
        if isinstance(created_at, (int, float)):
            timestamp = float(created_at)
            if timestamp > 100_000_000_000:
                timestamp /= 1000
            created = datetime.fromtimestamp(timestamp, timezone.utc)
        elif isinstance(created_at, str):
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            return None
    except (TypeError, ValueError, OverflowError):
        return None
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    reference = now or datetime.now(timezone.utc)
    return round(max(0.0, (reference - created).total_seconds() / 86400), 1)


def snapshot_created_at_iso(created_at) -> str | None:
    """Normalize a snapshot timestamp to an ISO-8601 UTC string."""

    if not created_at:
        return None
    try:
        if isinstance(created_at, (int, float)):
            timestamp = float(created_at)
            if timestamp > 100_000_000_000:
                timestamp /= 1000
            created = datetime.fromtimestamp(timestamp, timezone.utc)
        elif isinstance(created_at, str):
            created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            return None
    except (TypeError, ValueError, OverflowError):
        return None
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return created.astimezone(timezone.utc).isoformat()


def build_report(inventory: Inventory, results: list[CheckResult]) -> dict:
    """Build a JSON-serializable report payload."""

    generated_at = datetime.now(timezone.utc)
    snapshots = []
    for snapshot in inventory.snapshots:
        snapshot_data = asdict(snapshot)
        snapshot_data["age_days"] = snapshot_age_days(
            snapshot.created_at,
            generated_at,
        )
        snapshot_data["created_at_iso"] = snapshot_created_at_iso(snapshot.created_at)
        snapshots.append(snapshot_data)

    return {
        "generated_at": generated_at.isoformat(),
        "inventory": {
            "pools": [asdict(item) for item in inventory.pools],
            "hosts": [asdict(item) for item in inventory.hosts],
            "storage_repositories": [
                asdict(item) for item in inventory.storage_repositories
            ],
            "virtual_machines": [asdict(item) for item in inventory.virtual_machines],
            "snapshots": snapshots,
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
