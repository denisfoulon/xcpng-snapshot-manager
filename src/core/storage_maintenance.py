"""State and locking helpers for scheduled Storage Repository maintenance."""

import json
from datetime import datetime, timezone
from pathlib import Path


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def load_state(path: str) -> dict:
    file_path = Path(path)
    if not file_path.exists():
        return {}
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(path: str, state: dict) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = file_path.with_suffix(file_path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(file_path)


def acquire_lock(state_path: str) -> Path | None:
    """Create an exclusive lock file; return None when another run is active."""
    lock = Path(state_path + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        with lock.open("x", encoding="utf-8") as stream:
            stream.write(f"pid={__import__('os').getpid()}\n")
        return lock
    except FileExistsError:
        return None


def parse_timestamp(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def in_cooldown(last_run, minimum_hours: int, reference: datetime | None = None) -> bool:
    timestamp = parse_timestamp(last_run)
    if timestamp is None:
        return False
    current = reference or now_utc()
    return (current - timestamp).total_seconds() < max(minimum_hours, 0) * 3600
