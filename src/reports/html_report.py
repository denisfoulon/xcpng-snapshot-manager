"""Standalone HTML report writer."""

from html import escape
from pathlib import Path


class HtmlReport:
    """Render a report payload as a small self-contained HTML document."""

    def write(self, payload: dict, destination: str) -> Path:
        """Write the HTML report and return the resulting path."""

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        inventory = payload["inventory"]
        checks = payload["checks"]
        summary = [
            ("Pools", len(inventory["pools"])),
            ("Hosts", len(inventory["hosts"])),
            ("Storage repositories", len(inventory["storage_repositories"])),
            ("Virtual machines", len(inventory["virtual_machines"])),
            ("Snapshots", len(inventory["snapshots"])),
        ]
        summary_rows = "".join(
            f"<tr><th>{escape(name)}</th><td>{count}</td></tr>"
            for name, count in summary
        )
        check_rows = "".join(
            "<tr>"
            f"<td>{escape(check['name'])}</td>"
            f"<td class=\"{escape(check['status'])}\">"
            f"{escape(check['status'])}</td>"
            f"<td>{escape(check['message'])}</td>"
            "</tr>"
            for check in checks
        )
        snapshot_rows = "".join(
            "<tr>"
            f"<td>{escape(snapshot['vm_name'] or 'unknown VM')}</td>"
            f"<td>{escape(str(snapshot['age_days']) if snapshot['age_days'] is not None else 'unknown')}</td>"
            f"<td>{escape(snapshot['created_at_iso'] or 'unknown')}</td>"
            f"<td>{escape(snapshot['description'] or 'none')}</td>"
            f"<td>{escape(snapshot['name'] or snapshot['uuid'])}</td>"
            f"<td>{escape(snapshot['sr_name'] or 'unknown SR')}</td>"
            f"<td>{snapshot['size_bytes']}</td>"
            "</tr>"
            for snapshot in inventory["snapshots"]
        )
        document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>XCP-ng Snapshot Manager Report</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; color: #1f2937; }}
    table {{ border-collapse: collapse; margin: 1rem 0 2rem; min-width: 32rem; }}
    th, td {{ border: 1px solid #d1d5db; padding: .5rem .75rem; text-align: left; }}
    th {{ background: #f3f4f6; }}
    .PASS {{ color: #166534; }} .WARNING {{ color: #a16207; }}
    .CRITICAL, .ERROR {{ color: #b91c1c; }} .SKIPPED {{ color: #4b5563; }}
  </style>
</head>
<body>
  <h1>XCP-ng Snapshot Manager</h1>
  <p>Generated at {escape(payload['generated_at'])}</p>
  <h2>Infrastructure Summary</h2>
  <table><tbody>{summary_rows}</tbody></table>
  <h2>Compliance Checks</h2>
  <table><thead><tr><th>Check</th><th>Status</th><th>Message</th></tr></thead>
  <tbody>{check_rows}</tbody></table>
  <h2>Snapshot Details</h2>
  <table><thead><tr><th>VM</th><th>Age (days)</th><th>Created at</th><th>Comment</th><th>Snapshot</th><th>Storage Repository</th><th>Size (bytes)</th></tr></thead>
  <tbody>{snapshot_rows}</tbody></table>
</body>
</html>
"""
        path.write_text(document, encoding="utf-8")
        return path
