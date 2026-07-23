"""Tests for safe remediation candidate selection."""

import unittest

from core.models import Inventory, Snapshot, VirtualMachine
from core.remediation import select_expired_snapshots


class RemediationSelectionTests(unittest.TestCase):
    """Verify age, orphan and blacklist safeguards."""

    def test_selects_only_old_snapshots_with_known_vm(self) -> None:
        inventory = Inventory(
            virtual_machines=[VirtualMachine(uuid="vm-1", name="db")],
            snapshots=[
                Snapshot(uuid="old", vm_uuid="vm-1", created_at="2025-01-01T00:00:00Z"),
                Snapshot(uuid="orphan", vm_uuid="missing", created_at="2025-01-01T00:00:00Z"),
            ],
        )

        candidates = select_expired_snapshots(inventory, min_age_days=30)

        self.assertEqual([snapshot.uuid for snapshot in candidates], ["old"])

    def test_blacklisted_vm_is_protected_until_max_age(self) -> None:
        inventory = Inventory(
            virtual_machines=[VirtualMachine(uuid="vm-1", name="db", tags=["retain"])],
            snapshots=[Snapshot(uuid="old", vm_uuid="vm-1", created_at="2025-01-01T00:00:00Z")],
        )

        candidates = select_expired_snapshots(
            inventory,
            min_age_days=30,
            blacklist_max_age_days=1000,
            blacklist_tags=["retain"],
        )

        self.assertEqual(candidates, [])

        candidates = select_expired_snapshots(
            inventory,
            min_age_days=30,
            blacklist_max_age_days=1,
            blacklist_tags=["retain"],
        )

        self.assertEqual([snapshot.uuid for snapshot in candidates], ["old"])


if __name__ == "__main__":
    unittest.main()
