# CAP-012AK — Sale-Completion Repository Consumer

## Status
Implemented.

## Delivered boundary
`SaleCompletionQueryService` is the first application-service consumer of the existing `SaleCompletionRepository` protocol.

The service:

- receives the repository through constructor injection;
- constructs the existing `SaleCompletionQuery` contract;
- delegates exactly one repository read;
- returns the repository read unchanged;
- preserves available, unavailable, conflict, diagnostic, and reason-code authority.

## Exclusions preserved
No UI, reports, metrics, exports, integrations, schema changes, writes, retries, fallback sources, caches, globals, service locators, or concrete SQLite imports are introduced.
