import shutil
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from core.models import Inventory, VirtualMachine
from core.snapshot_scheduler import SnapshotScheduler


class FakeProvider:
    def __init__(self, failing=None):
        self.failing = failing
        self.created = []

    def create_snapshot(self, vm_uuid, name_label, timeout_seconds=1800):
        if vm_uuid == self.failing:
            raise RuntimeError("simulated failure")
        self.created.append((vm_uuid, name_label))


class SnapshotSchedulerTests(unittest.TestCase):
    root = Path("state/test_snapshot_scheduler")

    def setUp(self):
        shutil.rmtree(self.root, ignore_errors=True)
        (self.root / "requests").mkdir(parents=True)
        (self.root / "archives").mkdir(parents=True)
        self.inventory = Inventory(virtual_machines=[
            VirtualMachine(uuid="uuid-1", name="vm1"),
            VirtualMachine(uuid="uuid-2", name="vm2"),
        ])

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def config(self):
        return SimpleNamespace(
            enabled=True, mode="execute",
            input_directory=str(self.root / "requests"),
            archive_directory=str(self.root / "archives"),
            timezone="Europe/Paris", max_snapshot_lateness_minutes=60,
            snapshot_name_prefix="scheduled", task_timeout_minutes=1,
        )

    def test_success_moves_request_to_archive(self):
        request = self.root / "requests" / "job.txt"
        request.write_text("2026-08-05 14:40\nvm1\nvm2\n", encoding="utf-8")
        provider = FakeProvider()
        scheduler = SnapshotScheduler(self.config())
        result = scheduler.process(self.inventory, provider, datetime.fromisoformat("2026-08-05T14:41:00+02:00"))
        self.assertEqual(result["success"], 1)
        self.assertEqual(len(provider.created), 2)
        self.assertFalse(request.exists())
        self.assertEqual(len(list((self.root / "archives").glob("*.done.txt"))), 1)

    def test_partial_failure_marks_file_and_does_not_retry(self):
        request = self.root / "requests" / "job.txt"
        request.write_text("2026-08-05 14:40\nvm1\nvm2\n", encoding="utf-8")
        provider = FakeProvider(failing="uuid-2")
        scheduler = SnapshotScheduler(self.config())
        result = scheduler.process(self.inventory, provider, datetime.fromisoformat("2026-08-05T14:41:00+02:00"))
        self.assertEqual(result["failed"], 1)
        failed = list((self.root / "requests").glob("*.failed.txt"))
        self.assertEqual(len(failed), 1)
        self.assertIn("vm1: SUCCESS", failed[0].read_text(encoding="utf-8"))
        self.assertIn("vm2: FAILED", failed[0].read_text(encoding="utf-8"))
        self.assertEqual(scheduler.process(self.inventory, provider, datetime.fromisoformat("2026-08-05T14:42:00+02:00"))["processed"], 0)


if __name__ == "__main__":
    unittest.main()
