# Build 701J — Inventory Age Product-Link Integration Boundary

**Status:** PREBUILD CLASSIFICATION ONLY  
**Capability:** CAP-012 Reports  
**Issue:** #262

## Decision

Reports cannot yet bridge an Inventory detail mapping into an Inventory Age row because the current detail mapping lacks canonical Product Registry identity.

The future bridge must consume a composition-owned input record that brings together approved Inventory detail evidence and separately owned CAP-005B Inventory–Product Link evidence. Reports must not create substitute product identity from an asset identifier, asset name, or asset type.

## Repository evidence

- `InventoryAppService.get_asset_detail()` returns `asset_id`, `asset_name`, `asset_type`, current quantity, state, purchase date, and storage location.
- Canonical product identity is owned by Product Registry.
- CAP-005B persists Inventory–Product Link authority through `inventory_product_links`.
- Existing Inventory detail output does not contain a canonical `product_id`.

## Required future input contract

A later application-owned read model may supply exactly these categories of evidence:

- **Inventory evidence:** inventory position or asset ID, display name, quantity, status, purchase date, and storage location.
- **Product-link evidence:** canonical Product Registry `product_id` and a link-evidence state.
- **Read context:** explicit as-of date supplied by the caller.

The record must preserve source boundaries. It may not become a second Inventory, Product Registry, or product-link database.

## Product-link evidence states

A future input record must distinguish:

- **linked** — exactly one canonical Product Registry product ID is verified for the Inventory asset;
- **unlinked** — no canonical product link is available;
- **conflicting** — more than one incompatible product link or other contradiction is reported.

Unlinked and conflicting are not permission to invent or guess a product ID. They must fail closed before an Inventory Age row is created.

## Dependency direction

```text
Inventory detail read contract ─┐
                                ├─> Application-owned Inventory Age input record ─> Reports bridge
CAP-005B product-link read ────┘
```

Reports presentation and Reports domain code must not bypass this boundary by opening SQLite, querying `inventory_product_links`, or constructing `InventoryAppService`.

## First implementation gate

After Build 701J merges, Build 701K may introduce an immutable, persistence-free `InventoryAgeInputRecord` model with controlled product-link evidence states and validation.

Build 701K must not access a database, invoke Inventory or Product Registry services, create a report row, modify product links, or wire application composition.

## Non-goals

Build 701J adds no runtime integration, product-link query, adapter-to-row bridge, repository, database, schema, migration, persistence, write, import, data correction, report calculation, chart, export, workspace, navigation, provider, network call, automation, or UI change.
