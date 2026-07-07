# XCP-ng Snapshot Manager

## Architecture

### Philosophy

XCP-ng Snapshot Manager is **not** a snapshot deletion script.

It is a **policy-driven compliance engine** dedicated to XCP-ng snapshots and Storage Repositories.

The application continuously:

* Observes the infrastructure
* Evaluates compliance against user-defined policies
* Reports deviations
* Remediates issues (optional)
* Verifies the result

The cleanup of snapshots is only one possible remediation action.

---

# Execution Pipeline

```
Observe
    │
    ▼
Evaluate
    │
    ▼
Report
    │
    ▼
Remediate
    │
    ▼
Verify
```

Each execution always follows this pipeline.

The engine never skips a stage.

---

# Core Principles

## Single Responsibility

Each module has one responsibility.

Examples:

* Engine orchestrates the execution.
* InventoryProvider collects infrastructure data.
* Checks evaluate compliance.
* Reporters display results.
* Remediation performs corrective actions.

---

## Separation of Concerns

Infrastructure collection is completely independent from compliance evaluation.

Checks never communicate directly with Xen Orchestra.

They only receive an `Inventory` object.

---

## Extensibility

The application automatically discovers available checks.

Adding a new compliance rule only requires creating a new file inside the `checks/` directory.

The engine never needs to be modified.

---

## Providers

Providers are responsible for collecting infrastructure data.

The engine selects the active provider according to the configuration file.

Supported providers:

* Xen Orchestra (default)
* XAPI (planned)
* JSON Inventory (planned)
* Mock Provider (planned)

Each provider returns the same Inventory object.

This guarantees that compliance checks remain platform independent.

---

## Clients

Clients are responsible for communicating with external systems.

A client only knows how to authenticate, send requests and receive responses.

Clients never build Inventory objects.

Future clients include:

* XOClient
* XAPIClient

This separation keeps transport logic isolated from business logic.

---
# Mappers

Mappers convert raw API responses into internal data models.

For example:

API Response

↓

Snapshot

VirtualMachine

StorageRepository

The rest of the application never manipulates raw JSON returned by external APIs.

---

## Reporters

Reporters are responsible for presenting the results.

Future reporters include:

* Console
* HTML
* JSON
* Email
* Slack
* Teams
* Telegram

Checks never produce output directly.

---

## Remediation

Remediation is optional.

Execution modes:

* Audit
* Dry Run
* Execute

Destructive actions should never occur without explicit user approval.

---

## Project Architecture

```text
                           Engine
                              │
                              ▼
                    Inventory Provider
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
          XO Provider                 XAPI Provider
                │                           │
                ▼                           ▼
            XO Client                 XAPI Client
                │                           │
                ▼                           ▼
              Mapper                     Mapper
                │
                ▼
           Inventory Model
                │
                ▼
             Compliance Checks
                │
                ▼
             Check Results
                │
                ▼
              Reporters
                │
                ▼
            Remediation
                │
                ▼
             Verification
```

The Engine never communicates directly with Xen Orchestra or XAPI.

Infrastructure-specific logic belongs to Providers and Clients.

Checks always work with the internal Inventory model and remain completely independent from the underlying virtualization platform.

---

# Coding Rules

* English only.
* One responsibility per class.
* No business logic inside data models.
* No direct communication between checks and Xen Orchestra.
* No direct printing from checks.
* Every new feature should fit naturally into the execution pipeline.
* Every commit must leave the project in a working state.

---

# Long-Term Vision

XCP-ng Snapshot Manager aims to become the reference open-source framework for snapshot governance on XCP-ng.

The objective is not only to clean old snapshots but to continuously ensure infrastructure compliance through policies, reporting and safe remediation.
