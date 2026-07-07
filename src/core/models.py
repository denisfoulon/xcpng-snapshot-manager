"""
Core data models.

These dataclasses represent the internal objects manipulated by the
Snapshot Manager engine, independently from the underlying API.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ---------------------------------------------------------------------------
# Check status
# ---------------------------------------------------------------------------

class CheckStatus(str, Enum):
    """Supported check status."""

    PASS = "PASS"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


# ---------------------------------------------------------------------------
# Infrastructure objects
# ---------------------------------------------------------------------------

@dataclass
class Snapshot:
    """Represents a VM snapshot."""

    uuid: str = ""
    name: str = ""
    description: str = ""
    vm_uuid: str = ""
    vm_name: str = ""
    sr_uuid: str = ""
    sr_name: str = ""
    created_at: str = ""
    size_bytes: int = 0


@dataclass
class VirtualMachine:
    """Represents a virtual machine."""

    uuid: str = ""
    name: str = ""
    power_state: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class StorageRepository:
    """Represents a Storage Repository."""

    uuid: str = ""
    name: str = ""
    total_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0


@dataclass
class Inventory:
    """Infrastructure inventory."""

    snapshots: List[Snapshot] = field(default_factory=list)
    virtual_machines: List[VirtualMachine] = field(default_factory=list)
    storage_repositories: List[StorageRepository] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Check engine
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Result returned by a compliance check."""

    name: str
    status: CheckStatus
    severity: str
    message: str
