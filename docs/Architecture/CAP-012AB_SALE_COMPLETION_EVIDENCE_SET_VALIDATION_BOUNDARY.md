# CAP-012AB Sale-Completion Evidence-Set Validation Boundary

## Status

Approved planning boundary only. This document defines validation of immutable sale-completion evidence collections after CAP-012AA. It does not authorize repository, storage, service, provider, registration, composition, or UI implementation.

## Responsibility

A future pure domain validator may accept an immutable sequence of `SaleCompletionEvidence` values and return a typed validation outcome. It must be deterministic, side-effect free, storage-independent, and fail closed.

## Required validations

The validator must detect:

- duplicate `sale_completion_evidence_id` values;
- missing lineage parents;
- self-reference and lineage cycles;
- ambiguous branching from one predecessor;
- incompatible sale or inventory linkage across a lineage chain;
- multiple active terminal records for the same canonical sale and inventory scope;
- unsupported lifecycle transitions;
- impossible completed quantities or conflicting quantity histories;
- completion timestamps later than `recorded_at` or outside an explicit `as_of` boundary;
- non-canonical input ordering when ordered input is required.

No validation may infer identity from text, SKU, product, marketplace, price, settlement, or timestamp proximity.

## Typed outcomes

A future implementation may expose immutable outcomes equivalent to:

- `SaleCompletionEvidenceSetValid`;
- `SaleCompletionEvidenceSetConflict`;
- `SaleCompletionEvidenceSetValidationResult`.

A valid result must contain deterministically ordered evidence and the evaluated `as_of` boundary.

A conflict result must contain at least one stable reason code and the canonical evidence identities involved. Exceptions may represent malformed individual values, but cross-record conflicts must not be silently dropped or converted into an empty valid result.

## Stable conflict categories

The implementation must define stable machine-readable categories equivalent to:

- `duplicate_evidence_identity`;
- `missing_lineage_parent`;
- `lineage_cycle`;
- `ambiguous_lineage_branch`;
- `conflicting_sale_linkage`;
- `conflicting_inventory_linkage`;
- `multiple_active_terminal_evidence`;
- `unsupported_lifecycle_transition`;
- `conflicting_quantity_history`;
- `timestamp_conflict`;
- `evidence_after_as_of`;
- `non_canonical_ordering`.

Names may vary only through separately reviewed implementation, but semantics may not weaken this boundary.

## Ordering

Canonical output ordering remains:

1. authoritative `completed_at` when present, otherwise `recorded_at`;
2. `recorded_at`;
3. `sale_id`;
4. `inventory_id`;
5. `sale_completion_evidence_id`.

Equivalent evidence sets must produce equivalent validation outcomes and order across runs.

## Explicitly unauthorized

- database schema, migration, table, event-store, or persistence work;
- repository or application-service implementation;
- imports, marketplace APIs, networking, polling, or writes;
- report provider, registration, composition, or live execution;
- UI, preview, chart, or export;
- settlement, allocation, revenue, cost, margin, ranking, recommendation, or trend metrics;
- descriptive or temporal identity inference.

## Next gate

The next controlled build may implement only a pure evidence-set validator, typed conflict codes and outcomes, and focused tests. Repository, storage, service, provider, registration, composition, and UI remain separately gated.
