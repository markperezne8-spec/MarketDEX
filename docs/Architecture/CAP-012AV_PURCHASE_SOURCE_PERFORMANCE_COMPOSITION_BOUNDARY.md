# CAP-012AV — Purchase Source Performance Composition Boundary

## Status

Approved planning boundary for issue #695. This document authorizes a future composition-only implementation. It does not itself change runtime construction.

## Purpose

CAP-012AU now maps the canonical Inventory acquisition projection into the existing `PurchaseSourcePerformanceInventoryReader` seam. The existing `PurchaseSourcePerformanceProvider` also requires the sale-completion query consumer. A later implementation may wire these dependencies through the existing `ApplicationComposition` without changing either domain contract.

## Required construction path

The composition root owns one dependency graph:

1. Reuse the composition-owned `InventoryAppService.database` / `DatabaseManager`; do not create another database manager or database path.
2. Construct `SqliteInventoryAcquisitionProjectionRepository` with that existing manager.
3. Construct `PurchaseSourcePerformanceInventoryAdapter` with the projection repository protocol.
4. Reuse the registered sale-completion repository/query consumer path already owned by composition.
5. Construct `PurchaseSourcePerformanceProvider` with the adapter and sale-completion query service.

Construction order and object identity must be deterministic and inspectable in focused composition tests.

## Invariants

- Dependencies are constructor-injected; no globals, service locators, hidden lookups, or import-time side effects.
- The graph is read-only. Construction must not initialize schema, open long-lived unmanaged connections, write rows, mutate Inventory, or alter report formulas.
- Adapter and provider results pass through unchanged except for the already-approved protocol mapping in CAP-012AU.
- Unavailable/conflicting outcomes remain fail-closed and expose no fabricated records or zeroes.
- Existing Inventory Age, Inventory Turnover, sale-completion, and Mission Control composition remain behaviorally unchanged.

## Explicit non-goals

This boundary does not authorize report catalog registration, live Purchase Source Performance execution, UI/workspace wiring, presentation, charts, exports, calculations, schema or migration changes, persistence, fallback sources, retries, caching, networking, polling, background tasks, or a second composition root.

## Verification required for the next implementation

The implementation must add only a focused composition factory or method plus tests proving:

- exact shared `DatabaseManager` identity;
- protocol conformance and dependency order;
- no schema/data/audit mutation during construction;
- deterministic fail-closed propagation;
- existing composition regression coverage remains green.

After that implementation is merged, report catalog registration and live execution require a separate reviewed boundary.
