# CAP-012Z Sale-Completion Model and Read Boundary

## Status

Approved planning boundary only. This document translates CAP-012Y into a model and read-API implementation boundary. It does not authorize schema, persistence, repository, service, provider, registration, composition, or UI implementation.

## Model responsibility

The permanent sale-completion model represents immutable evidence emitted or accepted by canonical authority. It does not represent settlement, payout, allocation, listing, shipping, or descriptive marketplace state.

Each evidence record must expose:

- `sale_completion_evidence_id`;
- `sale_id`;
- `inventory_id`;
- `lineage_parent_evidence_id` when applicable;
- `lifecycle_state`;
- `completed_unit_quantity` when state is `completed`;
- `completed_at` when state is `completed`;
- `source_system`;
- `recorded_at`.

All identities are opaque canonical values. They must not be created from names, SKUs, listing text, prices, marketplace labels, settlement values, or timestamp proximity.

## Lifecycle constraints

Supported states are:

- `pending`;
- `completed`;
- `cancelled`;
- `refunded`;
- `reversed`;
- `superseded`.

Only `completed` evidence contributes completed units.

A `completed` record requires a positive whole-unit quantity and authoritative `completed_at`.

`refunded`, `reversed`, and `superseded` records require an exact predecessor evidence identity. Historical evidence is append-only and never overwritten.

Unsupported states, missing predecessor references, cycles, ambiguous branching, duplicate active terminal evidence, impossible quantities, or conflicting inventory linkage must fail closed.

## Value-object boundary

A future implementation may define immutable domain values equivalent to:

- `SaleCompletionEvidence`;
- `SaleCompletionLifecycleState`;
- `SaleCompletionCoverage`;
- `SaleCompletionQuery`;
- `SaleCompletionQueryResult`.

Names may vary only through a separately reviewed implementation build. Semantics may not weaken CAP-012Y.

## Query request boundary

The read API must accept a typed request containing:

- one or more canonical `inventory_id` values, canonical `sale_id` values, or both;
- inclusive lower and exclusive upper `completed_at` boundaries when a period is requested;
- an explicit `as_of` boundary;
- deterministic pagination or bounded-result semantics if pagination is needed.

The API must reject malformed ranges, unsupported identity types, empty identity scope where unrestricted reads are not explicitly authorized, and ambiguous time-zone handling.

## Query result boundary

The read API must return one typed result variant:

1. `available` with immutable ordered evidence and explicit complete coverage;
2. `unavailable` with a stable reason code and evaluated coverage;
3. `conflict` with a stable reason code and evaluated coverage.

An exception, `None`, unsupported response type, partial unmarked response, or silently omitted record is not an available result.

## Coverage contract

Coverage must identify:

- requested inventory identities;
- requested sale identities;
- consulted source domains;
- evaluated time range;
- `as_of` boundary;
- evidence count;
- completeness state;
- deterministic ordering definition.

Incomplete coverage that could change totals must be unavailable or conflicting. It must never produce a valid zero.

## Ordering contract

Available evidence must be ordered deterministically by canonical immutable fields. The minimum ordering key is:

1. authoritative `completed_at` when present;
2. `recorded_at`;
3. `sale_id`;
4. `inventory_id`;
5. `sale_completion_evidence_id`.

Equivalent evidence must produce equivalent order across runs and storage implementations.

## Validation ownership

The model validates intrinsic record invariants.

The read boundary validates request shape, response type, coverage, ordering, duplicate identity, lineage integrity, active terminal state, and cross-record quantity or linkage conflicts.

Storage adapters may enforce stronger physical constraints but may not replace domain validation or weaken fail-closed behavior.

## Repository boundary

A future repository may expose only read operations required by the typed query boundary. It must not expose ad hoc report-specific joins, fuzzy searches, marketplace-text matching, settlement inference, or mutable correction operations through this read contract.

Persistence technology, table shape, indexing, migration strategy, and import workflow remain unauthorized.

## Service boundary

A future application service may coordinate request validation, repository reads, lineage evaluation, coverage construction, and typed result mapping.

It must not calculate Purchase Source Performance, register reports, compose UI, infer inventory identity, or convert unavailable evidence into zero.

## Relationship to Purchase Source Performance

CAP-012Z does not authorize the Purchase Source Performance provider.

Provider work remains blocked until a separately approved implementation establishes the permanent sale-completion model and read boundary, proves canonical inventory linkage, and passes contract-focused tests.

## Explicitly unauthorized

- schema, migration, table, event-store, or persistence implementation;
- repository or service implementation;
- imports, marketplace APIs, networking, polling, or writes;
- report provider, registration, composition, or live execution;
- UI, presenter, preview, chart, or export;
- settlement, allocation, text, SKU, product, price, marketplace, or timestamp-proximity inference;
- revenue, cost, margin, return, ranking, recommendation, or trend metrics.

## Next gate

The next controlled build may define only the contract-level immutable Python domain types and tests for the sale-completion model and query result variants. Repository, storage, service, provider, registration, composition, and UI work remain separately gated.