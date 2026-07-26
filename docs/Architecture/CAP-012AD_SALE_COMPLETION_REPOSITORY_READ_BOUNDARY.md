# CAP-012AD Sale-Completion Repository Read Boundary

## Status

Approved planning boundary only. This document authorizes no persistence implementation.

## Responsibility

A future read-only repository contract may accept `SaleCompletionQuery` and return typed sale-completion query outcomes backed only by evidence that passes `validate_sale_completion_evidence_set`.

## Required contract behavior

- preserve explicit inventory and sale identity scope;
- honor timezone-aware `as_of` and optional completion range boundaries;
- return deterministic canonical evidence ordering;
- expose source and evidence coverage without overstating completeness;
- return unavailable when the repository cannot establish complete coverage;
- return conflict when retrieved evidence fails CAP-012AC validation;
- never silently drop malformed, duplicate, missing-lineage, cyclic, branched, or otherwise conflicting evidence;
- never infer identity from descriptions, products, marketplaces, prices, settlement, or timestamp proximity.

## Typed outcomes

The repository must use or adapt the existing `SaleCompletionAvailable`, `SaleCompletionUnavailable`, and `SaleCompletionConflict` result family. Validation conflicts must map to a stable conflict reason while preserving the involved evidence identities through an explicit diagnostic boundary.

## Coverage

Coverage must identify:

- requested inventory and sale identities;
- evaluated `as_of` boundary;
- requested completion range when present;
- source systems consulted;
- retrieved evidence count;
- whether coverage is complete, unavailable, or conflicting.

An empty evidence tuple may be available only when the repository can prove complete coverage for the requested scope. Unknown coverage is unavailable, not empty success.

## Read-only repository shape

A future implementation may define a protocol equivalent to:

```python
class SaleCompletionRepository(Protocol):
    def query_sale_completion(
        self,
        query: SaleCompletionQuery,
    ) -> SaleCompletionQueryResult: ...
```

The contract must remain storage-agnostic and synchronous at this boundary unless separately reviewed.

## Validation handoff

Retrieved evidence must be validated before an available result is constructed. A valid result uses the validator's canonical ordering. A validation conflict must fail closed and must not be converted into unavailable or empty available output.

## Explicitly unauthorized

- database schema, migrations, SQLite, event stores, files, or persistence adapters;
- write, append, update, delete, repair, reconciliation, or mutation APIs;
- application services, providers, registration, composition, or live execution;
- imports, marketplace APIs, networking, polling, UI, reports, previews, charts, or exports;
- settlement, revenue, cost, margin, ranking, recommendation, or trend metrics;
- inferred identity or descriptive matching.

## Next gate

The next controlled build may implement only the repository protocol, typed diagnostic mapping needed by that protocol, and contract tests using in-memory fakes. Storage adapters and application services remain separately gated.
