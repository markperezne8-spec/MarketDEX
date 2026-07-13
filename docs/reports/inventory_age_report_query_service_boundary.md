# Build 701X — Inventory Age Report Query-Service Boundary

**Status:** PREBUILD QUERY-SERVICE GATE  
**Capability:** CAP-012 Reports  
**Issue:** #290

## Decision

A future Inventory Age report query service is composition-owned. It receives an injected `InventoryAgeInputProvider` and produces one explicit report-read result for one Inventory position and one caller-provided `as_of_date`.

Reports presentation, workspaces, and row derivation do not open persistence or construct the provider.

## Required flow

```text
Inventory position ID + explicit as-of date
                │
                v
Injected InventoryAgeInputProvider — exactly one call
                │
                v
Explicit provider outcome
   ├─ found + verified input record ─> pure build_inventory_age_row_from_input()
   └─ not_found / unlinked / conflicting / unavailable ─> explicit non-row result
```

The query service must call the provider exactly once. It may call `build_inventory_age_row_from_input()` only when the provider result is `found` and contains a verified `InventoryAgeInputRecord`.

## Future result envelope

A later implementation may return an immutable result envelope with:

- `outcome` — one of `found`, `not_found`, `unlinked`, `conflicting`, or `unavailable`;
- `row` — present only for `found`;
- `reason` — preserved provider evidence or deterministic query-service explanation.

The query-service result preserves the provider outcome even when a found input record produces an Inventory Age row with unavailable or invalid purchase-date evidence. Source-date quality belongs to the row; provider availability belongs to the query result.

## Fail-closed rules

The query service must not:

- return a row for an unlinked, conflicting, unavailable, or not-found provider result;
- infer a `product_id` from asset identity, name, or type;
- replace unavailable evidence with zero age, zero quantity, or a placeholder row;
- invoke the provider again to recover an outcome;
- catch a provider result and silently convert it into a found result.

## Ownership and forbidden access

Only application composition may construct the future query service. It receives its provider through injection.

Reports domain code, the query service, UI, and report workspaces must not:

- open SQLite connections;
- construct `DatabaseManager`, `InventoryAppService`, or product-link services;
- query Inventory or product-link tables directly;
- create writes, events, audit entries, repairs, caches, schema changes, or migrations;
- invoke networks, exports, schedulers, alerts, cloud sync, or automation.

## Next runtime gate

Only after Build 701X is merged **and Mark has pulled current `main` locally** may a separately scoped build implement the immutable query result envelope and injected query service.

That build remains UI-free. It must use the provider exactly once, preserve all explicit outcomes, invoke only the existing pure bridge for found evidence, and add focused regression coverage.

## Non-goals

Build 701X adds no query-service implementation, provider invocation, composition-root change, SQLite access, database manager construction, schema initialization, report workspace, chart, export, migration, write, event, audit entry, repair, network call, scheduler, alert, cloud sync, or automation.
