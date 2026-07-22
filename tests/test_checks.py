"""Tests for compliance checks."""

import unittest
from datetime import datetime, timezone

from checks.snapshot_age import SnapshotAgeCheck
from checks.snapshot_count import SnapshotCountCheck
from checks.sr_usage import StorageRepositoryUsageCheck
from core.config_models import (
    SnapshotAgePolicy,
    SnapshotCountPolicy,
    StorageRepositoryUsagePolicy,
)
from core.models import Inventory, Snapshot, StorageRepository


class ComplianceCheckTests(unittest.TestCase):
    """Verify warning and critical threshold behavior."""

    def test_snapshot_age_becomes_critical(self) -> None:
        inventory = Inventory(
            snapshots=[
                Snapshot(
                    name="old",
                    created_at="2026-06-01T00:00:00Z",
                )
            ]
        )
        result = SnapshotAgeCheck(
            SnapshotAgePolicy(warning_days=7, critical_days=30),
            now=datetime(2026, 7, 22, tzinfo=timezone.utc),
        ).run(inventory)

        self.assertEqual(result.status.value, "CRITICAL")

    def test_snapshot_age_accepts_unix_milliseconds(self) -> None:
        inventory = Inventory(
            snapshots=[Snapshot(name="old", created_at=1_751_320_800_000)]
        )
        result = SnapshotAgeCheck(
            SnapshotAgePolicy(warning_days=7, critical_days=30),
            now=datetime(2026, 7, 22, tzinfo=timezone.utc),
        ).run(inventory)

        self.assertEqual(result.status.value, "CRITICAL")

    def test_snapshot_count_is_evaluated_per_vm(self) -> None:
        inventory = Inventory(
            snapshots=[Snapshot(vm_uuid="vm-1", vm_name="db") for _ in range(4)]
        )
        result = SnapshotCountCheck(
            SnapshotCountPolicy(warning=3, critical=5)
        ).run(inventory)

        self.assertEqual(result.status.value, "WARNING")

    def test_storage_repository_usage_becomes_critical(self) -> None:
        inventory = Inventory(
            storage_repositories=[
                StorageRepository(
                    name="local",
                    total_bytes=100,
                    used_bytes=95,
                )
            ]
        )
        result = StorageRepositoryUsageCheck(
            StorageRepositoryUsagePolicy(warning_percent=80, critical_percent=90)
        ).run(inventory)

        self.assertEqual(result.status.value, "CRITICAL")


if __name__ == "__main__":
    unittest.main()
