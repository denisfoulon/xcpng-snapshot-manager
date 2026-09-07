"""Tests for Xen Orchestra REST resource resolution."""

import unittest
from unittest.mock import Mock

from clients.xo_client import XOClient


class TestXOClient(unittest.TestCase):
    def test_get_virtual_machine_resolves_a_uuid_as_a_vm_endpoint(self):
        client = XOClient("https://xoa.example.com", "user", "password")
        transport = Mock()
        client._client = transport
        transport.get.return_value = {"is_a_template": True}

        self.assertEqual(client.get_virtual_machine("parent-uuid"), {"is_a_template": True})
        self.assertEqual(transport.get.call_args.args[0], "/vms/parent-uuid")


    def test_get_virtual_machine_template_resolves_the_template_endpoint(self):
        client = XOClient("https://xoa.example.com", "user", "password")
        transport = Mock()
        client._client = transport
        transport.get.return_value = {"is_a_template": True}

        self.assertEqual(client.get_virtual_machine_template("parent-uuid"), {"is_a_template": True})
        self.assertEqual(transport.get.call_args.args[0], "/vm-templates/parent-uuid")

if __name__ == "__main__":
    unittest.main()
