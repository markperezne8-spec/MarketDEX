# MarketDEX OS Repository Reconciliation

**Status:** Active baseline
**Authority:** Repository evidence on `main`
**Owner:** Lead Software Architect
**Update trigger:** Permanent architecture or capability evidence changes

## Baseline

Reconciliation began after EC-001 and PR #121. Repository evidence, CI gates, merged pull-request history, schema authority, and existing traceability records are re-verified at each controlled delivery boundary. This reconciliation is current through PR #755 and the accepted Visual North Star shell header evidence sequence.

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

The delivered contract contains three approved report definitions, with Inventory Age and Inventory Turnover previews plus the merged Purchase Source Performance read-only preview. PR #718 added the composition-owned immutable Purchase Source Performance snapshot and preserved the read-only Reports workspace; PR #720 reconciled CAP-012AN with the delivered canonical acquisition projection and adapter boundary. PR #725 exposed the composition-owned `ApplicationComposition.query_purchase_source_performance` read-only query seam through the canonical Reports query service. Reports remain deterministic, composition-owned, and read-only; the preview remains explicitly unavailable when no snapshot is supplied. PR #743 adds a zero-row Purchase Source Performance empty-result panel with period/as-of context while preserving the empty table and explicit no-fabricated-zero semantics. PR #746 adds the Inventory Age evidence-gate panel while preserving catalog-only, unavailable, source-context, and no-mutation semantics. PR #748 adds the Reports catalog scope panel while preserving the existing approved-count, catalog-only, and composition-owned boundary. Result presentation preserves outcome, reason, inventory position, as-of date, source domain, source date, source field, evidence state, and explicit unavailable/non-found semantics without creating duplicate persistence or business authority.

The dedicated Reports CI gate and Desktop Build composition tests protect the current extension point. CAP-012 is `Partial`, not `Missing` and not `Complete`; additional report definitions, cross-domain reconciliation, charts, exports, providers, persistence, and expanded analytics require separately approved workbook-backed boundaries.

### Existing work that must be extended, not rebuilt

Mission Control/dashboard code exists in multiple repository surfaces, including root services and `app/` UI/service components. Product Registry service logic and product-aware lifecycle logic exist. Marketplace allocation and publication lifecycle infrastructure also exist.

The read-only Collection Position service/workspace and the composition-owned Reports catalog/query/workspace are permanent extension points. Later builds must extend those surfaces through the existing application composition, runtime database, source-domain authority separation, and audit architecture rather than introducing parallel replacements.

### Remaining repository-backed capability gaps

The Capability Matrix identifies Collection and Reports as `Partial`. Collection Position remains incomplete as an ownership model until its workbook-backed position grain, field vocabulary, evidence ownership, transition rules, and archive semantics are accepted.

Reports has a verified Inventory Age report and a composition-owned Purchase Source Performance read-only preview. The next Reports slice must begin with one approved workbook-backed boundary, explicit source-domain authority, deterministic query/read-model contracts, and scoped verification. The delivered acquisition projection and adapter do not authorize live provider execution, new queries, charts, exports, persistence, cross-domain totals, or automation.

## Reconciliation Result

CAP-008 / Builds 481-497 parity is `Complete` after PR #148, CAP-005 Product Registry is `Complete` after PR #171, and CAP-006 has a provisional read-only slice after PR #175 with its mutation boundary locked by PR #178.

CAP-012 is reconciled from `Missing` to `Partial` based on the merged Build 701 sequence through PR #359 and the later Purchase Source Performance, Inventory Age, and Reports catalog visual sequence through PR #748: immutable definitions, composition-owned query execution, canonical workspace presentation, provenance-visible Inventory Age results, the delivered acquisition projection/adapter boundary, dedicated Reports CI, accepted visual evidence, and Purchase Source Performance empty-result clarity are present on `main`.

The next implementation build must be separately approved and must not derive authority from placeholder UI, roadmap language, stale capability classification, or this reconciliation record alone.

## Known Reconciliation Debt

The repository contains older and overlapping documentation locations and multiple `app/` versus root service/UI surfaces. EC-001 prohibits cleanup by assumption. These are evidence for later technical-debt classification, not permission to delete or restructure during capability delivery.

