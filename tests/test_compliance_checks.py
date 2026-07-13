"""Tests for compliance checks."""

import unittest
from datetime import datetime, timedelta

from core.models import (
    CheckStatus,
    Inventory,
    Pool,
    Host,
    Snapshot,
    StorageRepository,
    VirtualMachine,
    Severity,
    ComplianceReport,
    CheckResult,
)
from core.config_models import (
    SnapshotAgePolicy,
    SnapshotCountPolicy,
    StorageRepositoryPolicy,
)
from checks.snapshot_age import SnapshotAgeCheck
from checks.snapshot_count import SnapshotCountCheck
from checks.sr_usage import StorageRepositoryUsageCheck


class SnapshotAgeCheckTests(unittest.TestCase):
    """Tests for Snapshot Age check."""

    def setUp(self):
        """Set up test fixtures."""
        self.policy = SnapshotAgePolicy(
            enabled=True,
            max_age_days=30,
            warning_days=25,
            severity="HIGH"
        )
        self.check = SnapshotAgeCheck(self.policy)
        
        self.inventory = Inventory(
            pools=[Pool(uuid="pool-1", name="Test Pool")],
            hosts=[Host(uuid="host-1", name="Test Host", enabled=True)],
            virtual_machines=[
                VirtualMachine(uuid="vm-1", name="Web Server", power_state="running")
            ],
            snapshots=[],
            storage_repositories=[],
        )

    def test_empty_inventory_passes(self):
        """Empty inventory should pass."""
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertEqual(result.passed_items, 0)
        self.assertEqual(result.failed_items, 0)

    def test_all_snapshots_within_limit_passes(self):
        """All snapshots within age limit should pass."""
        now = datetime.now()
        self.inventory.snapshots = [
            Snapshot(
                uuid="snap-1",
                name="Recent",
                vm_uuid="vm-1",
                vm_name="Web Server",
                sr_uuid="sr-1",
                sr_name="Local",
                created_at=(now - timedelta(days=10)).isoformat(),
            ),
            Snapshot(
                uuid="snap-2",
                name="Fresh",
                vm_uuid="vm-1",
                vm_name="Web Server",
                sr_uuid="sr-1",
                sr_name="Local",
                created_at=(now - timedelta(days=5)).isoformat(),
            ),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertEqual(result.passed_items, 2)
        self.assertEqual(result.failed_items, 0)

    def test_old_snapshot_fails(self):
        """Snapshot exceeding max age should fail."""
        now = datetime.now()
        self.inventory.snapshots = [
            Snapshot(
                uuid="snap-1",
                name="Old",
                vm_uuid="vm-1",
                vm_name="Web Server",
                sr_uuid="sr-1",
                sr_name="Local",
                created_at=(now - timedelta(days=45)).isoformat(),
            ),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.CRITICAL)
        self.assertEqual(result.passed_items, 0)
        self.assertEqual(result.failed_items, 1)
        self.assertGreater(result.risk_score, 0)

    def test_warning_snapshot(self):
        """Snapshot in warning range should trigger warning."""
        now = datetime.now()
        self.inventory.snapshots = [
            Snapshot(
                uuid="snap-1",
                name="Aging",
                vm_uuid="vm-1",
                vm_name="Web Server",
                sr_uuid="sr-1",
                sr_name="Local",
                created_at=(now - timedelta(days=28)).isoformat(),
            ),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.WARNING)
        self.assertEqual(result.failed_items, 1)

    def test_disabled_check_skips(self):
        """Disabled check should return SKIPPED."""
        self.policy.enabled = False
        self.check = SnapshotAgeCheck(self.policy)
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.SKIPPED)


