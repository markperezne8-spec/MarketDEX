# Build 701M — Inventory Age Application Read Dependency

**Status:** PREBUILD CLASSIFICATION ONLY  
**Capability:** CAP-012 Reports  
**Issue:** #268

## Decision

A future Inventory Age application service requires exactly one composition-owned read dependency that supplies validated `InventoryAgeInputRecord` values. That dependency combines read-only Inventory detail with read-only CAP-005B product-link evidence before Reports receives it.

Reports remains a consumer. It must not query SQLite, `inventory_business_details`, `inventory_product_links`, Inventory repositories, or Product Registry repositories directly.

## Ownership

- Inventory owns asset ID, display name, quantity, status, purchase date, and storage location.
- CAP-005B Inventory–Product Link authority owns the relationship between the Inventory asset and canonical Product Registry identity.
- Product Registry owns the canonical `product_id`.
- The future input provider owns only the composition of approved read evidence into `InventoryAgeInputRecord`.
- Reports owns deterministic row derivation and later read-only presentation.

No layer may create, repair, or mutate an Inventory–Product Link while reading Inventory Age evidence.

## Provider contract

A later provider may expose a single operation conceptually equivalent to:

```text
get_inventory_age_input(asset_id, as_of_date) -> InventoryAgeInputRecord | unavailable result
```

The operation must:

1. require a nonblank Inventory asset ID;
2. require an explicit as-of date;
3. read only completed/current Inventory detail through an approved Inventory read boundary;
4. read Product Link evidence through an approved CAP-005B read boundary;
5. return `linked` only when exactly one canonical product ID is verified;
6. return `unlinked` when no product link exists;
7. return `conflicting` when incompatible link evidence exists;
8. preserve raw purchase-date text without parsing or rewriting it;
9. avoid writes, events, audit entries, background work, provider calls, and network access;
10. return deterministic results for the same local database state and arguments.

## Read outcomes

The future provider must distinguish:

- **not found** — Inventory asset is absent or not eligible for the approved read scope;
- **linked** — Inventory detail and one canonical product link are available;
- **unlinked** — Inventory detail exists but no product link is available;
- **conflicting** — Inventory detail exists but product-link evidence is contradictory;
- **unavailable** — a required approved read dependency cannot provide evidence.

The provider must not replace unlinked, conflicting, or unavailable outcomes with a guessed product ID.

## Dependency direction

```text
Inventory read boundary ────────┐
                                ├─> Application-owned Inventory Age input provider ─> Reports pure bridge
CAP-005B product-link boundary ┘
```

Application composition creates the provider. UI and Reports domain code receive only its explicit read result or the already-created `InventoryAgeInputRecord`.

## First implementation gate

After Build 701M merges, Build 701N may add an immutable result envelope and a provider protocol. That build must remain persistence-free and must not implement database reads or application composition wiring.

A later separately approved build may implement the provider using existing Inventory and product-link read paths only after their exact read APIs and empty/conflict behavior are audited.

## Non-goals

Build 701M adds no provider implementation, repository query, database connection, composition wiring, UI, chart, export, threshold, report workspace, product-link mutation, schema, migration, persistence, write, import, data correction, Inventory write validation change, live provider, network call, scheduler, alert, cloud sync, or automation.
