# MarketDEX OS Repository Reconciliation

**Status:** Active baseline
**Authority:** Repository evidence on `main`
**Owner:** Lead Software Architect
**Update trigger:** Permanent architecture or capability evidence changes

## Baseline

Reconciliation began after EC-001 and PR #121. Repository evidence, CI gates, merged pull-request history, schema authority, and existing traceability records are re-verified at each controlled delivery boundary.

## Permanent Runtime Authority

The canonical desktop entry point is root `launcher.py`. It creates the runtime SQLite path at `runtime/marketdex.sqlite3`, invokes legacy database migration, constructs `MissionControlService` and `InventoryAppService`, creates `MainWindow`, installs the inventory/pricing/listing/sale-completion feature chain, and launches maximized.

The root launcher is permanent runtime authority. A nested or competing launcher must not be introduced.

## Persistence Authority

`core/schema.py` remains the single SQLite schema authority. CAP-008A introduced schema version 18 and the append-only `settlement_evidence` parent grain. CAP-009A advances the controlled delivery branch to schema version 19 with append-only `settlement_allocation_evidence` intake persistence against that canonical parent.

Existing marketplace allocation and publication lifecycle tables remain inventory/publication authorities. They are not reclassified as settlement allocation evidence.

Immutable and append-only triggers protect event identity, inventory history, publication lifecycle, replay defense, audit events, Settlement Evidence, Settlement Allocation Evidence, settlement execution/history, and order closure/history.

## Verified CI Topology

The permanent CI topology contains five gates:

- Inventory
- Pricing
- Listing
- Desktop Build
- Core Tests

Desktop Build compiles root `launcher.py` and runs workspace navigation and maximized-launch contracts. Core Tests verify runtime database authority and now directly gate CAP-008A Settlement Evidence, CAP-009A Build 498 Settlement Allocation Evidence, and M39A settlement regression behavior.

## Capability Evidence Summary

### Mature permanent runtime capabilities

Inventory has service, application service, repository, schema, UI feature, and focused CI evidence. Pricing/profit guidance and the listing-to-sale-completion workflow are integrated into the root launcher and have focused CI gates. Runtime database authority, audit/history controls, and the desktop shell are also directly protected.

### Existing work that must be extended, not rebuilt

Mission Control/dashboard code exists in multiple repository surfaces, including root services and `app/` UI/service components. Product Registry service logic and product-aware lifecycle logic exist. Settlement service/repository and settlement persistence exist. Marketplace allocation and publication lifecycle infrastructure also exist.

CAP-008A established a sale-independent Settlement Evidence parent. CAP-009A extends that authority with a distinct Build 498 settlement-allocation evidence intake repository/service/schema slice. No second allocation architecture was created; marketplace inventory allocation remains separate and preserved.

### Remaining workbook-to-desktop authority gap

The accepted workbook evolved settlement authority through Builds 481-497 and settlement allocation authority through Builds 498-503. CAP-009A addresses Build 498 intake persistence and fail-closed status derivation. Build 499 allocation group cross-check/remainder, Build 500 sale-level attribution readiness, Build 502 evidence revision/supersession, and Build 503 lock/audit preservation remain incomplete.

## Reconciliation Result

CAP-009 remains `Partial`. The exact next missing vertical slice after CAP-009A merge verification is Build 499 Allocation Group Cross-Check and Allocation Remainder authority, extending the canonical `settlement_allocation_evidence` grain. Build 500 remains a later controlled boundary.

## Known Reconciliation Debt

The repository contains older and overlapping documentation locations and multiple `app/` versus root service/UI surfaces. EC-001 prohibits cleanup by assumption. These are evidence for later technical-debt classification, not permission to delete or restructure during capability delivery.
