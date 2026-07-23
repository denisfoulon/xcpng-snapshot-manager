"""
Provider models.
"""
"""
Provider models.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderCapabilities:
    """Capabilities supported by an inventory provider."""

    pools: bool = False
    hosts: bool = False
    virtual_machines: bool = False
    snapshots: bool = False
    storage_repositories: bool = False
    cleanup: bool = False
    estimated_reclaim: bool = False
    storage_scan: bool = False


@dataclass(frozen=True)
class ProviderInfo:
    """General information about a provider."""

    name: str
    platform: str
    version: str = "Unknown"
    api_version: str = "Unknown"


@dataclass(frozen=True)
class ProviderHealth:
    """Current provider health."""

    connected: bool = False
    authenticated: bool = False
    latency_ms: float | None = None
    last_error: str | None = None
