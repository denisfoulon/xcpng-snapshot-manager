"""Regression coverage for template snapshots resolved through their parent VM."""

import unittest
from unittest.mock import Mock

from core.exceptions import ApiError
from providers.xo_provider import XOProvider


class TestTemplateParentScope(unittest.TestCase):
    def _provider(self, parent, include_templates=False):
        provider = XOProvider(
            "https://xoa.example.com",
            "user",
            "password",
            include_templates=include_templates,
        )
        client = Mock()
        provider._client = client
        client.get_pools.return_value = []
        client.get_hosts.return_value = []
        client.get_virtual_machines.return_value = []
        client.get_storage_repositories.return_value = []
        client.get_snapshots.return_value = [
            {
                "id": "snapshot-1",
                "$snapshot_of": "parent-uuid",
                "snapshot_time": "2025-10-06T09:20:16Z",
                "name_label": "after partial import from V2V",
            }
        ]
        client.get_snapshot.return_value = {}
        if isinstance(parent, Exception):
            client.get_virtual_machine.side_effect = parent
        else:
            client.get_virtual_machine.return_value = parent
        return provider, client

    def test_normal_vm_parent_keeps_snapshot(self):
        provider, client = self._provider(
            {"name_label": "Database", "is_a_template": False}
        )

        inventory = provider.collect()

        self.assertEqual([snapshot.uuid for snapshot in inventory.snapshots], ["snapshot-1"])
        client.get_virtual_machine.assert_called_once_with("parent-uuid")

    def test_template_parent_excludes_v2v_snapshot_and_emits_debug_diagnostic(self):
        provider, _ = self._provider(
            {"name_label": "Template_RHEL9_Xen", "is_a_template": True}
        )

        with self.assertLogs("providers.xo_provider", level="DEBUG") as logs:
            inventory = provider.collect()

        self.assertEqual(inventory.snapshots, [])
        self.assertTrue(any("Template_RHEL9_Xen" in message for message in logs.output))

    def test_template_parent_is_included_when_explicitly_enabled(self):
        provider, _ = self._provider(
            {"name_label": "Template_RHEL9_Xen", "is_a_template": True},
            include_templates=True,
        )

        self.assertEqual(len(provider.collect().snapshots), 1)

    def test_unresolved_parent_preserves_orphan_snapshot(self):
        provider, _ = self._provider(ApiError("parent not found"))

        self.assertEqual(len(provider.collect().snapshots), 1)


    def test_template_parent_falls_back_to_template_collection(self):
        provider, client = self._provider(ApiError("VM endpoint not found"))
        client.get_virtual_machine_template.return_value = {
            "name_label": "Template_RHEL9_Xen", "is_a_template": True
        }

        self.assertEqual(provider.collect().snapshots, [])
        client.get_virtual_machine_template.assert_called_once_with("parent-uuid")

if __name__ == "__main__":
    unittest.main()
