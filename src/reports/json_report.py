"""JSON report writer."""

import json
from pathlib import Path


class JsonReport:
    """Write a report payload as formatted JSON."""

    def write(self, payload: dict, destination: str) -> Path:
        """Write the payload and return the resulting path."""

        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return path
