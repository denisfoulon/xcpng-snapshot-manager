"""File-based scheduler for one-shot VM snapshot requests."""

from dataclasses import dataclass
from datetime import datetime, timezone
from fnmatch import fnmatchcase
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass
class SnapshotRequest:
    path: Path
    scheduled_at: datetime
    targets: list[str]
    original_text: str


def _timestamp_from_line(line: str, timezone_name: str) -> datetime:
    value = datetime.fromisoformat(line.strip().replace("Z", "+00:00"))
    if value.tzinfo is None:
        try:
            value = value.replace(tzinfo=ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone '{timezone_name}'.") from exc
    return value


def parse_request(path: Path, timezone_name: str) -> SnapshotRequest:
    text = path.read_text(encoding="utf-8")
    meaningful = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not meaningful:
        raise ValueError("request file is empty")
    scheduled_at = _timestamp_from_line(meaningful[0], timezone_name)
    targets = meaningful[1:]
    if not targets:
        raise ValueError("request contains no VM target")
    return SnapshotRequest(path, scheduled_at, targets, text.rstrip() + "\n")


def _result_path(source: Path, suffix: str) -> Path:
    return source.with_name(f"{source.stem}.{suffix}{source.suffix}")


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return path.with_name(f"{path.stem}-{stamp}{path.suffix}")


def _format_snapshot_name(prefix: str, scheduled_at: datetime, vm_name: str) -> str:
    safe_name = "-".join(vm_name.split()) or "vm"
    return f"{prefix}-{scheduled_at.strftime('%Y%m%d-%H%M')}-{safe_name}"


class SnapshotScheduler:
    """Discover and execute pending request files."""

    def __init__(self, config) -> None:
        self.config = config

    def process(self, inventory, provider, now: datetime | None = None) -> dict[str, int]:
        policy = self.config
        mode = policy.mode.strip().lower().replace("-", "_")
        if not policy.enabled:
            print("Disabled by configuration.")
            return {"processed": 0, "success": 0, "failed": 0, "skipped": 0}
        if mode not in {"audit", "dry_run", "execute"}:
            print(f"Unknown snapshot scheduling mode '{policy.mode}'. No action taken.")
            return {"processed": 0, "success": 0, "failed": 0, "skipped": 0}

        input_directory = Path(policy.input_directory)
        archive_directory = Path(policy.archive_directory)
        input_directory.mkdir(parents=True, exist_ok=True)
        files = sorted(
            path for path in input_directory.glob("*.txt")
            if not path.name.endswith(".failed.txt") and not path.name.endswith(".done.txt")
        )
        current = now or datetime.now(ZoneInfo(policy.timezone))
        if current.tzinfo is None:
            current = current.replace(tzinfo=ZoneInfo(policy.timezone))
        vms = list(inventory.virtual_machines)
        summary = {"processed": 0, "success": 0, "failed": 0, "skipped": 0}
        print(f"Request files........................ {len(files)}")
        for path in files:
            try:
                request = parse_request(path, policy.timezone)
            except (OSError, ValueError) as exc:
                print(f"Invalid request....................... {path.name}: {exc}")
                if mode == "execute":
                    try:
                        original = path.read_text(encoding="utf-8")
                    except OSError:
                        original = ""
                    self._mark_failed(path, original, [("FILE", "FAILED", str(exc))])
                    summary["failed"] += 1
                continue

            if request.scheduled_at > current:
                summary["skipped"] += 1
                continue
            lateness = (current - request.scheduled_at).total_seconds() / 60
            if lateness > max(policy.max_snapshot_lateness_minutes, 0):
                print(f"Missed request........................ {path.name} ({lateness:.0f} minutes late)")
                if mode == "execute":
                    self._mark_failed(path, request.original_text, [("REQUEST", "MISSED", "past max_snapshot_lateness_minutes")])
                    summary["failed"] += 1
                else:
                    summary["skipped"] += 1
                continue

            summary["processed"] += 1
            results = self._resolve_targets(request.targets, vms)
            print(f"Due request........................... {path.name}")
            for vm, status, detail in results:
                print(f"- {vm.name if vm else detail}: {status}")
            if mode in {"audit", "dry_run"}:
                print(f"{mode.replace('_', ' ').title()}: no snapshots were created.")
                continue

            outcomes = []
            for vm, status, detail in results:
                if status != "READY":
                    outcomes.append((vm or detail, "FAILED", detail))
                    continue
                name = _format_snapshot_name(policy.snapshot_name_prefix, request.scheduled_at, vm.name)
                try:
                    provider.create_snapshot(
                        vm.uuid,
                        name,
                        timeout_seconds=max(policy.task_timeout_minutes, 1) * 60,
                    )
                    outcomes.append((vm.name, "SUCCESS", name))
                except Exception as exc:
                    outcomes.append((vm.name, "FAILED", str(exc)))
            if all(item[1] == "SUCCESS" for item in outcomes):
                archive_directory.mkdir(parents=True, exist_ok=True)
                destination = _unique_path(archive_directory / _result_path(path, "done").name)
                destination.write_text(self._append_results(request.original_text, outcomes), encoding="utf-8")
                path.unlink()
                summary["success"] += 1
                print(f"Archived............................. {destination}")
            else:
                self._mark_failed(path, request.original_text, outcomes)
                summary["failed"] += 1
                print(f"Marked failed........................ {path.name}")
        return summary

    @staticmethod
    def _resolve_targets(targets, vms):
        results = []
        seen = set()
        for target in targets:
            matches = [vm for vm in vms if vm.uuid == target or vm.name == target]
            if "*" in target or "?" in target:
                matches = [vm for vm in vms if fnmatchcase(vm.name, target)]
            for vm in matches:
                if vm.uuid not in seen:
                    seen.add(vm.uuid)
                    results.append((vm, "READY", ""))
            if not matches:
                results.append((None, "FAILED", f"VM not found: {target}"))
        return results

    @staticmethod
    def _append_results(original, outcomes):
        lines = [original.rstrip(), "", "# RESULT"]
        lines.extend(f"# {target}: {status} - {detail}" for target, status, detail in outcomes)
        return "\n".join(lines) + "\n"

    def _mark_failed(self, path: Path, original: str, outcomes) -> None:
        destination = _unique_path(_result_path(path, "failed"))
        destination.write_text(self._append_results(original, outcomes), encoding="utf-8")
        path.unlink(missing_ok=True)
