"""
Automatic discovery of compliance checks.
"""

import importlib
import inspect
import pkgutil

from checks.base import Check


class CheckDiscovery:
    """Discover and instantiate all available checks."""

    def __init__(self, config=None) -> None:
        self._checks: list[Check] = []
        self.config = config

    def discover(self) -> list[Check]:
        """Discover all check classes inside the checks package."""

        self._checks.clear()
        policy_names = {
            "snapshot_age": "snapshot_age",
            "snapshot_count": "snapshot_count",
            "sr_usage": "storage_repository_usage",
        }

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
                    constructor = inspect.signature(obj.__init__)
                    if "policy" in constructor.parameters:
                        policy_name = policy_names.get(module_name, module_name)
                        policy = getattr(self.config, policy_name, None)
                        self._checks.append(obj(policy=policy))
                    else:
                        self._checks.append(obj())

        return self._checks
