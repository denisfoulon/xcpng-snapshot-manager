"""
Xen Orchestra inventory provider.
"""

from clients.xo_client import XOClient
from core.models import (
    Host,
    Inventory,
    Pool,
    Snapshot,
    StorageRepository,
    VirtualMachine,
)
from core.provider_models import (
    ProviderCapabilities,
    ProviderHealth,
    ProviderInfo,
)
from providers.base import InventoryProvider


class XOProvider(InventoryProvider):
    """Xen Orchestra provider."""

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
    ) -> None:

        self._client = XOClient(
            url=url,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
        )

        self._info = ProviderInfo(
            name="Xen Orchestra",
            platform="XCP-ng",
        )

        self._capabilities = ProviderCapabilities(
            pools=True,
            hosts=True,
            virtual_machines=True,
            snapshots=True,
            storage_repositories=True,
            cleanup=False,
            estimated_reclaim=False,
        )

        self._health = ProviderHealth()

    @property
    def info(self) -> ProviderInfo:
        return self._info

    @property
    def capabilities(self) -> ProviderCapabilities:
        return self._capabilities

    @property
    def health(self) -> ProviderHealth:
        return self._health

    def connect(self) -> None:

        self._client.authenticate()
        self._health = ProviderHealth(
            connected=True,
            authenticated=True,
        )

    def disconnect(self) -> None:
        self._client.disconnect()
        self._health = ProviderHealth()

    def collect(self) -> Inventory:
        """Collect and normalize the Xen Orchestra inventory."""

        pools = [
            self._to_pool(item)
            for item in self._client.get_pools()
        ]
        hosts = [
            self._to_host(item)
            for item in self._client.get_hosts()
        ]
        virtual_machines = [
            self._to_virtual_machine(item)
            for item in self._client.get_virtual_machines()
        ]
        virtual_machines_by_uuid = {
            virtual_machine.uuid: virtual_machine
            for virtual_machine in virtual_machines
        }

        snapshots = [
            self._to_snapshot(item, virtual_machines_by_uuid)
            for item in self._client.get_snapshots()
        ]
        storage_repositories = [
            self._to_storage_repository(item)
            for item in self._client.get_storage_repositories()
        ]

        return Inventory(
            pools=pools,
            hosts=hosts,
            virtual_machines=virtual_machines,
            snapshots=snapshots,
            storage_repositories=storage_repositories,
        )

    @staticmethod
    def _object_uuid(item: dict) -> str:
        """Extract an object identifier from an XO REST collection entry."""

        value = item.get("id", item.get("href", item.get("url", "")))
        return value.rstrip("/").split("/")[-1]

    @classmethod
    def _to_virtual_machine(cls, item: dict) -> VirtualMachine:
        return VirtualMachine(
            uuid=cls._object_uuid(item),
            name=item.get("name_label", ""),
            power_state=item.get("power_state", ""),
            tags=item.get("tags", []),
        )

    @classmethod
    def _to_pool(cls, item: dict) -> Pool:
        return Pool(
            uuid=cls._object_uuid(item),
            name=item.get("name_label", ""),
        )

    @classmethod
    def _to_host(cls, item: dict) -> Host:
        return Host(
            uuid=cls._object_uuid(item),
            name=item.get("name_label", ""),
            address=item.get("address", ""),
            enabled=item.get("enabled", False),
        )

    @classmethod
    def _to_snapshot(
        cls,
        item: dict,
        virtual_machines_by_uuid: dict[str, VirtualMachine],
    ) -> Snapshot:
        vm_uuid = item.get("snapshot_of", "")
        virtual_machine = virtual_machines_by_uuid.get(vm_uuid)

        return Snapshot(
            uuid=cls._object_uuid(item),
            name=item.get("name_label", ""),
            description=item.get("name_description", ""),
            vm_uuid=vm_uuid,
            vm_name=virtual_machine.name if virtual_machine else "",
            created_at=item.get("snapshot_time", ""),
        )

    @classmethod
    def _to_storage_repository(cls, item: dict) -> StorageRepository:
        total_bytes = item.get("physical_size", 0)
        used_bytes = item.get("physical_utilisation", 0)

        return StorageRepository(
            uuid=cls._object_uuid(item),
            name=item.get("name_label", ""),
            total_bytes=total_bytes,
            used_bytes=used_bytes,
            free_bytes=max(total_bytes - used_bytes, 0),
        )
