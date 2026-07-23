"""
Application configuration loader.
"""

from pathlib import Path

import yaml

from core.config_models import (
    ApplicationConfig,
    ComplianceConfig,
    Config,
    LoggingConfig,
    ProviderConfig,
    ReportConfig,
    RemediationConfig,
    SnapshotAgePolicy,
    SnapshotCountPolicy,
    StorageRepositoryUsagePolicy,
    StorageMaintenanceConfig,
    XOConfig,
)


class ConfigLoader:
    """Load application configuration."""

    def __init__(self, config_file: str = "config/config.yaml") -> None:

        self.config_file = Path(config_file)

    def load(self) -> Config:

        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}"
            )

        with open(self.config_file, "r", encoding="utf-8") as stream:

            data = yaml.safe_load(stream)

        return Config(
            application=ApplicationConfig(
                **data["application"]
            ),
            logging=LoggingConfig(
                **data["logging"]
            ),
            provider=ProviderConfig(
                **data["provider"]
            ),
            xo=XOConfig(
                **data["xo"]
            ),
            report=ReportConfig(
                **data["report"]
            ),
            compliance=ComplianceConfig(
                snapshot_age=SnapshotAgePolicy(
                    **data.get("compliance", {}).get("snapshot_age", {})
                ),
                snapshot_count=SnapshotCountPolicy(
                    **data.get("compliance", {}).get("snapshot_count", {})
                ),
                storage_repository_usage=StorageRepositoryUsagePolicy(
                    **data.get("compliance", {})
                    .get("storage_repository_usage", {})
                ),
            ),
            remediation=RemediationConfig(
                **data.get("remediation", {})
            ),
            maintenance=StorageMaintenanceConfig(
                **data.get("maintenance", {}).get("vacuum", {})
            ),
        )