class SnapshotCountCheckTests(unittest.TestCase):
    """Tests for Snapshot Count check."""

    def setUp(self):
        """Set up test fixtures."""
        self.policy = SnapshotCountPolicy(
            enabled=True,
            max_snapshots_per_vm=3,
            warning_count=2,
            severity="MEDIUM"
        )
        self.check = SnapshotCountCheck(self.policy)
        
        self.inventory = Inventory(
            pools=[],
            hosts=[],
            virtual_machines=[
                VirtualMachine(uuid="vm-1", name="Web Server", power_state="running"),
                VirtualMachine(uuid="vm-2", name="DB Server", power_state="running"),
            ],
            snapshots=[],
            storage_repositories=[],
        )

    def test_empty_inventory_passes(self):
        """Empty inventory should pass."""
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.PASS)

    def test_vms_within_limit_pass(self):
        """VMs within snapshot limit should pass."""
        self.inventory.snapshots = [
            Snapshot(uuid="snap-1", name="S1", vm_uuid="vm-1", vm_name="Web Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
            Snapshot(uuid="snap-2", name="S2", vm_uuid="vm-1", vm_name="Web Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
            Snapshot(uuid="snap-3", name="S3", vm_uuid="vm-2", vm_name="DB Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertEqual(result.passed_items, 2)

    def test_vm_exceeds_limit_fails(self):
        """VM exceeding snapshot limit should fail."""
        self.inventory.snapshots = [
            Snapshot(uuid="snap-1", name="S1", vm_uuid="vm-1", vm_name="Web Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
            Snapshot(uuid="snap-2", name="S2", vm_uuid="vm-1", vm_name="Web Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
            Snapshot(uuid="snap-3", name="S3", vm_uuid="vm-1", vm_name="Web Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
            Snapshot(uuid="snap-4", name="S4", vm_uuid="vm-1", vm_name="Web Server",
                     sr_uuid="sr-1", sr_name="Local", created_at=datetime.now().isoformat()),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.CRITICAL)
        self.assertEqual(result.failed_items, 1)
        self.assertGreater(result.risk_score, 0)


class StorageRepositoryUsageCheckTests(unittest.TestCase):
    """Tests for Storage Repository Usage check."""

    def setUp(self):
        """Set up test fixtures."""
        self.policy = StorageRepositoryPolicy(
            enabled=True,
            max_usage_percent=80.0,
            warning_percent=70.0,
            severity="CRITICAL"
        )
        self.check = StorageRepositoryUsageCheck(self.policy)
        
        self.inventory = Inventory(
            pools=[],
            hosts=[],
            virtual_machines=[],
            snapshots=[],
            storage_repositories=[],
        )

    def test_empty_inventory_passes(self):
        """Empty inventory should pass."""
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.PASS)

    def test_srs_within_limit_pass(self):
        """SRs within usage limit should pass."""
        self.inventory.storage_repositories = [
            StorageRepository(
                uuid="sr-1",
                name="Local",
                total_bytes=100 * 1024**3,
                used_bytes=50 * 1024**3,
                free_bytes=50 * 1024**3,
            ),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertEqual(result.passed_items, 1)

    def test_sr_exceeds_limit_fails(self):
        """SR exceeding usage limit should fail."""
        self.inventory.storage_repositories = [
            StorageRepository(
                uuid="sr-1",
                name="Local",
                total_bytes=100 * 1024**3,
                used_bytes=85 * 1024**3,
                free_bytes=15 * 1024**3,
            ),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.CRITICAL)
        self.assertEqual(result.failed_items, 1)
        self.assertGreater(result.risk_score, 0)

    def test_sr_in_warning_range(self):
        """SR in warning range should trigger warning."""
        self.inventory.storage_repositories = [
            StorageRepository(
                uuid="sr-1",
                name="Local",
                total_bytes=100 * 1024**3,
                used_bytes=75 * 1024**3,
                free_bytes=25 * 1024**3,
            ),
        ]
        
        result = self.check.run(self.inventory)
        self.assertEqual(result.status, CheckStatus.WARNING)
        self.assertEqual(result.failed_items, 1)


class ComplianceReportTests(unittest.TestCase):
    """Tests for ComplianceReport aggregation."""

    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        # Risk score logic:
        # - status_weight: CRITICAL=10, WARNING=5, PASS=0
        # - severity_weight: CRITICAL=10, HIGH=7, MEDIUM=3, LOW=1, INFO=0
        # - risk_score = max(status_weight, severity_weight) * failed_items
        # So: CRITICAL+CRITICAL=10*1=10, WARNING+HIGH=max(5,7)*1=7, PASS+INFO=0*0=0
        # Total = 10 + 7 + 0 = 17
        # Risk level: 0=LOW, <20=MEDIUM, <50=HIGH, >=50=CRITICAL
        results = [
            CheckResult(
                name="Test 1",
                description="Test",
                status=CheckStatus.CRITICAL,
                severity=Severity.CRITICAL,
                message="Critical issue",
                passed_items=0,
                failed_items=1,
            ),
            CheckResult(
                name="Test 2",
                description="Test",
                status=CheckStatus.WARNING,
                severity=Severity.HIGH,
                message="Warning issue",
                passed_items=0,
                failed_items=1,
            ),
            CheckResult(
                name="Test 3",
                description="Test",
                status=CheckStatus.PASS,
                severity=Severity.INFO,
                message="All good",
                passed_items=1,
                failed_items=0,
            ),
        ]
        
        report = ComplianceReport(check_results=results)
        
        self.assertEqual(report.total_checks, 3)
        self.assertEqual(report.passed_checks, 1)
        self.assertEqual(report.warning_checks, 1)
        self.assertEqual(report.critical_checks, 1)
        # Risk scores: CRITICAL+CRITICAL=10*1=10, WARNING+HIGH=max(5,7)*1=7, PASS+INFO=0*0=0
        self.assertEqual(report.total_risk_score, 17)
        self.assertEqual(report.overall_status, CheckStatus.CRITICAL)
        # 17 < 20, so risk_level is MEDIUM
        self.assertEqual(report.risk_level, "MEDIUM")


if __name__ == "__main__":
    unittest.main()
