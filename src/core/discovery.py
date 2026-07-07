"""
Automatic discovery of compliance checks.
"""

import importlib
import inspect
import pkgutil

from checks.base import Check


class CheckDiscovery:
    """Discover and instantiate all available checks."""

    def __init__(self) -> None:
        self._checks: list[Check] = []

    def discover(self) -> list[Check]:
        """Discover all check classes inside the checks package."""

        self._checks.clear()

        import checks

        for _, module_name, is_package in pkgutil.iter_modules(checks.__path__):

            if is_package or module_name == "base":
                continue

            module = importlib.import_module(f"checks.{module_name}")

            for _, obj in inspect.getmembers(module, inspect.isclass):

                if (
                    issubclass(obj, Check)
                    and obj is not Check
                ):
                    self._checks.append(obj())

        return self._checks
