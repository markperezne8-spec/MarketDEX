# MarketDEX OS Capability Matrix

**Status:** Active baseline
**Authority:** Derived operational engineering status
**Owner:** Lead Software Architect
**Update trigger:** Merged delivery changes capability evidence or classification
**Baseline:** `main` at PR #753 merge commit `5fe59155cee74b79406ab0c7e3356919a24a1d5c` / CAP-012/CAP-006 regression evidence reconciliation

## Status Vocabulary

`Complete`, `Partial`, `Missing`, and `Deprecated` are the only capability classifications. Status is derived from repository implementation, workbook authority, and verification evidence. It is not a roadmap estimate.

| Capability ID | Capability | Workbook / Requirement Authority | Repository Evidence | Verification Evidence | Status | Next Action |
|---|---|---|---|---|---|---|
| CAP-001 | Inventory authority and operator workflow | Inventory / REQ-INV-001 | `services/inventory_app_service.py`; `services/inventory_service.py`; `repositories/inventory_repository.py`; inventory UI feature modules; schema inventory tables | Inventory CI gate and inventory integration/default/sort tests | Complete | Preserve; extend only through a separately justified capability boundary |
| CAP-002 | Pricing and profit guidance | Workbook pricing/profit surfaces | `ui/inventory_cost_feature.py`; `ui/inventory_profit_feature.py`; `ui/inventory_price_guidance_feature.py` | Pricing CI gate; profit and price-guidance feature tests | Complete | Preserve regression coverage |
| CAP-003 | Listing planning and execution workflow | Listing workflow and sale-completion workbook authority | `listing_plans`; listing package review schema; listing UI feature chain; publication lifecycle services | Listing CI gate; listing plan repository and operator sale-completion tests | Complete | Preserve; reconcile future workbook changes before extension |
| CAP-004 | Mission Control / dashboard | Mission Control / REQ-MIS-001 | root `launcher.py` selects `services/mission_control_service.py`; root `ui/main_window.py` renders the canonical nine-key read-only snapshot contract; broader `services/dashboard_service.py` remains non-root legacy/secondary evidence | `tests/test_mission_control_integration.py` gates protected SQLite projection semantics, read-only behavior, exact snapshot keys, and permanent-root launcher selection; dedicated Mission Control vertical-slice CI gate | Complete | Preserve root `MissionControlService` as canonical desktop projection; do not promote `DashboardService` or add metrics without a separately justified authority boundary |
| CAP-005 | Product Registry | Product Registry / REQ-PROD-001 | `services/product_registry_service.py`; `services/product_registry_lookup_service.py`; read-only `ui/product_registry_workspace.py`; root application composition and workspace catalog registration | CAP-005A persistence, CAP-005B inventory linkage, CAP-005C lookup/workspace/navigation/zero-mutation tests; Core Tests and Desktop Build CI | Complete | Preserve the canonical registry and read-only operator lookup; extend only through a separately justified capability boundary |
| CAP-006 | Collection | Collection / REQ-COL-001 | Provisional read-only `services/collection_position_service.py`; `ui/collection_position_workspace.py`; canonical workspace registration and application composition; `docs/Architecture/CAP-006B_COLLECTION_WRITE_AUTHORITY_GATE.md`; `docs/Architecture/CAP-006E_COLLECTION_VISUAL_AUTHORITY_EVIDENCE.md`; no Collection write authority | CAP-006 projection, empty/unmatched, workspace read-only, and navigation tests; Desktop/Core CI via PR #175; PR #737 CI #1034 and accepted visual evidence for the read-only authority card; PR #738 CAP-006E documentation reconciliation; PR #741 CI #1045 and accepted visual evidence for the empty-state panel; PR #745 CI #1053 and accepted visual evidence for the unrecorded field-authority panel | Partial | Preserve the read-only projection and enforce the CAP-006B authority gate; do not add persistence or mutations until workbook-backed position grain, field vocabulary, and ownership transitions are approved |
| CAP-007 | Audit and immutable history | Audit Trail / REQ-AUD-001 | `event_identity`; `audit_history`; `audit_events`; append-only and immutable schema triggers | Core runtime authority and multiple authority/conformance tests | Complete | Preserve append-only authority |
| CAP-008 | Settlement execution authority | Settlement Evidence Intake and Linkage Rules / REQ-SET-001; workbook Builds 481-497 | `services/settlement_service.py`; `repositories/settlement_repository.py`; `settlement_evidence`; `settlement_evidence_linkage`; `settlement_executions`; `settlement_history`; read-only settlement verification authority derivation | CAP-008A parent evidence, CAP-008B linkage, CAP-008C Build 484 pending-allocation, CAP-008D Builds 487-497 verification authority-chain, and M39A settlement regression suites in Core Tests CI; PR #148 green | Complete | Preserve settlement evidence and verification authority; do not create tax, reconciliation, automatic matching/allocation, or settlement-completion authority by assumption |
| CAP-009 | Settlement allocation evidence and cross-check | Settlement Allocation Evidence / REQ-ALL-001; Builds 498-501 | Build 498 `settlement_allocation_evidence`; Build 499 `settlement_allocation_cross_checks`; Build 500 sale-level readiness evidence through immutable `audit_events`; Build 501 lifecycle derivation in `SettlementAllocationService`; `SettlementAllocationRepository`; marketplace allocation remains separate inventory reservation authority | CAP-009A intake, CAP-009B group cross-check/remainder, CAP-009C sale-level readiness, CAP-009D lifecycle, and Build 504 stale cross-check authority regressions in Core Tests CI | Complete | Preserve current-group cross-check and lifecycle authority; do not fold marketplace inventory allocation into settlement allocation |
| CAP-010 | Allocation evidence revision and supersession | Allocation Evidence Revisions / REQ-ALL-002; Build 502 | schema v21 `settlement_allocation_revisions`; immutable triggers; `SettlementAllocationRepository`; `SettlementAllocationService`; exact Build 502 boundary audit | CAP-010A revision lineage, status derivation, conflict, fail-closed, replay, immutability, and restart reconstruction tests in Core Tests CI | Complete | Preserve Build 502 authority |
| CAP-011 | Allocation evidence lock and audit preservation | Allocation Evidence Locks / REQ-ALL-003; Build 503 plus Build 504 authority audit | `settlement_allocation_locks`; immutable lock triggers; `SettlementAllocationRepository`; `SettlementAllocationService`; lock audit evidence through `audit_events`; current lifecycle and single-active-revision revalidation on persisted lock reads | CAP-011A lock derivation, audit preservation, lifecycle prerequisite, replay, immutability, restart reconstruction, stale group cross-check, and active-revision conflict regressions in Core Tests CI; PR #139 CI #156 green | Complete | Preserve Build 503 lock authority and Build 504 fail-closed read revalidation; do not create a second lock architecture |
| CAP-012 | Reports | Workbook Analytics and Reports / REQ-REP-001; Build 701; approved Inventory Turnover and Purchase Source Performance business questions; CAP-012 contract sequence | `reports/definitions.py`; `reports/report_query_service.py`; Inventory Age request/provider/query boundaries; Inventory Turnover immutable request/result contract, provider/query boundary, deterministic calculator, canonical presenter, deterministic preview factory, catalog registration, and presentation-bound read-only KPI panel in `ui/reports_workspace.py`; Purchase Source Performance authority audit, formula vocabulary, planning and immutable runtime contracts, pure calculator, fail-closed query boundary, and constructor-injected read-only orchestration provider in `reports/purchase_source_performance_provider.py`; canonical application composition, `ApplicationComposition.query_purchase_source_performance`, workspace registration, and read-only Purchase Source Performance preview in `ui/reports_workspace.py` | Build 701 Inventory Age definition, projection, source-authority, request, query, composition, result-presentation, provenance, and visibility tests; CAP-012E through CAP-012M Inventory Turnover contract/query/calculation/presentation/factory tests; CAP-012R through CAP-012T Purchase Source Performance contract/calculator/query-boundary tests; CAP-012AL composition-boundary evidence and CAP-012AM provider, lifecycle, coverage, diagnostics, malformed-response, and no-SQLite tests; CAP-012BC preview contract tests and visual verification; CAP-012BE composition snapshot and visual verification; CAP-012AN documentation reconciliation; dedicated Reports CI gate; Desktop Build and installer coverage; PR #710 CI #994 green; PR #718 visual acceptance passed; PR #720 CI #1004 green; PR #725 CI #1013 green; composition query routing coverage in `tests/test_application_composition.py`; PR #739 CI #1041 and accepted visual evidence for the Inventory Age Patterns preview; PR #743 CI #1049 and accepted visual evidence for the Purchase Source Performance empty-result panel; PR #746 CI #1055 and accepted visual evidence for the Inventory Age evidence-gate panel; PR #748 CI #1059 and accepted visual evidence for the Reports catalog scope panel; PR #750 CI #1063 and accepted visual evidence for the three read-only preview state headers | Partial | Preserve the approved read-only report boundaries and explicit unavailable/conflict semantics; the composition-owned Purchase Source Performance query seam is delivered; live workspace execution, UI, exports, persistence, and expanded analytics remain separately gated |
| CAP-013 | Runtime database authority and migration | Desktop implementation authority | `launcher.py`; `core/runtime_database_migration.py`; schema version 23; runtime SQLite path | Core Tests CI gate; `test_runtime_database_authority.py` plus restart reconstruction evidence | Complete | Preserve single database authority |
| CAP-014 | Desktop shell and navigation | Desktop engineering authority | root `launcher.py`; `ui/main_window.py`; viewport feature; workspace/navigation surfaces | Desktop Build CI gate; workspace navigation and maximized-launch contract tests | Complete | Preserve permanent root launcher authority |

