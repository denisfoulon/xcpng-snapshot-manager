"""
Base class for all inventory providers.
"""

from abc import ABC, abstractmethod

from core.models import Inventory
from core.provider_models import (
    ProviderCapabilities,
    ProviderHealth,
    ProviderInfo,
)


class InventoryProvider(ABC):
    """Abstract inventory provider."""

    @property
    @abstractmethod
    def info(self) -> ProviderInfo:
        """Provider information."""

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Provider capabilities."""

    @property
    @abstractmethod
    def health(self) -> ProviderHealth:
        """Provider health."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the provider."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the provider."""

    @abstractmethod
    def collect(self) -> Inventory:
        """Collect the infrastructure inventory."""

    @abstractmethod
    def delete_snapshot(self, snapshot_uuid: str) -> None:
        """Delete one VM snapshot."""
