# MarketDEX OS Repository Reconciliation

**Status:** Active baseline
**Authority:** Repository evidence on `main`
**Owner:** Lead Software Architect
**Update trigger:** Permanent architecture or capability evidence changes

## Baseline

Reconciliation began after EC-001 and PR #121. Repository evidence, CI gates, merged pull-request history, schema authority, and existing traceability records are re-verified at each controlled delivery boundary. This reconciliation is current through PR #554 and the merged Build 701 Reports sequence.

## Permanent Runtime Authority

The canonical desktop entry point is root `launcher.py`. It creates the runtime SQLite path at `runtime/marketdex.sqlite3`, invokes legacy database migration, constructs the application composition, creates `MainWindow`, installs the inventory/pricing/listing/sale-completion feature chain, mounts canonical workspaces, and opens at a practical screen-bounded size.

The root launcher is permanent runtime authority. A nested or competing launcher must not be introduced.

## Persistence Authority

`core/schema.py` remains the single SQLite schema authority. Settlement evidence, canonical linkage, allocation evidence, cross-checks, revisions, and locks extend that single authority through controlled schema versions.

Existing marketplace allocation and publication lifecycle tables remain inventory/publication authorities. They are not reclassified as settlement allocation evidence.

Immutable and append-only triggers protect event identity, inventory history, publication lifecycle, replay defense, audit events, Settlement Evidence, Settlement Allocation Evidence, settlement execution/history, and order closure/history.

## Verified CI Topology

The permanent CI topology contains nine required gates:

- Core Tests
- Collection
- Market Intelligence
- Reports
- Inventory
- Pricing
- Listing
- Mission Control Visual Slice
- Desktop Build

Desktop Build compiles and packages the permanent root runtime, verifies composition and workspace contracts, builds the installer, and verifies the installed runtime. Core Tests protect runtime database authority and authority-heavy settlement contracts. The dedicated Reports gate directly exercises the Build 701 definition, Inventory Age projection/provider/query/request chain, source-authority boundaries, and read-only report contracts.

## Capability Evidence Summary

### Mature permanent runtime capabilities

Inventory has service, application service, repository, schema, UI feature, and focused CI evidence. Pricing/profit guidance and the listing-to-sale-completion workflow are integrated into the root launcher and have focused CI gates. Runtime database authority, audit/history controls, and the desktop shell are also directly protected.

CAP-008 through CAP-011 now preserve the workbook settlement and settlement-allocation authority sequence through Builds 481-503, plus the Build 504 fail-closed authority audit repairs. CAP-008A established sale-independent Settlement Evidence. CAP-008B established canonical linkage. CAP-008C repaired Build 484 pending-allocation semantics. CAP-008D delivered the Builds 487-497 read-only settlement verification authority chain. CAP-009 through CAP-011 preserve allocation evidence, cross-check, readiness, lifecycle, revision, lock, and audit authority.

### Delivered product-registry vertical slice

CAP-005 is Complete for `REQ-PROD-001`. CAP-005A established Product Registry persistence, CAP-005B established inventory-to-product linkage, and CAP-005C established deterministic read-only operator lookup and the canonical Product Registry workspace. Searches by Product ID, canonical name, alias, set, card number, variant, and product type are zero-mutation reads over the existing SQLite authority.

### Delivered Collection read-only slice

PR #175 introduced the provisional CAP-006 Collection Position query surface through `services/collection_position_service.py`, `ui/collection_position_workspace.py`, canonical application composition, workspace registration, and focused projection/workspace/navigation tests.

The delivered contract is intentionally limited to canonical Product Registry identity plus linked Inventory quantity, location, and acquisition evidence. Condition, grade, collector intent, valuation, and Collection lifecycle facts remain absent and must not be inferred.

`docs/Architecture/CAP-006B_COLLECTION_WRITE_AUTHORITY_GATE.md` records the controlling authority boundary. CAP-006 remains `Partial`; no Collection persistence, CRUD, lifecycle command, automatic Inventory conversion, or speculative business vocabulary is authorized.

### Delivered Reports read-only slice

Build 701 introduced the canonical CAP-012 Reports foundation through `reports/definitions.py`, Inventory Age source/provider/query/request contracts, `reports/report_query_service.py`, root application composition, workspace registration, and `ui/reports_workspace.py`.

The delivered contract contains one approved report: `inventory-age-patterns`. It is catalog-only, offline, deterministic, composition-owned, and read-only. Result presentation preserves outcome, reason, inventory position, as-of date, source domain, source date, source field, evidence state, and explicit unavailable/non-found semantics without creating duplicate persistence or business authority.

The dedicated Reports CI gate and Desktop Build composition tests protect the current extension point. CAP-012 is `Partial`, not `Missing` and not `Complete`; additional report definitions, cross-domain reconciliation, charts, exports, providers, persistence, and expanded analytics require separately approved workbook-backed boundaries.

### Existing work that must be extended, not rebuilt

Mission Control/dashboard code exists in multiple repository surfaces, including root services and `app/` UI/service components. Product Registry service logic and product-aware lifecycle logic exist. Marketplace allocation and publication lifecycle infrastructure also exist.

The read-only Collection Position service/workspace and the composition-owned Reports catalog/query/workspace are permanent extension points. Later builds must extend those surfaces through the existing application composition, runtime database, source-domain authority separation, and audit architecture rather than introducing parallel replacements.

### Remaining repository-backed capability gaps

The Capability Matrix identifies Collection and Reports as `Partial`. Collection Position remains incomplete as an ownership model until its workbook-backed position grain, field vocabulary, evidence ownership, transition rules, and archive semantics are accepted.

Reports has one verified Inventory Age report but no authorization to infer the next report from roadmap memory. The next Reports slice must begin with one approved workbook-backed business question, explicit source-domain authority, deterministic query/read-model contracts, and scoped verification. No chart, export, provider, persistence, cross-domain total, or automation follows by assumption.

## Reconciliation Result

CAP-008 / Builds 481-497 parity is `Complete` after PR #148, CAP-005 Product Registry is `Complete` after PR #171, and CAP-006 has a provisional read-only slice after PR #175 with its mutation boundary locked by PR #178.

CAP-012 is reconciled from `Missing` to `Partial` based on the merged Build 701 sequence through PR #359: immutable definitions, composition-owned query execution, canonical workspace presentation, provenance-visible Inventory Age results, dedicated Reports CI, and accepted visual evidence are present on `main`.

The next implementation build must be separately approved and must not derive authority from placeholder UI, roadmap language, stale capability classification, or this reconciliation record alone.

## Known Reconciliation Debt

The repository contains older and overlapping documentation locations and multiple `app/` versus root service/UI surfaces. EC-001 prohibits cleanup by assumption. These are evidence for later technical-debt classification, not permission to delete or restructure during capability delivery.