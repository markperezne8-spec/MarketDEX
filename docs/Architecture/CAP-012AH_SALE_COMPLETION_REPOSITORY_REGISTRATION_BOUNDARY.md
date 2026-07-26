# CAP-012AH Sale-Completion Repository Registration Boundary

## Status

Approved planning boundary only. This document authorizes no runtime registration, consumer service, UI, schema, migration, or write path.

## Responsibility

A future controlled build may expose one explicit application-composition function that constructs `SqliteSalesSaleCompletionRepository` from the existing `DatabaseManager` and returns it through the `SaleCompletionRepository` protocol boundary.

## Required composition behavior

- construct exactly one SQLite sale-completion repository for the supplied database manager;
- preserve the CAP-012AG adapter without wrapping, widening, retrying, translating, or suppressing its results;
- expose the dependency through the existing `SaleCompletionRepository` protocol rather than the concrete type at consumer boundaries;
- keep dependency direction from application composition toward core protocol and concrete infrastructure adapter;
- avoid module-import side effects, hidden singletons, global mutation, and implicit database initialization;
- keep repository lifecycle explicit and owned by the composition root;
- preserve synchronous, read-only, fail-closed query behavior and stable diagnostics.

## Ownership and lifecycle

The composition root owns construction. The caller owns the supplied `DatabaseManager` and its database path. Registration must not create an alternate database manager, open persistent connections, initialize schema, or modify runtime state.

The repository may retain the supplied manager reference only for later `read_connection()` calls. No connection may be opened during construction.

## Consumer boundary

Consumers must depend on `SaleCompletionRepository`. They must not import `SqliteSalesSaleCompletionRepository`, execute SQL, inspect SQLite rows, reinterpret adapter diagnostics, or substitute unavailable/conflict results with empty available data.

No consumer is authorized in this planning build.

## Verification requirements

A future implementation build must prove:

- construction returns an object satisfying `SaleCompletionRepository`;
- the exact supplied `DatabaseManager` is used;
- construction performs no database read, write, initialization, or connection opening;
- available, unavailable, and conflict outcomes pass through unchanged;
- repeated explicit construction does not create shared global state;
- no service locator or fallback repository is introduced.

## Explicitly unauthorized

- schema creation, schema modification, migrations, or initialization;
- inserts, updates, deletes, repair, reconciliation, or mutation APIs;
- automatic retries, fallback sources, caching, polling, or multi-source composition;
- service locators, mutable registries, hidden globals, or import-time construction;
- application services, business metrics, settlement, revenue, cost, margin, ranking, recommendation, reports, previews, exports, or UI;
- networking, marketplace APIs, imports, background workers, or scheduled execution;
- inferred identity, fuzzy matching, descriptive joins, or widened query scope.

## Next gate

The next controlled build may implement one explicit composition function plus isolated composition tests. Any consumer service, UI exposure, report, metric, fallback, cache, or additional source requires a separate reviewed boundary.
