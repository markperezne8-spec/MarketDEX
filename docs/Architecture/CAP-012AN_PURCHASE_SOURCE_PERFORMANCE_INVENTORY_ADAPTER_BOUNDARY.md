# CAP-012AN — Purchase Source Performance Inventory Adapter Boundary

## Status and scope

This document records the delivered read-only acquisition projection and Purchase Source Performance inventory adapter boundary for issue #677. The canonical projection repository, adapter, and composition-owned snapshot are now present on main; this document preserves their fail-closed limits. It does not authorize schema expansion, mutation, a second Inventory authority, or speculative live execution.

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

The canonical acquisition evidence table and projection reader now expose the required acquisition grain through core.inventory_acquisition_projection and core.sqlite_inventory_acquisition_projection_repository. The projection reader validates identity, positive acquired units, strict acquisition dates, source labels, provenance, recorded-at ceilings, supersession lifecycle, duplicate identities, and exact requested coverage.

The adapter remains fail-closed when the projection is unavailable, conflicting, malformed, duplicated, or outside the requested period/as-of boundary. It maps no current balance, mutable metadata, event timestamp, cost, or asset name into acquisition facts. Unavailable and conflicting outcomes expose no projection records and are preserved by the report provider and presentation mapper.

The repository still does not authorize deriving acquisition facts from inventory_authority.quantity, inventory_history.recorded_at, or mutable inventory_business_details fields. Any future authority expansion must introduce an explicit reviewed projection contract rather than reinterpret those fields.

## Delivered adapter boundary

The delivered adapter is reports.purchase_source_performance_inventory_adapter.PurchaseSourcePerformanceInventoryAdapter. It is constructor-injected with the InventoryAcquisitionProjectionRepository protocol, translates the report reader request into an inclusive UTC as-of projection request, and maps only validated canonical projection records into PurchaseSourcePerformanceInventoryRecord values.

The adapter returns available records in canonical deterministic order, including a valid empty complete read. Projection unavailable and conflict results map to unavailable and conflicting reads without exposing records. Malformed projection records fail closed as conflicting. The adapter does not construct a database, open a second repository, write through Inventory services, join sale evidence, calculate formulas, or depend on UI state.

The merged composition snapshot uses the existing query and presentation boundaries to inject an immutable Purchase Source Performance presentation into ReportsWorkspace. The workspace remains presentation-only and read-only.

## Provenance and diagnostics

An available read must identify the source domain as `inventory`, preserve the requested period/as-of boundary, and provide deterministic provenance naming the canonical read authority and fields used. An unavailable or conflicting read must preserve a stable reason such as `inventory_acquisition_quantity_unavailable`, `purchase_date_missing`, `purchase_date_invalid_iso`, `purchase_source_missing`, `duplicate_canonical_inventory_identity`, or `inventory_acquisition_coverage_conflict`. The adapter must not downgrade a detected conflict to an empty successful read.

`PurchaseSourcePerformanceProvider` in `reports/purchase_source_performance_provider.py` already fails closed for adapter exceptions, unsupported response types, non-available Inventory outcomes, duplicate identities, and out-of-period records. The adapter must honor that protocol; it must not implement sale joins, formula calculation, application composition, or provider registration. The provider remains responsible for passing canonical Inventory identities to `SaleCompletionQueryService` and for aggregating report evidence.

## Explicit non-goals and follow-up

This boundary does not authorize changing core/schema.py, adding acquisition columns, migrations, persistence, mutation authority, charts, exports, ranking, recommendation, or a second Inventory storage path. It does not authorize deriving acquired units from balances or inferring dates from event timestamps. The existing composition snapshot remains a deterministic read-only presentation boundary.

Any future expansion beyond the delivered projection, adapter, provider, and composition snapshot requires a separately reviewed authority boundary and focused tests.
