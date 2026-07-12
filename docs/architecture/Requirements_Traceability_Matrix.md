# MarketDEX OS Requirements Traceability Matrix

## Purpose
Trace authoritative workbook specification sources to desktop implementation components and verification evidence.

| Requirement ID | Workbook Source | Desktop Component | Verification | Status |
|---|---|---|---|---|
| REQ-INV-001 | Inventory | Inventory Domain / Service / UI | Planned inventory vertical-slice tests | Planned |
| REQ-COL-001 | Collection | Provisional read-only `CollectionPositionService`; `CollectionPositionWorkspace`; canonical workspace registration and application composition; `CAP-006B_COLLECTION_WRITE_AUTHORITY_GATE.md` blocks unapproved Collection persistence and mutations | CAP-006 deterministic projection, bounded search, empty/unmatched, restart-safe read, zero-mutation, read-only workspace, and navigation evidence merged in PR #175; CAP-006B authority separation is documentation-gated | In Progress |
| REQ-PROD-001 | Product Registry | `ProductRegistryService`; `ProductRegistryLookupService`; read-only `ProductRegistryWorkspace`; canonical workspace catalog and application composition | CAP-005A persistence, CAP-005B linkage, and CAP-005C lookup/workspace/navigation/zero-mutation tests in Core Tests and Desktop Build CI | Verified |
| REQ-MIS-001 | Mission Control | root `launcher.py`; `MissionControlService`; root `MainWindow` Mission Control cards | Exact snapshot contract, protected SQLite projection, read-only behavior, and permanent-root launcher selection in `test_mission_control_integration.py`; dedicated Mission Control vertical-slice CI gate | Verified |
| REQ-AUD-001 | Audit Trail | Audit Domain / Service / Repository | Planned append-preservation tests | Planned |
| REQ-SET-001 | Settlement Evidence Intake; Settlement Linkage Rules; Builds 481-497 | `settlement_evidence`; `settlement_evidence_linkage`; `SettlementRepository`; settlement services and read-only verification authority derivation | CAP-008A parent-grain, CAP-008B linkage, CAP-008C Build 484 pending-allocation, CAP-008D Builds 487-497 verification authority-chain, and M39A regression tests in Core Tests CI | Verified |
| REQ-ALL-001 | Settlement Allocation Evidence; Builds 498-500 | `settlement_allocation_evidence`; `settlement_allocation_cross_checks`; immutable `audit_events` readiness evidence; `SettlementAllocationRepository`; `SettlementAllocationService` | CAP-009A Build 498 intake, CAP-009B Build 499 cross-check/remainder, and CAP-009C Build 500 sale-level Settlement Attribution Readiness contract tests in Core Tests CI | Verified |
| REQ-ALL-002 | Allocation Evidence Revisions; Build 502 | `settlement_allocation_revisions`; immutable revision triggers; `SettlementAllocationRepository`; `SettlementAllocationService` | CAP-010A Build 502 revision lineage, status, conflict, fail-closed, replay, immutability, and restart tests in Core Tests CI | Verified |
| REQ-ALL-003 | Allocation Evidence Locks; Build 503 plus Build 504 authority audit | `settlement_allocation_locks`; `SettlementAllocationRepository`; `SettlementAllocationService`; immutable `audit_events` | CAP-011A lock, preservation, lifecycle, replay, immutability, restart, stale-cross-check, and active-revision conflict regressions in Core Tests CI | Verified |

## Traceability Rule
A desktop requirement is not complete until its workbook source, implementation component, and verification evidence are identified. Status values are `Planned`, `In Progress`, `Verified`, or `Blocked`.

REQ-COL-001 remains `In Progress` because its read-only projection is verified while its Collection-owned position grain, field vocabulary, evidence ownership, lifecycle, persistence, and mutation contracts remain blocked by the CAP-006B authority gate.
