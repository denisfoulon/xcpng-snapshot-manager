from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ApplicationConfig:
    name: str


@dataclass
class LoggingConfig:
    level: str


@dataclass
class ProviderConfig:
    type: str


@dataclass
class XOConfig:
    url: str
    username: str
    password: str
    verify_ssl: bool = True


@dataclass
class ReportConfig:
    console: bool = True


# ---------------------------------------------------------------------------
# Compliance Policies
# ---------------------------------------------------------------------------

@dataclass
class SnapshotAgePolicy:
    """Policy for snapshot age compliance."""

    enabled: bool = True
    max_age_days: int = 30
    warning_days: int = 25
    severity: str = "HIGH"


@dataclass
class SnapshotCountPolicy:
    """Policy for snapshot count compliance."""

    enabled: bool = True
    max_snapshots_per_vm: int = 5
    warning_count: int = 4
    severity: str = "MEDIUM"


@dataclass
class StorageRepositoryPolicy:
    """Policy for Storage Repository usage compliance."""

    enabled: bool = True
    max_usage_percent: float = 80.0
    warning_percent: float = 70.0
    severity: str = "CRITICAL"


@dataclass
class CompliancePolicies:
    """All compliance policies."""

    snapshot_age: SnapshotAgePolicy = field(default_factory=SnapshotAgePolicy)
    snapshot_count: SnapshotCountPolicy = field(default_factory=SnapshotCountPolicy)
    storage_repository: StorageRepositoryPolicy = field(default_factory=StorageRepositoryPolicy)


@dataclass
class Config:
    application: ApplicationConfig
    logging: LoggingConfig
    provider: ProviderConfig
    xo: XOConfig
    report: ReportConfig
    policies: Optional[CompliancePolicies] = None
