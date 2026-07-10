# Changelog

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
