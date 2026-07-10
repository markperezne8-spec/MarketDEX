# MarketDEX OS Repository Reconciliation

**Status:** Active baseline
**Authority:** Repository evidence on `main`
**Owner:** Lead Software Architect
**Update trigger:** Permanent architecture or capability evidence changes

## Baseline

Reconciliation performed after EC-001 and PR #121. Repository evidence, current CI gates, merged pull-request history, schema authority, and existing traceability records were inspected before capability classification.

## Permanent Runtime Authority

The canonical desktop entry point is root `launcher.py`. It creates the runtime SQLite path at `runtime/marketdex.sqlite3`, invokes legacy database migration, constructs `MissionControlService` and `InventoryAppService`, creates `MainWindow`, installs the inventory/pricing/listing/sale-completion feature chain, and launches maximized.

The root launcher is permanent runtime authority. A nested or competing launcher must not be introduced.

## Persistence Authority

`core/schema.py` is at schema version 17 and defines the current SQLite business persistence surface. Evidence includes event identity, audit history, assets, inventory authority and business details, listing plans and package reviews, inventory history and movements, controlled damage/loss adjustments, sales and financial history, replay defense, audit events, marketplace allocations, publication allocations and lifecycle events, exception authority, inventory reconciliation, settlement executions and history, and order closures and history.

Immutable and append-only triggers protect event identity, inventory history, publication lifecycle, replay defense, audit events, settlement execution/history, and order closure/history.

## Verified CI Topology

The current permanent CI topology contains five successful gates on the PR #121 head:

- Inventory
- Pricing
- Listing
- Desktop Build
- Core Tests

The Desktop Build gate compiles root `launcher.py` and runs workspace navigation and maximized-launch contracts. Core Tests verify runtime database authority. The remaining gates execute focused capability regression suites.

## Capability Evidence Summary

### Mature permanent runtime capabilities

Inventory has service, application service, repository, schema, UI feature, and focused CI evidence. Pricing/profit guidance and the listing-to-sale-completion workflow are integrated into the root launcher and have focused CI gates. Runtime database authority, audit/history controls, and the desktop shell are also directly protected.

### Existing work that must be extended, not rebuilt

Mission Control/dashboard code exists in multiple repository surfaces, including root services and `app/` UI/service components. Product Registry service logic and product-aware lifecycle logic exist. Settlement service/repository and settlement persistence exist. Marketplace allocation and publication lifecycle infrastructure also exist.

These areas are classified as `Partial` where workbook parity or canonical operator integration is not yet directly proven. Their existing implementation must be reconciled and extended rather than replaced.

### Workbook-to-desktop authority gap

The accepted workbook evolved settlement authority through Builds 481-497 and settlement allocation authority through Builds 498-503. Recent workbook contracts explicitly define allocation evidence intake, group cross-check and remainder handling, sale-level attribution readiness, lifecycle transitions, evidence revision/supersession, and evidence lock/audit preservation.

Repository search found settlement execution and marketplace allocation infrastructure, but did not find direct desktop implementation evidence for the Build 498-503 settlement-allocation evidence model, revision model, or lock contract. Existing marketplace allocation must not be assumed equivalent to settlement allocation evidence.

## Reconciliation Result

The repository is substantially more mature than the desktop foundation planning record suggested. Inventory, Pricing, Listing, runtime database authority, audit/history, and shell/navigation are existing permanent capabilities. Collection and Reports lack verified permanent root vertical slices. Product Registry and Mission Control require canonical integration reconciliation. Settlement is partial relative to the latest workbook authority.

The highest-value incomplete capability is CAP-009, Settlement allocation evidence and cross-check. Its first boundary is a Build 498-500 contract gap audit against existing schema, services, repositories, UI, and tests. No implementation should begin until that audit identifies reusable components and the exact missing authority surface.

## Known Reconciliation Debt

The repository contains older and overlapping documentation locations and multiple `app/` versus root service/UI surfaces. EC-001 prohibits cleanup by assumption. These are evidence for later technical-debt classification, not permission to delete or restructure during capability delivery.
