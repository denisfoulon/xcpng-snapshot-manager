"""
Core data models.

These dataclasses represent the internal objects manipulated by the
Snapshot Manager engine, independently from the underlying API.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


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
# Severity levels
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    """Severity levels for check results."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Risk score weights
# ---------------------------------------------------------------------------

RISK_SCORE_WEIGHTS = {
    CheckStatus.PASS: 0,
    CheckStatus.WARNING: 5,
    CheckStatus.CRITICAL: 10,
    CheckStatus.ERROR: 10,
    CheckStatus.SKIPPED: 0,
}

SEVERITY_WEIGHTS = {
    Severity.INFO: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 3,
    Severity.HIGH: 7,
    Severity.CRITICAL: 10,
}


# ---------------------------------------------------------------------------
# Infrastructure objects
# ---------------------------------------------------------------------------

@dataclass
class Pool:
    """Represents an XCP-ng pool."""

    uuid: str = ""
    name: str = ""


@dataclass
class Host:
    """Represents an XCP-ng host."""

    uuid: str = ""
    name: str = ""
    address: str = ""
    enabled: bool = False


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

    @property
    def usage_percent(self) -> float:
        """Calculate usage percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.used_bytes / self.total_bytes) * 100


@dataclass
class Inventory:
    """Infrastructure inventory."""

    pools: List[Pool] = field(default_factory=list)
    hosts: List[Host] = field(default_factory=list)
    snapshots: List[Snapshot] = field(default_factory=list)
    virtual_machines: List[VirtualMachine] = field(default_factory=list)
    storage_repositories: List[StorageRepository] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Check engine
# ---------------------------------------------------------------------------

@dataclass
class CheckItem:
    """A single item affected by a check."""

    identifier: str
    name: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class CheckResult:
    """Result returned by a compliance check."""

    name: str
    description: str = ""
    status: CheckStatus = CheckStatus.PASS
    severity: Severity = Severity.INFO
    message: str = ""
    passed_items: int = 0
    failed_items: int = 0
    affected_items: List[CheckItem] = field(default_factory=list)
    remediation_hint: str = ""
    risk_score: int = 0

    def __post_init__(self):
        """Calculate risk score based on status and severity."""
        status_weight = RISK_SCORE_WEIGHTS.get(self.status, 0)
        severity_weight = SEVERITY_WEIGHTS.get(self.severity, 0)
        
        # Base score from status
        self.risk_score = status_weight
        
        # Adjust based on severity
        if self.severity != Severity.INFO:
            self.risk_score = max(self.risk_score, severity_weight)
        
        # Multiply by number of affected items for aggregate checks
        if self.failed_items > 0:
            self.risk_score *= self.failed_items


@dataclass
class ComplianceReport:
    """Aggregate compliance report."""

    check_results: List[CheckResult] = field(default_factory=list)
    total_risk_score: int = 0
    total_checks: int = 0
    passed_checks: int = 0
    warning_checks: int = 0
    critical_checks: int = 0

    def __post_init__(self):
        """Calculate aggregate metrics."""
        self.total_checks = len(self.check_results)
        self.passed_checks = sum(
            1 for r in self.check_results if r.status == CheckStatus.PASS
        )
        self.warning_checks = sum(
            1 for r in self.check_results 
            if r.status == CheckStatus.WARNING
        )
        self.critical_checks = sum(
            1 for r in self.check_results 
            if r.status in [CheckStatus.CRITICAL, CheckStatus.ERROR]
        )
        self.total_risk_score = sum(r.risk_score for r in self.check_results)

    @property
    def overall_status(self) -> CheckStatus:
        """Determine overall compliance status."""
        if self.critical_checks > 0:
            return CheckStatus.CRITICAL
        if self.warning_checks > 0:
            return CheckStatus.WARNING
        return CheckStatus.PASS

    @property
    def risk_level(self) -> str:
        """Determine risk level based on total score."""
        if self.total_risk_score == 0:
            return "LOW"
        elif self.total_risk_score < 20:
            return "MEDIUM"
        elif self.total_risk_score < 50:
            return "HIGH"
        else:
            return "CRITICAL"