### CAP-012 post-PR #743 evidence

- PR [#743](https://github.com/markperezne8-spec/MarketDEX/pull/743) added the Purchase Source Performance zero-row visual clarity panel.
- Exact PR #743 head: `988934ab4c21581a463866aadd19caed1c0e8af1`.
- CI [#1049](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32688317552) passed for that exact head.
- Squash merge commit: `1b9ca2577e7542b0c80bc4340c391da9ac526659`.
- Mark accepted the maximized Reports screenshot showing the period/as-of context, read-only controls, empty table, and explicit missing-evidence semantics.
- CAP-012 remains `Partial`; the build introduces no additional report authority, query service, persistence, export, networking, automation, or mutation.


### CAP-006 post-PR #745 field-authority evidence

- PR [#745](https://github.com/markperezne8-spec/MarketDEX/pull/745) delivered the read-only Collection field-authority panel.
- Exact PR #745 head: `a8e529fc082429535e889c8d3b6a098e08de594b`.
- CI [#1053](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32695854552) passed for that exact head.
- Squash merge commit: `3afe559292cac3d3b0f5f905d95b45d89bb9d01c`.
- Accepted visual evidence shows `Unrecorded Collection fields` and preserves `Not recorded` semantics until authority is approved.
- CAP-006 remains `Partial`, read-only, and blocked on workbook-backed position authority. No Collection write authority was introduced.

### CAP-012 post-PR #746 Inventory Age evidence-gate evidence

- PR [#746](https://github.com/markperezne8-spec/MarketDEX/pull/746) delivered the read-only Inventory Age evidence-gate panel.
- Exact PR #746 head: `4ff7bbc5c9b8319a7b9b13be82e5b2ad2ef6b652`.
- CI [#1055](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32698189459) passed for that exact head.
- Squash merge commit: `7a591bf7cdcb16454ec9d29eea463758133c2d5c`.
- Accepted visual evidence shows `Inventory Age evidence gate`, `CATALOG-ONLY · UNAVAILABLE`, unavailable metrics, source context, and explicit missing/conflicting-evidence wording.
- CAP-012 remains `Partial`, read-only, composition-owned, and fail-closed. No new report, query, provider, persistence, export, networking, automation, or mutation authority was introduced.


### CAP-012 post-PR #748 catalog scope evidence

- PR [#748](https://github.com/markperezne8-spec/MarketDEX/pull/748) delivered the compact read-only `Approved report catalog` scope panel.
- Exact PR #748 head: `ffeffe750ceefd6cb6d6983e34c21800d4520f11`.
- CI [#1059](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32886676226) passed for that exact head.
- Squash merge commit: `97d9718123b677708adb76371a3d61bfe77de36e`.
- Accepted visual evidence confirms the approved report count, catalog-only behavior, composition-owned query execution, three approved report cards, intact catalog table, and North Star alignment.
- CAP-012 remains `Partial` and read-only. No new report, query, provider, persistence, export, networking, automation, or mutation authority was introduced.


### CAP-012 post-PR #750 read-only preview state evidence

- PR [#750](https://github.com/markperezne8-spec/MarketDEX/pull/750) delivered consistent `READ-ONLY PREVIEW` labels for the three existing Reports preview panels.
- Exact PR #750 head: `caac9d1457b3189a560af5e21ba5df2f035dfd24`.
- CI [#1063](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32893850196) passed for that exact head across all nine required gates.
- Squash merge commit: `40cf9b7a6c65373519f2ba979cdc5728fa658c79`.
- Accepted maximized Reports screenshots confirm the Inventory Age Patterns, Inventory Turnover, and Purchase Source Performance labels, preserved read-only evidence semantics, intact controls, no clipping, and North Star styling.
- CAP-012 remains `Partial`, read-only, composition-owned, and fail-closed. No new report, query, provider, persistence, export, networking, automation, or mutation authority was introduced.


## CAP-012/CAP-006 PR #752 reconciliation

- PR [#752](https://github.com/markperezne8-spec/MarketDEX/pull/752) delivered test-only regression hardening for the existing CAP-012 Reports and CAP-006 Collection read-only boundaries.
- Exact PR #752 head: `ceac91e5b623cc245c5d80b73d189332f6cb9dbd`; CI [#1068](https://github.com/markperezne8-spec/MarketDEX/actions/runs/32937077082) passed all nine required jobs.
- Squash merge commit: `cc2ae18e5b1e67320791181dd3bcc3ee4334a4cb`.
- The two-file scope preserves non-editable Reports actions, fail-closed unavailable/conflicting semantics, Collection refresh-only behavior, and unrecorded classification fields.
- No runtime, UI, workbook, provider, persistence, export, networking, automation, or mutation authority was added.


## Top-level baseline normalization after PR #753

- Repository reconciliation now points to current `main` at `5fe59155cee74b79406ab0c7e3356919a24a1d5c`.
- PR #753 is the current documentation boundary after PR #752 test-only regression hardening.
- CAP-006 and CAP-012 remain read-only and separately gated for any workbook-backed authority expansion.


## Visual North Star shell header evidence after PR #755

- PR [#755](https://github.com/markperezne8-spec/MarketDEX/pull/755) delivered the branded command-center header in the canonical WorkspaceHost.
- Exact PR #755 head: `c46bc244d3d28efe568114302264e09a5c1db82c`; CI [#1074](https://github.com/markperezne8-spec/MarketDEX/actions/runs/33030902498) passed all nine required jobs.
- Squash merge commit: `b6d40ab7f75dcb445dbff5ca286754b9e855c46c`.
- Accepted visual evidence confirms MarketDEX OS branding, COMMAND CENTER context, LOCAL AUTHORITY, OFFLINE FIRST, persistent navigation, and no clipping or overlap.
- The three-file presentation-only scope preserved the launcher, composition root, workspace registry, services, data, commands, workspace IDs, and read-only capability boundaries.
- CAP-006 and CAP-012 remain separately gated for workbook-backed authority expansion.


## Visual North Star navigation evidence after PR #757

- This reconciliation is current through PR [#757](https://github.com/markperezne8-spec/MarketDEX/pull/757) and the accepted Mission Control visual evidence.
- Exact PR #757 head: `30d08d2aad7864af574d650678dfd3c8293fcf80`; CI [#1079](https://github.com/markperezne8-spec/MarketDEX/actions/runs/33036161560) passed all nine required jobs.
- Squash merge/current `main`: `806c11693e416ed5f93f039682f15d80cce503e3`.
- The delivered presentation-only change groups existing navigation as OPERATIONS, COLLECTION, and INTELLIGENCE and applies semantic accent colors without changing workspace identity, routing, activation, services, data, commands, launcher, composition root, or authority.
- Visual acceptance passed on a maximized Mission Control screenshot with no clipping or overlap.
- CAP-006 remains Partial/read-only and blocked on workbook-backed Collection position authority.
- CAP-012 remains Partial/read-only and blocked from expanded report authority or execution without a separately approved workbook-backed boundary.
- Issue [#758](https://github.com/markperezne8-spec/MarketDEX/issues/758) records this documentation-only reconciliation; no visual check is required.


## Visual North Star dashboard-panel evidence after PR #759

- Repository reconciliation is current through PR [#759](https://github.com/markperezne8-spec/MarketDEX/pull/759) and the accepted Mission Control visual evidence.
- Exact PR #759 head: `c2ab9f04f46aff998680d35edea8666f2b3e28ce`; CI [#1083](https://github.com/markperezne8-spec/MarketDEX/actions/runs/33037632359) passed all nine required jobs.
- Squash merge/current `main`: `ea7f993a7164d8ac897619a77e854462c7230615`.
- The presentation-only change adds semantic left-edge accents to reusable dashboard panels while preserving content, data, workspace identity, routing, activation, services, launcher, composition root, and authority.
- Visual acceptance passed on a maximized Mission Control screenshot with no clipping or overlap.
- CAP-006 remains Partial/read-only and blocked on workbook-backed Collection position authority.
- CAP-012 remains Partial/read-only and blocked from expanded report authority or execution without a separately approved workbook-backed boundary.
- Issue [#760](https://github.com/markperezne8-spec/MarketDEX/issues/760) records this documentation-only reconciliation; no visual check is required.
