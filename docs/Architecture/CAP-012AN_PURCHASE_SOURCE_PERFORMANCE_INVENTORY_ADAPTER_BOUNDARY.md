# CAP-012AN — Purchase Source Performance Inventory Adapter Boundary

## Status and scope

This document is the architecture boundary for issue #677. It authorizes repository inspection and a future read-only adapter design only. It does not authorize an adapter implementation, composition, registration, UI, schema, migration, persistence, mutation, report catalog change, or live execution.

The only existing consumer seam is `PurchaseSourcePerformanceInventoryReader.read_purchase_source_performance_inventory` in `reports/purchase_source_performance_provider.py`. Its request is `PurchaseSourcePerformanceInventoryReadRequest(period_start, period_end, as_of)`; its response is `PurchaseSourcePerformanceInventoryRead`, containing either complete records or an `unavailable`/`conflicting` outcome. `PurchaseSourcePerformanceInventoryRecord` requires `inventory_id`, positive `acquired_units`, a `date` `acquisition_date`, and a non-blank `purchase_source_label` (same file, `PurchaseSourcePerformanceInventoryRecord.__post_init__`).

## Existing canonical Inventory authority

The canonical runtime Inventory authority is the `services`/`core` path used by `composition/application_composition.py`: `ApplicationComposition.__init__` constructs `InventoryAppService(self.database_path)`, and `InventoryAppService.__init__` creates the `DatabaseManager` and `InventoryRepository`. The adapter must not use the legacy `app/repositories/asset_repository.py` or its separate `app/models/asset.py` storage shape as a second authority.

The permanent canonical facts are split as follows:

| Required fact | Existing authority and exact symbol | Stored semantics |
| --- | --- | --- |
| Inventory identity and current quantity | `core/schema.py`, `CREATE TABLE inventory_authority`; `repositories/inventory_repository.py`, `InventoryRepository.get` and `InventoryRepository.apply` | `asset_id` is the primary key; `quantity` is the current non-negative balance. `InventoryRepository.apply` records deltas in `inventory_history` and updates the balance. |
| Asset existence/state | `core/schema.py`, `CREATE TABLE assets`; `services/inventory_app_service.py`, `InventoryAppService.get_asset_detail` | `assets.asset_id` is the canonical asset identity. The detail read inner-joins `inventory_authority` and returns `state`; it does not itself establish an acquisition event. |
| Acquisition events and quantity deltas | `services/inventory_service.py`, `InventoryService.apply_acquisition`; `repositories/inventory_repository.py`, `InventoryRepository.apply`; `core/schema.py`, `CREATE TABLE inventory_history` | `apply_acquisition` emits event type `ACQUISITION` and applies a positive quantity delta. `inventory_history` is append-only and records `quantity_delta`, resulting balance/cost, and `recorded_at`; it has no `purchase_source` or `purchase_date` column. |
| Purchase date/source fields | `core/schema.py`, `CREATE TABLE inventory_business_details`; `services/inventory_app_service.py`, `InventoryAppService.get_asset_detail` and `InventoryAppService.update_business_details` | `purchase_date` and `purchase_source` are `TEXT NOT NULL DEFAULT ''`, are optional at read time through `LEFT JOIN` + `COALESCE`, and are normalized only by surrounding-whitespace trimming on update. The date is not parsed or validated by this service. |

`InventoryAppService.get_asset_detail` is the existing read path that returns all four requested values in one record (`asset_id`, `quantity`, `purchase_date`, `purchase_source`). It is therefore the narrowest existing application read seam to reuse if, and only if, the adapter treats the returned values according to their actual semantics. It is not permission to reinterpret `quantity` as an acquisition quantity or `purchase_date` as an immutable event date.

## Confirmed gaps and fail-closed consequences

The current repository does not expose a complete canonical acquisition record with all four required fields:

1. `inventory_authority.quantity` is a current balance. It can be changed by acquisition, sale, return, reconciliation, transformation, or adjustment through `InventoryRepository.apply` and related services. It is not the amount originally acquired.
2. `inventory_history` can prove quantity movement and event time, but it does not carry `purchase_source` or `purchase_date`, and its rows are not sufficient to associate a source/date with one acquisition without inference.
3. `inventory_business_details.purchase_date` and `.purchase_source` are optional mutable metadata. `update_business_details` can change them independently of the acquisition event and accepts any trimmed string for `purchase_date`; blank values are valid storage values.
4. `InventoryAppService.get_asset_detail` uses `COALESCE(..., '')`, so a missing detail row and an explicitly blank field both become unavailable evidence. That is safe only if the adapter reports the field as unavailable rather than inventing a value.
5. The older `app` storage path has a different `Asset`/`AssetRepository` shape and nullable text fields. Mixing it with the canonical `core` schema would create duplicate authority and is prohibited.

