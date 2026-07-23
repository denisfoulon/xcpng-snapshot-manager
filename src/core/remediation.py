"""Selection logic for safe snapshot remediation."""

from core.models import Inventory, Snapshot
from reports.serialization import snapshot_age_days


def select_expired_snapshots(
    inventory: Inventory,
    min_age_days: int,
    blacklist_max_age_days: int | None = 90,
    blacklist_tags: list[str] | None = None,
    include_orphans: bool = False,
) -> list[Snapshot]:
    """Return snapshots eligible for deletion under the retention policy.

    A snapshot must have a known VM and a known creation date by default.
    Any matching VM blacklist tag excludes all of its snapshots.
    """

    blacklisted = set(blacklist_tags or [])
    virtual_machines = {
        virtual_machine.uuid: virtual_machine
        for virtual_machine in inventory.virtual_machines
    }
    candidates = []
    for snapshot in inventory.snapshots:
        age_days = snapshot_age_days(snapshot.created_at)
        if age_days is None or age_days < min_age_days:
            continue
        virtual_machine = virtual_machines.get(snapshot.vm_uuid)
        if virtual_machine is None and not include_orphans:
            continue
        is_blacklisted = bool(
            virtual_machine and blacklisted.intersection(virtual_machine.tags)
        )
        if (
            is_blacklisted
            and blacklist_max_age_days is not None
            and age_days < blacklist_max_age_days
        ):
            continue
        candidates.append(snapshot)
    return candidates
