# MarketDEX OS Repository Reconciliation

**Status:** Active baseline
**Authority:** Repository evidence on `main`
**Owner:** Lead Software Architect
**Update trigger:** Permanent architecture or capability evidence changes

## Baseline

Reconciliation began after EC-001 and PR #121. Repository evidence, CI gates, merged pull-request history, schema authority, and existing traceability records are re-verified at each controlled delivery boundary.

## Permanent Runtime Authority

The canonical desktop entry point is root `launcher.py`. It creates the runtime SQLite path at `runtime/marketdex.sqlite3`, invokes legacy database migration, constructs the application composition, creates `MainWindow`, installs the inventory/pricing/listing/sale-completion feature chain, mounts canonical workspaces, and opens at a practical screen-bounded size.

The root launcher is permanent runtime authority. A nested or competing launcher must not be introduced.

## Persistence Authority

`core/schema.py` remains the single SQLite schema authority. Settlement evidence, canonical linkage, allocation evidence, cross-checks, revisions, and locks extend that single authority through controlled schema versions.

Existing marketplace allocation and publication lifecycle tables remain inventory/publication authorities. They are not reclassified as settlement allocation evidence.

Immutable and append-only triggers protect event identity, inventory history, publication lifecycle, replay defense, audit events, Settlement Evidence, Settlement Allocation Evidence, settlement execution/history, and order closure/history.

## Verified CI Topology

The permanent CI topology contains five gates:

- Inventory
- Pricing
- Listing
- Desktop Build
- Core Tests

Desktop Build compiles root `launcher.py` and runs workspace navigation and maximized-launch contracts. Core Tests verify runtime database authority and directly gate CAP-008 settlement evidence/linkage/verification authority, CAP-009 settlement allocation authority, CAP-010 revisions, CAP-011 locks, and M39A settlement regression behavior.

## Capability Evidence Summary

### Mature permanent runtime capabilities

Inventory has service, application service, repository, schema, UI feature, and focused CI evidence. Pricing/profit guidance and the listing-to-sale-completion workflow are integrated into the root launcher and have focused CI gates. Runtime database authority, audit/history controls, and the desktop shell are also directly protected.

CAP-008 through CAP-011 now preserve the workbook settlement and settlement-allocation authority sequence through Builds 481-503, plus the Build 504 fail-closed authority audit repairs. CAP-008A established sale-independent Settlement Evidence. CAP-008B established canonical linkage. CAP-008C repaired Build 484 pending-allocation semantics. CAP-008D delivered the Builds 487-497 read-only settlement verification authority chain. CAP-009 through CAP-011 preserve allocation evidence, cross-check, readiness, lifecycle, revision, lock, and audit authority.

### Delivered product-registry vertical slice

CAP-005 is Complete for `REQ-PROD-001`. CAP-005A established Product Registry persistence, CAP-005B established inventory-to-product linkage, and CAP-005C established deterministic read-only operator lookup and the canonical Product Registry workspace. Searches by Product ID, canonical name, alias, set, card number, variant, and product type are zero-mutation reads over the existing SQLite authority.

### Existing work that must be extended, not rebuilt

Mission Control/dashboard code exists in multiple repository surfaces, including root services and `app/` UI/service components. Product Registry service logic and product-aware lifecycle logic exist. Marketplace allocation and publication lifecycle infrastructure also exist.

### Remaining repository-backed capability gaps

The Capability Matrix identifies Collection and Reports as Missing. Collection is next because Collection Position is the remaining ownership model needed before portfolio or reporting read models can be authoritative. No capability may be selected from roadmap memory alone.

## Reconciliation Result

CAP-008 / Builds 481-497 parity is `Complete` after PR #148, and CAP-005 Product Registry is `Complete` after PR #171. The next controlled action is CAP-006 Collection pre-build classification: establish the workbook-backed Collection Position and ownership boundary before any Collection persistence or workspace implementation.

## Known Reconciliation Debt

The repository contains older and overlapping documentation locations and multiple `app/` versus root service/UI surfaces. EC-001 prohibits cleanup by assumption. These are evidence for later technical-debt classification, not permission to delete or restructure during capability delivery.
