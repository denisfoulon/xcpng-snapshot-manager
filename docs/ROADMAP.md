# Roadmap

## v0.0.1 - Bootstrap
- [x] Project structure
- [x] Execution engine
- [x] First checks

## v0.0.2 - Configuration
- [x] YAML configuration
- [x] Banner
- [x] Configuration loader

## v0.0.3 - Provider Connection
- [x] Typed configuration
- [x] REST client
- [x] XO client
- [x] Provider abstraction
- [x] XO provider
- [x] Provider connection
- [x] Provider disconnection

## v0.0.4 - Inventory
- [x] Pools
- [x] Hosts
- [x] Virtual Machines
- [x] Snapshots
- [x] Storage Repositories
- [x] Inventory models
- [x] Console inventory report

## v0.0.5 - Compliance
- [x] Snapshot age
- [x] Snapshot count
- [x] SR usage
- [ ] Policies
- [ ] Risk score

## v0.0.6 - Reporting
- [x] Rich console output
- [x] JSON export
- [x] HTML report

## v0.0.7 - Remediation
- [x] Delete expired snapshots
- [x] Blacklist support
- [x] Blacklist maximum age
- [x] Dry-run mode
- [x] Explicit execute confirmation
- [x] Post-remediation verification

## v0.0.8 - Advanced SR Vacuum
- [x] Automatic discovery of all Storage Repositories
- [x] Storage Repository blacklist
- [x] Configurable vacuum interval and minimum cooldown
- [x] Audit and dry-run vacuum modes
- [x] SR scan task execution through Xen Orchestra
- [x] Task polling and timeout handling
- [x] Scan task timeout and serialized execution safeguards
- [x] Before/after free-space measurement
- [x] Vacuum history and last-run state
- [x] Cron/systemd scheduling documentation

Target configuration:

```yaml
maintenance:
  vacuum:
    enabled: false
    mode: audit
    interval_hours: 24
    min_interval_hours: 20
    blacklist_sr_uuids: []
```

## v0.1.0 - Advanced Compliance
- [ ] Policies
- [ ] Risk score
