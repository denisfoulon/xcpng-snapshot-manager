"""
Application configuration loader.
"""

from pathlib import Path

import yaml

from core.config_models import (
    ApplicationConfig,
    CompliancePolicies,
    Config,
    LoggingConfig,
    ProviderConfig,
    ReportConfig,
    SnapshotAgePolicy,
    SnapshotCountPolicy,
    StorageRepositoryPolicy,
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

        # Load policies if present, otherwise use defaults
        policies_data = data.get("policies", {})
        policies = CompliancePolicies(
            snapshot_age=SnapshotAgePolicy(
                **policies_data.get("snapshot_age", {})
            ),
            snapshot_count=SnapshotCountPolicy(
                **policies_data.get("snapshot_count", {})
            ),
            storage_repository=StorageRepositoryPolicy(
                **policies_data.get("storage_repository", {})
            ),
        )

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
            policies=policies,
        )
