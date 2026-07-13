# Build 701V — Inventory Age Provider Composition Integration Gate

**Status:** PREBUILD COMPOSITION GATE  
**Capability:** CAP-012 Reports  
**Issue:** #286

## Decision

Build 701U proved that an application-owned provider can compose approved Inventory detail and CAP-005B product-link evidence without owning persistence. Build 701V defines the only acceptable future composition path before that provider is wired into a report query service.

This build adds no runtime wiring. It preserves the provider as an injected read-only dependency.

## Composition ownership

`composition/application_composition.py` is the future composition owner. Reports, UI code, and report-row derivation must not construct adapters, open SQLite connections, or construct database managers.

A later composition slice may create the dependency chain in this order:

```text
Runtime-owned read-connection factory
    ├─> InventoryDetailReadAdapter
    └─> InventoryProductLinkReadAdapter
                │
                v
ApplicationInventoryAgeInputProvider
                │
                v
Future composition-owned Reports query service
```

The read-connection factory remains runtime infrastructure. It is injected into each adapter and is not moved into Reports.

## Required runtime behavior

The later composition owner must:

1. construct only the approved injected read adapters;
2. pass those adapters to `ApplicationInventoryAgeInputProvider`;
3. require callers to provide an explicit `as_of_date`;
4. preserve the provider's deterministic `found`, `not_found`, `unlinked`, `conflicting`, and `unavailable` outcomes;
5. fail closed before report-row derivation when the provider result is not `found`;
6. pass only a verified `InventoryAgeInputRecord` into the existing pure Reports bridge.

The later composition owner must not substitute asset names, types, or Inventory IDs for canonical Product Registry identity.

## Forbidden access paths

The future Reports query service, Reports workspace, and UI remain forbidden from:

- opening SQLite connections;
- constructing `DatabaseManager`, `InventoryAppService`, or `InventoryProductLinkService`;
- querying `inventory_business_details` or `inventory_product_links` directly;
- creating, repairing, or mutating a product link while reading;
- writing a report cache, audit event, or source-domain record.

## Next runtime gate

Only after Build 701V is merged **and Mark has pulled current `main` locally** may a separately scoped runtime slice add composition-root construction for this provider.

That later slice must remain UI-free and must prove:

- one existing runtime-owned read-connection authority is reused;
- no database-manager construction or schema initialization occurs;
- no write, event, audit, repair, migration, network, scheduler, alert, cloud-sync, or automation behavior is introduced;
- Reports receives a provider result through composition rather than direct persistence access.

## Non-goals

Build 701V adds no composition-root modification, provider construction, runtime database connection, schema initialization, write, event, audit entry, repair, UI, chart, export, workspace, migration, network call, scheduler, alert, cloud sync, or automation.
