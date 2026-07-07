"""
Base class for all compliance checks.
"""

from abc import ABC, abstractmethod

from core.models import CheckResult, Inventory


class Check(ABC):
    """Abstract base class for all checks."""

    NAME = "Generic Check"
    DESCRIPTION = "Base check"

    @abstractmethod
    def run(self, inventory: Inventory) -> CheckResult:
        """
        Execute the check.

        Args:
            inventory: Infrastructure inventory.

        Returns:
            CheckResult
        """
        pass
