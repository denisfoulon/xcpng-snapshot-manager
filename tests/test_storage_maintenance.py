import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.storage_maintenance import acquire_lock, in_cooldown, load_state, save_state


class StorageMaintenanceTests(unittest.TestCase):
    def test_state_round_trip_and_exclusive_lock(self):
        path = Path("state/test_sr_maintenance.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = Path(str(path) + ".lock")
        for candidate in (path, lock_path):
            if candidate.exists():
                candidate.unlink()
        try:
            state = {"sr-1": {"status": "success"}}
            save_state(str(path), state)
            self.assertEqual(load_state(str(path)), state)
            lock = acquire_lock(str(path))
            self.assertIsNotNone(lock)
            self.assertIsNone(acquire_lock(str(path)))
        finally:
            for candidate in (path, lock_path):
                if candidate.exists():
                    candidate.unlink()

    def test_cooldown(self):
        recent = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        old = (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat()
        self.assertTrue(in_cooldown(recent, 20))
        self.assertFalse(in_cooldown(old, 20))


if __name__ == "__main__":
    unittest.main()
