# Changelog

## v0.1.0 - Compliance

### Added

- **Compliance Policies**: YAML configuration for compliance thresholds
  - `snapshot_age`: max_age_days, warning_days, severity
  - `snapshot_count`: max_snapshots_per_vm, warning_count, severity
  - `storage_repository`: max_usage_percent, warning_percent, severity
- **Implemented Compliance Checks**
  - Snapshot Age: Checks if snapshots exceed configured age limits
  - Snapshot Count: Checks if VMs have too many snapshots
  - SR Usage: Checks if Storage Repositories exceed usage thresholds
- **Risk Score System**
  - Automatic risk score calculation based on check status and severity
  - Aggregate risk score for overall compliance assessment
  - Risk levels: LOW, MEDIUM, HIGH, CRITICAL
- **Enhanced CheckResult Model**
  - Added: description, passed_items, failed_items, affected_items
  - Added: remediation_hint, risk_score
  - CheckItem dataclass for detailed affected item information
- **ComplianceReport Model**
  - Aggregate compliance metrics
  - Overall status calculation
  - Total risk score aggregation
- **Enhanced Console Reporting**
  - Detailed compliance report display
  - Check results with affected items
  - Risk score and level visualization

### Changed

- CheckResult now includes comprehensive compliance information
- Engine passes policies to checks automatically
- Console report now displays full compliance information

### Fixed

- Check discovery now works with updated check classes

## v0.0.4

### Added

- Xen Orchestra inventory collection for pools, hosts, virtual machines, snapshots and Storage Repositories.
- Console inventory summary.

### Changed

- The engine now collects inventory between provider connection and disconnection.

## v0.0.3

### Added

- REST client
- XO client
- Provider abstraction
- Typed configuration
- Provider health model
- Provider capabilities model
- XO provider integration
- Connection workflow

### Changed

- Configuration now uses dataclasses.
- Engine now supports providers.

### Fixed

- Provider lifecycle.
- HTTP session handling.

## v0.0.2

### Added

- Configuration loader
- YAML configuration support

### Changed

- Application bootstrap

### Fixed

- CheckStatus display
