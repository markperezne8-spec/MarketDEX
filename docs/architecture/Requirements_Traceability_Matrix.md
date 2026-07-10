# MarketDEX OS Requirements Traceability Matrix

## Purpose
Trace authoritative workbook specification sources to desktop implementation components and verification evidence.

| Requirement ID | Workbook Source | Desktop Component | Verification | Status |
|---|---|---|---|---|
| REQ-INV-001 | Inventory | Inventory Domain / Service / UI | Planned inventory vertical-slice tests | Planned |
| REQ-COL-001 | Collection | Collection Domain / Service / UI | Planned collection tests | Planned |
| REQ-PROD-001 | Product Registry | Product Registry Domain / Service | Planned registry tests | Planned |
| REQ-MIS-001 | Mission Control | Dashboard UI / Query Services | Planned dashboard regression tests | Planned |
| REQ-AUD-001 | Audit Trail | Audit Domain / Service / Repository | Planned append-preservation tests | Planned |
| REQ-SET-001 | Settlement Evidence Intake; Settlement Linkage Rules | `settlement_evidence`; `SettlementRepository`; settlement services | CAP-008A parent-grain contract tests and M39A regression tests in Core Tests CI | In Progress |
| REQ-ALL-001 | Settlement Allocation Evidence; Builds 498-500 | `settlement_allocation_evidence`; `SettlementAllocationRepository`; `SettlementAllocationService` | CAP-009A Build 498 fail-closed contract tests in Core Tests CI; Builds 499-500 remain unimplemented | In Progress |
| REQ-ALL-002 | Allocation Evidence Revisions | Allocation Revision Service | Planned supersession tests | Planned |
| REQ-ALL-003 | Allocation Evidence Locks | Allocation Lock Service | Planned lock and preservation tests | Planned |

## Traceability Rule
A desktop requirement is not complete until its workbook source, implementation component, and verification evidence are identified. Status values are `Planned`, `In Progress`, `Verified`, or `Blocked`.
