"""Tests for report serialization and writers."""

import json
import tempfile
import unittest
from pathlib import Path

from core.models import CheckResult, CheckStatus, Inventory
from reports.html_report import HtmlReport
from reports.json_report import JsonReport
from reports.serialization import build_report


class ReportTests(unittest.TestCase):
    """Verify JSON and HTML reports contain the same result data."""

    def test_json_report_is_machine_readable(self) -> None:
        payload = build_report(
            Inventory(),
            [CheckResult("Example", CheckStatus.PASS, "INFO", "All good")],
        )
        with tempfile.TemporaryDirectory() as directory:
            path = JsonReport().write(payload, str(Path(directory) / "report.json"))
            content = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(content["checks"][0]["status"], "PASS")

    def test_html_report_contains_check(self) -> None:
        payload = build_report(
            Inventory(),
            [CheckResult("Example", CheckStatus.WARNING, "WARNING", "Review")],
        )
        with tempfile.TemporaryDirectory() as directory:
            path = HtmlReport().write(payload, str(Path(directory) / "report.html"))
            content = path.read_text(encoding="utf-8")

        self.assertIn("Example", content)
        self.assertIn("WARNING", content)


if __name__ == "__main__":
    unittest.main()
