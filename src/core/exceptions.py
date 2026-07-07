"""
Project exceptions.
"""


class SnapshotManagerError(Exception):
    """Base exception for the project."""


class ConfigurationError(SnapshotManagerError):
    """Invalid configuration."""


class ProviderError(SnapshotManagerError):
    """Provider failure."""


class ConnectionError(ProviderError):
    """Unable to connect to the provider."""


class AuthenticationError(ProviderError):
    """Authentication failed."""


class ApiError(ProviderError):
    """Unexpected API error."""