## Current Priority

**CAP-004, CAP-005, and CAP-008 through CAP-011 are Complete.** CAP-004A reconciled the permanent root Mission Control path: root `launcher.py` selects `MissionControlService`, root `MainWindow` consumes its exact nine-key read-only snapshot contract, and focused regression evidence prevents accidental promotion of the broader non-root `DashboardService` surface. CAP-005C closes the prior Product Registry operator-surface gap with a deterministic, read-only workspace over existing registry authority.

**CAP-006 and CAP-012 are Partial.** CAP-006 remains blocked at the read-only Collection Position boundary until workbook/business authority approves position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition rules. CAP-012 contains three approved workbook-backed report business questions: Inventory Age Patterns, Inventory Turnover, and Purchase Source Performance. Inventory Turnover has immutable request/result contracts, a fail-closed provider boundary, deterministic calculation, a canonical presenter, a deterministic preview factory, and a visually verified presentation-bound KPI workspace. Purchase Source Performance now has approved source authority and formula vocabulary, immutable request/result contracts, a deterministic pure calculator, a fail-closed query boundary, and a constructor-injected orchestration provider that joins canonical Inventory acquisition evidence to sale-completion authority with exact coverage and lifecycle reconciliation. Local read-only provider execution and composition-owned Purchase Source Performance workspace controls are delivered through PR #729; the Inventory Age Patterns read-only visual preview panel is delivered through PR #739. External providers, networking, exports, persistence, automation, and expanded analytics remain separately gated; unavailable and conflicting evidence must remain fail-closed.

