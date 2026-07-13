# Build 701O â Inventory Age Read API Audit

**Status:** PROVIDER IMPLEMENTATION BLOCKED  
**Capability:** CAP-012 Reports  
**Issue:** #272

## Audit decision

The existing Inventory read surface can supply Inventory detail, but CAP-005B has no approved asset-to-product read surface. Build 701O therefore does not authorize an `InventoryAgeInputProvider` implementation.

The provider protocol and result envelope remain pure contracts. Reports must continue to receive only an already-created `InventoryAgeInputRecord` or an explicit provider result.

## Inventory detail surface

`services.inventory_app_service.InventoryAppService.get_asset_detail(asset_id)` is the current Inventory detail read operation. Its result contains:

- `asset_id`, `asset_name`, `asset_type`, and `state`;
- `quantity` and `total_cost_minor`;
- `verified_at`;
- raw `purchase_date`, `purchase_source`, `storage_location`, and `notes`.

For an absent asset, it raises `ValueError('Inventory asset not found')`. The operation can expose archived assets, so a later provider must explicitly classify a non-`COMPLETED` asset as not found or otherwise ineligible according to its separately approved contract. It must preserve `purchase_date` as raw text.

This surface is not imported by Reports. A later application-owned adapter may use it only after it is constructed through an approved composition boundary.

## CAP-005B product-link surface

`services.inventory_product_link_service.InventoryProductLinkService` currently exposes `quantities(product_id)`, which derives quantities for a known product ID. It does not expose a read operation that accepts an Inventory `asset_id` and returns exactly one of linked, unlinked, conflicting, or unavailable product-link evidence.

Its constructor initializes `DatabaseManager`, and its public linkage operation is `link(asset_id, product_id, request_id)`, which mutates CAP-005B authority. Neither behavior is an approved read dependency for Inventory Age.

## Required implementation gate

Before a provider implementation can be approved, a later build must add or identify a dedicated, injected, read-only CAP-005B boundary with all of these properties:

1. accepts a nonblank Inventory asset ID;
2. returns deterministic linked, unlinked, conflicting, or unavailable evidence;
3. exposes a canonical product ID only for exactly one verified link;
4. performs no schema initialization, write, event, audit entry, repair, or network work;
5. can be composed without giving Reports direct database or repository access.

Until that gate is complete, the correct outcome is `unavailable`; no fallback may infer a product identity from asset name, type, or Inventory ID.

## Non-goals

Build 701O adds no provider implementation, database or repository query, service modification, composition wiring, UI, chart, export, threshold, report workspace, product-link mutation, schema, migration, persistence, write, import, data correction, Inventory write validation change, network call, scheduler, alert, cloud sync, or automation.
