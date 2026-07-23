# XCP-ng Snapshot Manager

# Development Guide

This document describes the development workflow, coding standards and project conventions.

Every contributor should read this document before submitting changes.

---

# Development Philosophy

The objective is not only to write working code.

The objective is to build a maintainable, extensible and predictable project.

Every change should improve the project without introducing technical debt.

Project principles:

* Small commits
* Stable releases
* No technical debt
* One responsibility per class
* One feature per sprint

---

# Sprint Workflow

Each sprint must have:

* One clear objective
* One visible new capability
* One stable release

Workflow:

```text
Plan

↓

Implement

↓

Test

↓

Commit

↓

Architecture Freeze

↓

Next Sprint
```

The project must compile and execute successfully after every sprint.

---

# Architecture Rules

The project follows a layered architecture.

```text
Engine
    │
    ▼
Provider
    │
    ▼
Client
    │
    ▼
Mapper
    │
    ▼
Inventory
    │
    ▼
Checks
    │
    ▼
Reports
    │
    ▼
Remediation
    │
    ▼
Verification
```

Each layer has one responsibility.

---

# Coding Standards

## Language

Everything is written in English.

Including:

* source code
* comments
* documentation
* commit messages
* pull requests

---

## Naming

Use explicit names.

Good examples:

* SnapshotAgeCheck
* InventoryProvider
* ProviderCapabilities
* StorageRepository

Avoid abbreviations whenever possible.

---

## Data Models

Business objects are represented using dataclasses.

Examples:

* Snapshot
* VirtualMachine
* StorageRepository
* Inventory

Avoid dictionaries whenever possible.

Prefer:

```python
inventory.snapshots
```

instead of:

```python
inventory["snapshots"]
```

---

## Configuration

Configuration is loaded once.

The rest of the application works with configuration objects.

Avoid nested dictionary access.

The v0.0.8 SR maintenance policy is exposed as `config.maintenance` and is
disabled by default. The one-shot command discovers all SRs, skips UUIDs in
`blacklist_sr_uuids`, enforces `min_interval_hours`, and persists run state in
`state_file`. `interval_hours` documents the intended scheduler cadence; cron
or a systemd timer invokes the command. Only `mode: execute` starts XO scan
tasks; `audit` and `dry_run` are non-mutating.

---

## Checks

Checks are plugins.

A check:

* receives an Inventory
* returns a CheckResult

Checks never:

* communicate with Xen Orchestra
* generate reports
* print output

---

## Providers

Providers collect infrastructure data.

Providers never evaluate compliance.

Providers never generate reports.

Every provider returns the same Inventory object.

---

## Clients

Clients communicate with external APIs.

Clients never build Inventory objects.

Clients never perform compliance checks.

---

## Mappers

Mappers convert external API responses into internal objects.

The rest of the application never manipulates raw JSON.

---

## Reports

Reports display results.

Reports never collect data.

Reports never evaluate compliance.

---

## Remediation

Remediation is optional.

Execution modes:

* Audit
* Dry Run
* Execute

Destructive actions must always require explicit user approval.

---

# Commit Messages

Keep commit messages short and descriptive.

Examples:

```
Add XO provider base

Implement snapshot age check

Add HTML reporter

Refactor inventory models
```

---

# Git Workflow

The main branch must always remain stable.

Recommended workflow:

```text
feature/provider-xo

↓

Merge

↓

Tag

↓

Release
```

---

# Release Strategy

Each release introduces one visible capability.

Example roadmap:

* v0.0.1 Bootstrap
* v0.0.2 Configuration
* v0.0.3 Provider
* v0.0.4 Inventory
* v0.1.0 First Compliance Check

---

# Definition of Done

A sprint is complete only if:

* Code compiles
* Tests succeed
* Documentation is updated
* ROADMAP is updated
* CHANGELOG is updated
* No TODO remains
* No technical debt is introduced

---

# Long-Term Vision

The project aims to become the reference open-source framework dedicated to snapshot and Storage Repository governance for XCP-ng.

The focus remains intentionally narrow.

The objective is excellence within a clearly defined scope rather than supporting every possible virtualization feature.
