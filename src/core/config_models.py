from dataclasses import dataclass, field


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


@dataclass
class SnapshotAgePolicy:
    """Thresholds for snapshot age in days."""

    warning_days: int = 7
    critical_days: int = 30


@dataclass
class SnapshotCountPolicy:
    """Maximum snapshot thresholds per virtual machine."""

    warning: int = 3
    critical: int = 5


@dataclass
class StorageRepositoryUsagePolicy:
    """Storage Repository usage thresholds in percent."""

    warning_percent: float = 80.0
    critical_percent: float = 90.0


@dataclass
class ComplianceConfig:
    """Configuration for compliance checks."""

    snapshot_age: SnapshotAgePolicy = field(default_factory=SnapshotAgePolicy)
    snapshot_count: SnapshotCountPolicy = field(default_factory=SnapshotCountPolicy)
    storage_repository_usage: StorageRepositoryUsagePolicy = field(
        default_factory=StorageRepositoryUsagePolicy
    )


@dataclass
class Config:
    application: ApplicationConfig
    logging: LoggingConfig
    provider: ProviderConfig
    xo: XOConfig
    report: ReportConfig
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
