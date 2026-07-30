# CAP-012AJ — Sale-Completion Repository Consumer Boundary

## Status
Planning boundary only.

## Purpose
Define one deterministic application-service seam that consumes the registered `SaleCompletionRepository` without broad runtime rewiring.

## Approved consumer seam
The first consumer must be a single application service whose constructor receives a `SaleCompletionRepository` explicitly. The service owns query orchestration only; it does not own repository construction, database lifecycle, persistence, retries, or fallback selection.

## Dependency direction

```text
application composition
    -> constructs DatabaseManager
    -> builds SaleCompletionRepository
    -> injects repository into one application service
    -> application service issues SaleCompletionQuery
    -> repository returns SaleCompletionRepositoryRead
```

The consumer must depend on the existing protocol, never on `SqliteSalesSaleCompletionRepository`.

## Result handling
The consumer must preserve all existing repository outcomes:

- `SaleCompletionAvailable` may proceed to consumer-owned interpretation.
- `SaleCompletionUnavailable` must remain unavailable and fail closed.
- `SaleCompletionConflict` must remain conflicting and fail closed.
- Repository diagnostics must be propagated without rewriting reason codes.

The consumer must not silently coerce unavailable or conflicting reads into empty success results.

## Ownership

- Application composition owns construction and lifecycle wiring.
- The repository owns data access and evidence validation.
- The consumer owns only query construction and application-level interpretation.
- Callers own presentation or workflow decisions outside this boundary.

## Explicit exclusions

This boundary does not authorize:

- UI, reports, metrics, exports, or integrations
- schema changes or database writes
- retries, fallback repositories, caches, or secondary sources
- globals, service locators, hidden registries, or import-time construction
- broad service rewiring
- changes to repository result contracts

## Acceptance criteria for implementation

1. One application service accepts `SaleCompletionRepository` through its constructor.
2. The concrete SQLite adapter is not imported by the consumer.
3. Available, unavailable, and conflict outcomes are preserved deterministically.
4. Diagnostics and reason codes remain stable.
5. Focused tests prove constructor injection and fail-closed behavior.
6. Full CI is green before merge.
