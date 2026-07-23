"""Tests for Xen Orchestra inventory normalization."""

import unittest

from providers.xo_provider import XOProvider


class XOProviderMapperTests(unittest.TestCase):
    """Validate conversion from REST collection entries to core models."""

    def test_pool_and_host_are_normalized(self) -> None:
        pool = XOProvider._to_pool(
            {"href": "/rest/v0/pools/pool-1", "name_label": "Lab"}
        )
        host = XOProvider._to_host(
            {
                "id": "host-1",
                "name_label": "xcp-ng-01",
                "address": "192.0.2.10",
                "enabled": True,
            }
        )

        self.assertEqual(pool.uuid, "pool-1")
        self.assertEqual(host.name, "xcp-ng-01")
        self.assertTrue(host.enabled)

    def test_virtual_machine_uses_href_as_uuid(self) -> None:
        virtual_machine = XOProvider._to_virtual_machine(
            {
                "href": "/rest/v0/vms/vm-1",
                "name_label": "Database",
                "power_state": "Running",
                "tags": ["production"],
            }
        )

        self.assertEqual(virtual_machine.uuid, "vm-1")
        self.assertEqual(virtual_machine.name, "Database")
        self.assertEqual(virtual_machine.tags, ["production"])

    def test_snapshot_is_linked_to_its_virtual_machine(self) -> None:
        virtual_machine = XOProvider._to_virtual_machine(
            {"id": "vm-1", "name_label": "Database"}
        )

        snapshot = XOProvider._to_snapshot(
            {
                "url": "/rest/v0/vm-snapshots/snapshot-1",
                "name_label": "Before upgrade",
                "name_description": "Maintenance window",
                "$snapshot_of": "/rest/v0/vms/vm-1",
                "snapshot_time": "2026-07-10T10:00:00Z",
                "SR": "/rest/v0/srs/sr-1",
            },
            {virtual_machine.uuid: virtual_machine},
            {"sr-1": XOProvider._to_storage_repository(
                {"id": "sr-1", "name_label": "Local storage"}
            )},
        )

        self.assertEqual(snapshot.uuid, "snapshot-1")
        self.assertEqual(snapshot.vm_name, "Database")
        self.assertEqual(snapshot.sr_name, "Local storage")
        self.assertEqual(snapshot.created_at, "2026-07-10T10:00:00Z")

    def test_storage_repository_calculates_free_capacity(self) -> None:
        storage_repository = XOProvider._to_storage_repository(
            {
                "id": "sr-1",
                "name_label": "Fast storage",
                "physical_size": 1_000,
                "physical_utilisation": 250,
            }
        )

        self.assertEqual(storage_repository.free_bytes, 750)


if __name__ == "__main__":
    unittest.main()
