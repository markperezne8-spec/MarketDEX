# CAP-012AQ — Canonical Acquisition Evidence Authority Boundary

## Status and scope

This document is the authority-design boundary for issue #685. It identifies the acquisition facts that must become canonical before the CAP-012 Purchase Source Performance projection provider or adapter may be implemented. It is planning only: no schema, migration, SQL, persistence, provider, adapter, composition, registration, catalog, UI, calculation, or mutation is authorized.

## Business and report requirement

Purchase Source Performance requires a complete, deterministic population of canonical Inventory acquisitions. Each record must prove the canonical Inventory identity, original acquired units, acquisition date, and exact purchase-source label. The existing InventoryAcquisitionProjectionRecord in core/inventory_acquisition_projection.py is the contract target; its period is inclusive-start/exclusive-end, its as_of is timezone-aware and inclusive, and its available outcome requires complete coverage and provenance.

## Current authority gap

The current authorities cannot prove that record without inference:

- core/schema.py stores inventory_authority.quantity as the current balance, which may be changed by later movement.
- repositories/inventory_repository.py, InventoryRepository.apply, writes append-only inventory_history movement rows, but those rows carry no acquisition purchase source or acquisition date.
- services/inventory_app_service.py, InventoryAppService.get_asset_detail, reads current quantity and COALESCEd business-detail text.
- InventoryAppService.update_business_details permits later updates to purchase date/source, so those fields are mutable metadata rather than immutable acquisition evidence.

Current quantity, recorded_at, verified_at, created_at, cost, asset name, and mutable business details must never be inferred as the missing acquisition facts.

## Required canonical authority

A future implementation must establish one canonical, immutable acquisition-evidence grain:

- one stable acquisition evidence identity;
- canonical Inventory asset_id/inventory identity;
- positive original acquired units for that acquisition;
- strict ISO acquisition date or equivalent validated date value;
- exact trimmed, non-blank purchase-source label;
- immutable event/evidence provenance and recorded timestamp;
- explicit lifecycle/supersession policy; and
- complete-coverage semantics for a projection request.

An acquisition correction must preserve the original evidence and link a replacement or superseding evidence record. It must not silently rewrite acquired quantity, source, or date. Multiple acquisitions for one Inventory identity require an explicit documented grain and a projection rule; until that rule exists, the provider returns unavailable or conflicting rather than aggregating by assumption.

## Read boundary and outcomes

A future read-only evidence reader must receive the projection request and return all-or-nothing evidence for the requested period and inclusive as_of. It must preserve deterministic ordering and provenance. Empty complete coverage may be available.

Missing source/date/authoritative units, malformed values, unsupported lifecycle, or partial coverage return an unavailable result with stable diagnostics. Duplicate identity at the declared grain, incompatible supersession, contradictory field values, out-of-period evidence, or evidence later than as_of return conflicting. Neither non-available outcome exposes records.

## Migration decision

The repository does not currently contain this authority. Therefore an explicit new canonical acquisition-evidence authority is required before provider or adapter work. The next separately approved implementation slice must be limited to that authority's schema/persistence/service boundary and focused tests. It must not compose the provider, register a report, alter the UI, or introduce report calculations.