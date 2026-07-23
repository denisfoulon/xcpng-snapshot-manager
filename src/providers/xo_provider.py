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
from core.exceptions import ApiError
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
            cleanup=True,
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

    def delete_snapshot(self, snapshot_uuid: str) -> None:
        """Delete one VM snapshot."""

        self._client.delete_snapshot(snapshot_uuid)

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

        storage_repositories = [
            self._to_storage_repository(item)
            for item in self._client.get_storage_repositories()
        ]
        storage_repositories_by_uuid = {
            repository.uuid: repository
            for repository in storage_repositories
        }
        snapshots = []
        for item in self._client.get_snapshots():
            snapshot_uuid = self._object_uuid(item)
            try:
                details = self._client.get_snapshot(snapshot_uuid)
                details = self._enrich_snapshot_storage(details)
            except ApiError:
                details = {}
            snapshots.append(
                self._to_snapshot(
                    {**item, **details},
                    virtual_machines_by_uuid,
                    storage_repositories_by_uuid,
                )
            )

        return Inventory(
            pools=pools,
            hosts=hosts,
            virtual_machines=virtual_machines,
            snapshots=snapshots,
            storage_repositories=storage_repositories,
        )

    def _enrich_snapshot_storage(self, details: dict) -> dict:
        """Resolve VBD/VDI references to expose the snapshot's SR and size."""

        references = details.get(
            "VBDs",
            details.get("$VBDs", details.get("vbds", details.get("$vbds", []))),
        )
        if not references:
            references = details.get(
                "VDIs",
                details.get("$VDIs", details.get("vdis", details.get("$vdis", []))),
            )
        if isinstance(references, (str, dict)):
            references = [references]

        for reference in references or []:
            try:
                child = (
                    reference
                    if isinstance(reference, dict) and len(reference) > 1
                    else self._client.get_resource(reference)
                )
                vdi_reference = child.get("VDI", child.get("vdi", child))
                vdi = (
                    vdi_reference
                    if isinstance(vdi_reference, dict) and len(vdi_reference) > 1
                    else self._client.get_resource(vdi_reference)
                )
                if vdi:
                    if "SR" in vdi:
                        details.setdefault("SR", vdi["SR"])
                    elif "sr" in vdi:
                        details.setdefault("sr", vdi["sr"])
                    for key in ("physical_utilisation", "virtual_size"):
                        if isinstance(vdi.get(key), (int, float)):
                            details.setdefault(key, vdi[key])
                            break
                    if details.get("SR") or details.get("sr"):
                        break
            except ApiError:
                continue
        return details

    @staticmethod
    def _object_uuid(item: dict) -> str:
        """Extract an object identifier from an XO REST collection entry."""

        value = item.get(
            "uuid",
            item.get("href", item.get("url", item.get("id", ""))),
        )
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
        storage_repositories_by_uuid: dict[str, StorageRepository] | None = None,
    ) -> Snapshot:
        vm_uuid = cls._reference_uuid(
            item.get("snapshot_of", item.get("$snapshot_of", ""))
        )
        virtual_machine = virtual_machines_by_uuid.get(vm_uuid)
        sr_uuid, sr_name = cls._storage_reference(
            item,
            storage_repositories_by_uuid or {},
        )

        return Snapshot(
            uuid=cls._object_uuid(item),
            name=item.get("name_label", ""),
            description=item.get("name_description", ""),
            vm_uuid=vm_uuid,
            vm_name=virtual_machine.name if virtual_machine else "",
            sr_uuid=sr_uuid,
            sr_name=sr_name,
            created_at=item.get("snapshot_time", ""),
            size_bytes=cls._snapshot_size(item),
        )

    @classmethod
    def _reference_uuid(cls, value) -> str:
        """Normalize an XO UUID, URL or reference object to a UUID."""

        if isinstance(value, dict):
            value = value.get(
                "uuid",
                value.get(
                    "href",
                    value.get(
                        "url",
                        value.get(
                            "id",
                            value.get("$ref", value.get("ref", "")),
                        ),
                    ),
                ),
            )
        if not isinstance(value, str):
            return ""
        return value.rstrip("/").split("/")[-1]

    @classmethod
    def _storage_reference(
        cls,
        item: dict,
        storage_repositories: dict[str, StorageRepository],
    ) -> tuple[str, str]:
        """Find an SR reference in the varying XO detail representations."""

        reference_keys = {
            "sr",
            "$sr",
            "sr_uuid",
            "storage",
            "storage_repository",
            "storage_repository_uuid",
        }
        pending = [item]
        while pending:
            current = pending.pop()
            if not isinstance(current, dict):
                continue
            for key, value in current.items():
                if key.lower() in reference_keys:
                    uuid = cls._reference_uuid(value)
                    repository = storage_repositories.get(uuid)
                    if repository:
                        return repository.uuid, repository.name
                    if uuid:
                        name = value.get("name_label", "") if isinstance(value, dict) else ""
                        return uuid, name
                if isinstance(value, (dict, list)):
                    pending.extend(value if isinstance(value, list) else [value])
        return "", ""

    @staticmethod
    def _snapshot_size(item: dict) -> int:
        """Extract a best-effort snapshot size from XO detail fields."""

        for key in ("size_bytes", "physical_utilisation", "virtual_size", "size"):
            value = item.get(key)
            if isinstance(value, (int, float)):
                return int(value)
        return 0

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
