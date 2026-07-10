# MarketDEX OS Capability Matrix

**Status:** Active baseline
**Authority:** Derived operational engineering status
**Owner:** Lead Software Architect
**Update trigger:** Merged delivery changes capability evidence or classification
**Baseline:** `main` after PR #123, with CAP-009B Build 499 delivery evidence pending PR #124 merge

## Status Vocabulary

`Complete`, `Partial`, `Missing`, and `Deprecated` are the only capability classifications. Status is derived from repository implementation, workbook authority, and verification evidence. It is not a roadmap estimate.

| Capability ID | Capability | Workbook / Requirement Authority | Repository Evidence | Verification Evidence | Status | Next Action |
|---|---|---|---|---|---|---|
| CAP-001 | Inventory authority and operator workflow | Inventory / REQ-INV-001 | `services/inventory_app_service.py`; `services/inventory_service.py`; `repositories/inventory_repository.py`; inventory UI feature modules; schema inventory tables | Inventory CI gate and inventory integration/default/sort tests | Complete | Preserve; extend only through a separately justified capability boundary |
| CAP-002 | Pricing and profit guidance | Workbook pricing/profit surfaces | `ui/inventory_cost_feature.py`; `ui/inventory_profit_feature.py`; `ui/inventory_price_guidance_feature.py` | Pricing CI gate; profit and price-guidance feature tests | Complete | Preserve regression coverage |
| CAP-003 | Listing planning and execution workflow | Listing workflow and sale-completion workbook authority | `listing_plans`; listing package review schema; listing UI feature chain; publication lifecycle services | Listing CI gate; listing plan repository and operator sale-completion tests | Complete | Preserve; reconcile future workbook changes before extension |
| CAP-004 | Mission Control / dashboard | Mission Control / REQ-MIS-001 | `services/mission_control_service.py`; `services/dashboard_service.py`; dashboard and mission-control UI components | Dashboard layout, navigation, M27 Mission Control, and end-to-end conformance tests exist | Partial | Reconcile permanent root runtime dashboard against duplicated `app/` dashboard surfaces before changing behavior |
| CAP-005 | Product Registry | Product Registry / REQ-PROD-001 | `services/product_registry_service.py`; product-aware services reference `product_id` | Product-aware closure and M38/M39B acceptance tests provide indirect evidence | Partial | Verify persistence authority and operator surface; do not rebuild service logic |
| CAP-006 | Collection | Collection / REQ-COL-001 | Collection navigation/card surfaces exist under `app/ui/`; no verified root collection service/repository found in reconciliation search | No dedicated collection test evidence found | Missing | Define first vertical slice only after confirming workbook authority and permanent runtime integration point |
| CAP-007 | Audit and immutable history | Audit Trail / REQ-AUD-001 | `event_identity`; `audit_history`; `audit_events`; append-only and immutable schema triggers | Core runtime authority and multiple authority/conformance tests | Complete | Preserve append-only authority |
| CAP-008 | Settlement execution authority | Settlement Evidence Intake and Linkage Rules / REQ-SET-001; workbook Builds 481-497 | `services/settlement_service.py`; `repositories/settlement_repository.py`; `settlement_evidence`; `settlement_executions`; `settlement_history` | CAP-008A settlement evidence parent tests and M39A settlement regression suite run in Core Tests CI | Partial | Preserve CAP-008A parent authority; reconcile remaining Builds 481-497 parity separately |
| CAP-009 | Settlement allocation evidence and cross-check | Settlement Allocation Evidence / REQ-ALL-001; Builds 498-500 | Build 498 `settlement_allocation_evidence`; Build 499 `settlement_allocation_cross_checks`; `SettlementAllocationRepository`; `SettlementAllocationService`; marketplace allocation remains separate inventory reservation authority | CAP-009A intake and CAP-009B group cross-check/remainder fail-closed contract tests in Core Tests CI; Build 500 direct parity evidence absent | Partial | After CAP-009B merge, implement the smallest Build 500 sale-level Settlement Attribution Readiness authority gate |
| CAP-010 | Allocation evidence revision and supersession | Allocation Evidence Revisions / REQ-ALL-002; Build 502 | No verified allocation evidence revision service or persistence authority matching Build 502 found | No direct supersession test evidence found | Missing | Implement only after CAP-009 canonical evidence model exists |
| CAP-011 | Allocation evidence lock and audit preservation | Allocation Evidence Locks / REQ-ALL-003; Build 503 | Existing immutable audit infrastructure is reusable; no verified allocation evidence lock service matching Build 503 found | No direct Build 503 lock/preservation parity test found | Missing | Implement after CAP-010 using existing immutable audit patterns |
| CAP-012 | Reports | Workbook reporting surfaces; desktop charter release sequence | No verified canonical root report workflow found in reconciliation search | No dedicated report regression evidence found | Missing | Defer until authority-heavy settlement/allocation gap is closed |
| CAP-013 | Runtime database authority and migration | Desktop implementation authority | `launcher.py`; `core/runtime_database_migration.py`; schema version 20 on CAP-009B delivery branch; runtime SQLite path | Core Tests CI gate; `test_runtime_database_authority.py` | Complete | Preserve single database authority |
| CAP-014 | Desktop shell and navigation | Desktop engineering authority | root `launcher.py`; `ui/main_window.py`; viewport feature; workspace/navigation surfaces | Desktop Build CI gate; workspace navigation and maximized-launch contract tests | Complete | Preserve permanent root launcher authority |

## Current Priority

**CAP-009 — Settlement allocation evidence and cross-check** remains the highest-value incomplete capability. CAP-009A supplies Build 498 intake authority. CAP-009B supplies the Build 499 group-total, signed remainder, and append-only cross-check result authority without mutating allocation evidence lines or redistributing money.

After CAP-009B is merged and verified on `main`, the next controlled boundary is the smallest missing Build 500 sale-level Settlement Attribution Readiness authority gate. Builds 502-503 remain later capabilities.

## Matrix Rule

A `Complete` classification prohibits rebuilding the capability. A `Partial` capability must be extended through the existing permanent architecture. A `Missing` capability may be introduced only after repository search confirms no canonical implementation exists.
