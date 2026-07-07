"""
Xen Orchestra inventory provider.
"""

from clients.xo_client import XOClient
from core.models import Inventory
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

        return Inventory()