The next controlled Reports movement must remain boundary-first. Any additional report requires selection of another workbook-backed business question and proof of its source-domain authority. Any movement of Purchase Source Performance beyond the delivered read-only composition snapshot requires a separately approved live-execution or expanded presentation boundary. Until then, preserve the approved reports and their explicit unavailable, non-found, and conflict semantics.

## Matrix Rule

A `Complete` classification prohibits rebuilding the capability. A `Partial` capability must be extended through the existing permanent architecture. A `Missing` capability may be introduced only after repository search confirms no canonical implementation exists.

## CAP-012 Reports post-PR #729 reconciliation

- CAP-012 remains `Partial`.
- PR [#729](https://github.com/markperezne8-spec/MarketDEX/pull/729) delivered the existing Purchase Source Performance query through the composition-owned application boundary and constructor-injected read-only Reports workspace controls.
- Exact PR head: `c5b67daac4c175242dafb1608defde3f487a7f46`.
- CI [#1017](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31787132407) passed for that exact head.
- Merge commit: `941c65ca4730f052a9f2f9bb9978de99fe74afaa`.
- Scope was limited to `ui/reports_workspace.py`, `composition/application_composition.py`, and `tests/test_reports_workspace.py`.
- The delivered surface is local, read-only, deterministic, fail-closed, and preserves coverage/provenance/outcome semantics.
- Visual acceptance passed from the maximized full-window Reports screenshot.
- External providers, networking, exports, persistence, automation, and expanded analytics remain separately gated.
- CAP-006 remains `Partial` and blocked on workbook-backed Collection position authority; this reconciliation introduces no Collection scope.


## CAP-006E Collection visual authority evidence reconciliation

- CAP-006 remains `Partial` and blocked on workbook-backed Collection position authority.
- PR [#737](https://github.com/markperezne8-spec/MarketDEX/pull/737) delivered the read-only Collection Position Projection authority card and removed table row-number chrome.
- Exact PR head: `b5c7c78304a67c224419be3f38499e68964c36d2`.
- CI [#1034](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31954583951) passed for that exact head.
- Merge commit: `dadadf0da7c197d784f986405b4e22e4284c22f3`.
- Visual acceptance passed from Mark's maximized Collection Overview screenshot.
- The authority card explicitly states `READ-ONLY`, `AUTHORITY GATE`, and `Product Registry + Inventory projection · no Collection writes`.
- No Collection persistence, CRUD, inference, valuation, lifecycle mutation, Inventory conversion, provider, network, export, automation, or business-state mutation authority was added.
- The CAP-006E synchronization is documentation-only and requires no new visual check.


## CAP-012 Reports post-PR #739 reconciliation

- CAP-012 remains `Partial`.
- PR [#739](https://github.com/markperezne8-spec/MarketDEX/pull/739) delivered the Inventory Age Patterns read-only visual preview panel using the existing Inventory Age query boundary.
- Exact PR #739 head: `8da4873f2f4a0c5f328eb1c6e5a53efa2654fce1`; CI [#1041](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32332846188) passed; squash merge commit: `6b9de6cbe9f2dcdd14b32506a2afe733db1f9a34`.
- The preview is catalog-only, deterministic, read-only, and fail-closed: missing Inventory detail evidence renders `Unavailable` rather than a fabricated age value.
- The accepted visual evidence confirms the Reports North Star navy/blue panel and card treatment, source context `inventory` / `purchase_date`, evidence wording, and no mutation authority.
- CAP-012 still authorizes only the three approved Reports business questions. A fourth report, expanded Purchase Source Performance execution, live cross-domain queries, charts, exports, persistence, automation, and mutation remain separately gated.
- CAP-006 remains `Partial` and blocked on workbook-backed Collection position authority; this reconciliation introduces no Collection runtime scope.

## CAP-006 current evidence after PR #738

- PR [#738](https://github.com/markperezne8-spec/MarketDEX/pull/738) reconciled the accepted PR #737 Collection visual authority evidence.
- CAP-006 remains a read-only Product Registry + Inventory projection with no Collection writes.
- Workbook-backed position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition authority remain unresolved and must be separately approved before runtime expansion.


## CAP-006 post-PR #741 reconciliation

- CAP-006 remains `Partial` and read-only.
- PR [#741](https://github.com/markperezne8-spec/MarketDEX/pull/741) delivered a compact empty-state panel for the Collection Overview.
- Exact PR #741 head: `7881cfbae8ee145b5c83b8383d70947cd6ea52ee`; CI [#1045](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32578607084) passed; squash merge commit: `88f11e9968ddbcd40beb1653f32d1525a81592dc`.
- The panel distinguishes no linked positions from an unmatched search and hides when populated results exist.
- The panel explains the existing Product Registry + Inventory projection and explicitly preserves the no-Collection-writes gate.
- Visual acceptance passed from the maximized Collection Overview screenshot.
- No Collection persistence, CRUD, lifecycle, schema, migration, condition/grade inference, collector intent, valuation, Inventory conversion, provider, networking, export, automation, or mutation authority was added.
- Workbook-backed position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition decisions remain blocked and must be approved before runtime expansion.

## CAP-012 post-PR #743 reconciliation

- CAP-012 remains `Partial`.
- PR [#743](https://github.com/markperezne8-spec/MarketDEX/pull/743) delivered a compact read-only empty-result panel for Purchase Source Performance.
- Exact PR #743 head: `988934ab4c21581a463866aadd19caed1c0e8af1`; CI [#1049](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32688317552) passed; squash merge commit: `1b9ca2577e7542b0c80bc4340c391da9ac526659`.
- The panel makes the zero-row result explicit for the selected period/as-of context and preserves the result's read-only, fail-closed evidence semantics.
- Accepted visual evidence confirms the Reports North Star navy/blue treatment, readable spacing, intact controls/table, and explicit `missing evidence is not converted to zero` wording.
- The build added no new report, source authority, query service, persistence, export, networking, automation, or mutation authority.
- CAP-006 remains `Partial` and blocked on workbook-backed Collection position authority; this reconciliation introduces no Collection scope.


## CAP-006 post-PR #745 reconciliation

- CAP-006 remains `Partial` and read-only.
- PR [#745](https://github.com/markperezne8-spec/MarketDEX/pull/745) delivered the field-authority panel stating that Condition / Grade and Collector Intent remain `Not recorded` until authority is approved.
- Exact PR #745 head: `a8e529fc082429535e889c8d3b6a098e08de594b`.
- CI [#1053](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32695854552) passed for that exact head.
- Squash merge commit: `3afe559292cac3d3b0f5f905d95b45d89bb9d01c`.
- Accepted visual evidence confirms the read-only Product Registry + Inventory projection and the no-Collection-writes boundary.
- Workbook-backed position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition authority remain unresolved.

## CAP-012 post-PR #746 reconciliation

- CAP-012 remains `Partial` and read-only.
- PR [#746](https://github.com/markperezne8-spec/MarketDEX/pull/746) delivered the Inventory Age evidence-gate panel.
- Exact PR #746 head: `4ff7bbc5c9b8319a7b9b13be82e5b2ad2ef6b652`.
- CI [#1055](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32698189459) passed for that exact head.
- Squash merge commit: `7a591bf7cdcb16454ec9d29eea463758133c2d5c`.
- Accepted visual evidence confirms `CATALOG-ONLY · UNAVAILABLE`, unavailable metrics, source context, no mutation authority, and the evidence-gate wording for missing/conflicting Inventory detail evidence.
- No new report, query, provider, persistence, export, networking, automation, or mutation authority was introduced.
- The approved report set remains Inventory Age Patterns, Inventory Turnover, and Purchase Source Performance. Any fourth report or expanded execution boundary requires separate workbook-backed approval.


## CAP-012 post-PR #748 reconciliation

- CAP-012 remains `Partial` and read-only.
- PR [#748](https://github.com/markperezne8-spec/MarketDEX/pull/748) delivered the `Approved report catalog` scope panel using the existing report count, catalog-only, and composition-owned query status text.
- Exact PR #748 head: `ffeffe750ceefd6cb6d6983e34c21800d4520f11`.
- CI [#1059](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32886676226) passed for that exact head.
- Squash merge commit: `97d9718123b677708adb76371a3d61bfe77de36e`.
- Accepted visual evidence confirms the three approved report cards, intact catalog table, preserved unavailable/conflicting semantics, and North Star styling.
- No new report definition, query, provider, persistence, export, networking, automation, or mutation authority was introduced.


## CAP-012 post-PR #750 reconciliation

- CAP-012 remains `Partial` and read-only.
- PR [#750](https://github.com/markperezne8-spec/MarketDEX/pull/750) delivered consistent `READ-ONLY PREVIEW` labels across Inventory Age Patterns, Inventory Turnover, and Purchase Source Performance.
- Exact PR #750 head: `caac9d1457b3189a560af5e21ba5df2f035dfd24`.
- CI [#1063](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32893850196) passed for that exact head across all nine required gates.
- Squash merge commit: `40cf9b7a6c65373519f2ba979cdc5728fa658c79`.
- Accepted visual evidence confirms all three labels, preserved metrics and empty-result semantics, intact controls, no clipping, and North Star styling.
- No new report definition, query, provider, persistence, export, networking, automation, or mutation authority was introduced.
- CAP-006 remains `Partial` and blocked on workbook-backed Collection position authority; this reconciliation introduces no Collection scope.


## CAP-012/CAP-006 post-PR #752 reconciliation

- PR [#752](https://github.com/markperezne8-spec/MarketDEX/pull/752) added focused regression coverage for the existing approved read-only boundary.
- Exact PR #752 head: `ceac91e5b623cc245c5d80b73d189332f6cb9dbd`.
- CI [#1068](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32937077082) passed all nine required jobs.
- Squash merge commit: `cc2ae18e5b1e67320791181dd3bcc3ee4334a4cb`.
- Changed files: `tests/test_build701ar_reports_workspace.py`, `tests/test_cap006_collection_position_workspace.py`.
- CAP-012 remains Partial/read-only with fail-closed unavailable/conflicting evidence semantics.
- CAP-006 remains Partial/read-only with no Collection writes and no inference of unrecorded classification fields.
- No new report, Collection, persistence, export, networking, automation, or mutation authority was introduced.
- Any runtime expansion remains separately gated by workbook-backed authority.


## Top-level baseline normalization after PR #753

- The derived capability baseline now points to current `main` at `5fe59155cee74b79406ab0c7e3356919a24a1d5c`.
- PR #753 is the current documentation reconciliation boundary for the merged CAP-012/CAP-006 read-only regression hardening.
- CAP-006 and CAP-012 remain Partial; no new authority or runtime expansion is implied.