Accordingly, the adapter must fail closed as `unavailable` when any requested record lacks a non-blank source, lacks a strict ISO `YYYY-MM-DD` date that parses to a `date`, or cannot establish that the quantity is an authoritative acquired quantity. It must return `conflicting` when duplicate canonical identity, contradictory rows, out-of-bound dates, non-positive quantities, malformed typed values, or incompatible coverage are observed. It must never use current balance, `created_at`, `verified_at`, `recorded_at`, asset name, cost, or a source label as a substitute for missing acquisition authority.

## Smallest safe adapter boundary

The next implementation slice is one read-only adapter class in the report/application boundary, constructor-injected with the existing Inventory read authority. The dependency must be a narrow protocol or callable that can read the canonical Inventory acquisition projection; it must not construct a database, open a second repository, write through `InventoryAppService`, or depend on UI state. The adapter translates the immutable `PurchaseSourcePerformanceInventoryReadRequest` into the canonical read request and maps only verified canonical fields into `PurchaseSourcePerformanceInventoryRecord` values.

The boundary contract is:

- request period is `[period_start, period_end)`; `as_of` is an inclusive evidence ceiling and must not precede `period_start`;
- source coverage must be complete for the requested canonical Inventory population; partial rows are not silently dropped;
- identity is canonical `assets.asset_id` / `inventory_authority.asset_id`, with no inferred joins;
- `acquired_units` must come from a future explicit acquisition projection, not `inventory_authority.quantity` unless a separately reviewed authority proves that equivalence;
- `acquisition_date` must come from a future explicit acquisition-date authority with strict ISO parsing; neither `inventory_history.recorded_at` nor metadata `purchase_date` may be silently substituted;
- `purchase_source_label` is the exact trimmed non-blank Inventory source label; case folding is for ordering only, never grouping or aliasing;
- output records are unique by canonical `inventory_id`, ordered by `(acquisition_date, inventory_id, purchase_source_label.casefold(), purchase_source_label)`; database row order is not observable;
- successful empty complete coverage may return `PurchaseSourcePerformanceInventoryRead('available', ())`;
- missing/blank/malformed/incomplete source/date/quantity evidence returns unavailable; contradictory or duplicate evidence returns conflicting; neither outcome exposes records.

The adapter may read through `InventoryAppService.get_asset_detail` only for facts that method actually owns and returns. Given the current schema, that method alone cannot produce a valid `PurchaseSourcePerformanceInventoryRecord`; the safe next slice is therefore adapter contract tests plus an explicit, separately approved acquisition projection/read authority if implementation requires it. No schema or persistence change is part of this issue.

## Provenance and diagnostics

An available read must identify the source domain as `inventory`, preserve the requested period/as-of boundary, and provide deterministic provenance naming the canonical read authority and fields used. An unavailable or conflicting read must preserve a stable reason such as `inventory_acquisition_quantity_unavailable`, `purchase_date_missing`, `purchase_date_invalid_iso`, `purchase_source_missing`, `duplicate_canonical_inventory_identity`, or `inventory_acquisition_coverage_conflict`. The adapter must not downgrade a detected conflict to an empty successful read.

`PurchaseSourcePerformanceProvider` in `reports/purchase_source_performance_provider.py` already fails closed for adapter exceptions, unsupported response types, non-available Inventory outcomes, duplicate identities, and out-of-period records. The adapter must honor that protocol; it must not implement sale joins, formula calculation, application composition, or provider registration. The provider remains responsible for passing canonical Inventory identities to `SaleCompletionQueryService` and for aggregating report evidence.

## Explicit non-goals and follow-up

This boundary does not change `core/schema.py`, `services/inventory_service.py`, `services/inventory_app_service.py`, `repositories/inventory_repository.py`, `composition/application_composition.py`, or any UI/report catalog. It does not add a second Inventory authority, derive acquired units from balances, infer dates from event timestamps, persist snapshots, or mutate Inventory.

The smallest safe follow-up after this document is reviewed is a focused, read-only adapter/projection contract that exposes an explicit canonical acquisition record and tests complete, unavailable, conflicting, malformed, duplicate, boundary-date, deterministic-ordering, provenance, and zero-write behavior. Runtime composition and registration require a separate issue and approval.
