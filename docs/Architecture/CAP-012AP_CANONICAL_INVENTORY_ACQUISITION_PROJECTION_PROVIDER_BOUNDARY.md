# CAP-012AP — Canonical Inventory Acquisition Projection-Provider Boundary

## Status and scope

This is the architecture boundary for issue #683. It authorizes a documentation-only design for a future read-only provider of `InventoryAcquisitionProjectionResult`. It does not authorize provider implementation, adapter implementation, SQL, schema, migration, persistence, application composition, registration, report catalog work, live execution, UI, networking, or mutation.

## Existing contract and authority

`core/inventory_acquisition_projection.py` defines the runtime-neutral result contract. `InventoryAcquisitionProjectionRequest` requires an inclusive-start/exclusive-end date period and timezone-aware `as_of`; `InventoryAcquisitionProjectionAvailable` requires exact complete coverage and non-empty provenance. Records require a canonical `inventory_id`, positive `acquired_units`, a `date` `acquisition_date`, and an exact trimmed non-blank `purchase_source_label`.

The existing canonical Inventory storage cannot currently provide all of those facts without inference:

- `core/schema.py` defines `inventory_authority.quantity` as a current non-negative balance, not acquired units.
- `repositories/inventory_repository.py`, `InventoryRepository.apply`, appends quantity deltas to `inventory_history`; those rows have no purchase source or purchase date.
- `services/inventory_app_service.py`, `InventoryAppService.get_asset_detail`, returns current quantity plus `COALESCE`d business metadata.
- `inventory_business_details.purchase_date` and `.purchase_source` are mutable optional text fields; `InventoryAppService.update_business_details` may change them independently of an acquisition event.

Neither current balance, `recorded_at`, `verified_at`, `created_at`, nor mutable business metadata may be promoted to acquisition authority.

## Future provider seam

A future provider must be constructor-injected with a narrow read-only canonical acquisition evidence reader. It must accept `InventoryAcquisitionProjectionRequest` and return exactly one `InventoryAcquisitionProjectionResult`. The provider must not construct a database, query a second storage model, perform writes, depend on UI state, or perform report calculations.

An available result is permitted only when the reader proves, for the complete requested canonical population:

1. unique canonical Inventory identity;
2. positive authoritative acquired units;
3. strict ISO acquisition date parsed to `date`;
4. exact trimmed non-blank purchase-source label;
5. period membership in `[period_start, period_end)`;
6. acquisition date no later than the inclusive `as_of` date; and
7. deterministic provenance naming the exact authority and fields.

Records must be ordered by acquisition date, canonical identity, case-folded label, then exact label. Empty complete coverage is available; partial coverage is never silently dropped.

## Fail-closed outcomes

Return unavailable, with no records, for missing acquisition quantity, missing source, missing date, invalid ISO date, unsupported reader result, or incomplete coverage. Stable reasons include `inventory_acquisition_quantity_unavailable`, `purchase_date_missing`, `purchase_date_invalid_iso`, `purchase_source_missing`, and `inventory_acquisition_coverage_unavailable`.

Return conflicting, with no records, for duplicate canonical identity, contradictory evidence, malformed typed values, incompatible coverage, out-of-period records, or records after `as_of`. Stable reasons include `duplicate_canonical_inventory_identity`, `inventory_acquisition_evidence_conflict`, and `inventory_acquisition_coverage_conflict`.

## Next controlled movement

The repository currently lacks a proven canonical source that supplies acquired units, immutable acquisition date, exact source label, and complete coverage together. Therefore the next implementation issue must first establish that read authority; it may not implement the Purchase Source Performance adapter, runtime composition, or presentation.