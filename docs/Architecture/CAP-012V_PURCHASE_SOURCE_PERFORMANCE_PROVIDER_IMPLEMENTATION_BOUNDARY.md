# CAP-012V Purchase Source Performance Provider Implementation Boundary

## Status

Approved planning boundary. This document authorizes a future narrow provider implementation only after repository search confirms the canonical read-only evidence paths described below. It does not itself authorize live execution, composition, registration, UI, persistence, or mutation.

## Authority chain

CAP-012V extends the approved Purchase Source Performance sequence without replacing it:

1. CAP-012O selects the workbook-backed business question and separates acquisition, sale-completion, pricing, settlement, and history authority.
2. CAP-012P fixes exact source-label grouping, closed-period unit grain, and the approved sell-through formula.
3. CAP-012Q defines the planning request/result contract.
4. CAP-012R provides immutable runtime contracts.
5. CAP-012S provides the deterministic pure calculator.
6. CAP-012T provides the fail-closed query boundary and provider protocol.

A provider implementation must conform to CAP-012R through CAP-012T exactly. It may not widen their vocabulary or create alternate report authority.

## Permitted provider responsibility

A future provider may perform one read-only projection for one validated Purchase Source Performance request. It may:

- read canonical Inventory acquisition evidence containing the original purchase-source label, acquired-unit quantity, acquisition date, and stable inventory identity;
- read canonical confirmed sale-completion evidence containing completed-sale unit quantity, completion date, and stable linkage back to the acquired inventory identity;
- restrict both evidence sets to the request's closed reporting period and as-of boundary;
- group only by the exact purchase-source label after the already-approved trim-only normalization;
- aggregate acquired units and confirmed completed-sale units for each exact source label;
- preserve provenance and coverage evidence sufficient for CAP-012T to distinguish available, unavailable, conflicting, unsupported, and invalid outcomes;
- return only the response type accepted by the existing CAP-012T provider protocol.

The pure calculator remains the sole authority for computing `completed_sale_units / acquired_units × 100`. The provider must not duplicate or reinterpret that formula.

## Canonical evidence gate

Before implementation, repository search must identify and document:

- the permanent Inventory acquisition read path and its field-level authority for purchase source, acquired units, acquisition date, and inventory identity;
- the permanent confirmed sale-completion read path and its field-level authority for completed units, completion date, and inventory linkage;
- the exact linkage proving that a completed-sale unit belongs to acquired inventory without inferring from product name, SKU text, marketplace text, source aliases, or price similarity;
- whether partial, missing, duplicated, superseded, or contradictory evidence can occur and how the existing contracts represent those states.

If any required field or linkage lacks canonical authority, the provider must return the existing unavailable or conflict semantics. It must not guess, backfill, alias, rank, or silently omit evidence.

## Request identity and filtering

The provider must preserve the validated request object unchanged. Filtering must be deterministic and use only the request's approved closed-period boundaries and as-of semantics.

The provider must fail closed when:

- the request identity returned by a lower boundary differs from the incoming request;
- the reporting period is not closed under CAP-012R validation;
- source evidence falls outside the approved period or as-of boundary;
- acquisition or sale-completion evidence cannot be linked through canonical stable identity;
- unsupported values, impossible quantities, duplicate authoritative rows, or contradictory evidence are encountered;
- a read exception or unsupported response type occurs.

## Grouping and ordering

- Source labels remain exact after trim-only normalization.
- No case folding, punctuation folding, alias table, marketplace normalization, fuzzy matching, or source-family grouping is permitted.
- Empty labels must use the existing contract semantics rather than a newly invented display label.
- Evidence and result groups must use the deterministic ordering already required by CAP-012R through CAP-012T.

## Provenance and coverage

Each provider response must retain enough immutable evidence for downstream contracts to show:

- the exact request identity;
- the authoritative source domains consulted;
- the reporting-period and as-of coverage actually evaluated;
- the exact source labels encountered;
- whether acquisition and completed-sale evidence were complete, unavailable, or conflicting;
- deterministic evidence ordering.

The provider may not convert incomplete coverage into a valid zero result. Zero sell-through is valid only when acquired units are authoritative and confirmed completed-sale evidence is complete with zero completed units.

## Explicitly unauthorized

CAP-012V does not authorize:

- application composition or dependency registration;
- catalog or report-definition registration;
- live desktop execution;
- UI, presenter, preview factory, chart, export, or operator workflow;
- database schema changes, new persistence, cache tables, snapshots, or materialized views;
- writes, corrections, reconciliation, settlement decisions, or inventory mutations;
- revenue, cost, profit, margin, return, ranking, recommendation, benchmark, or trend calculations;
- source aliasing, source cleanup, fuzzy matching, networking, polling, or marketplace API access.

## Implementation-entry tests

A future provider implementation must include focused tests proving:

1. exact request identity preservation;
2. closed-period and as-of filtering;
3. exact trim-only source grouping;
4. authoritative acquisition-unit aggregation;
5. authoritative confirmed completed-sale-unit aggregation;
6. canonical identity linkage with no text-based inference;
7. valid zero only under complete evidence;
8. unavailable and conflict propagation for incomplete or contradictory evidence;
9. deterministic provenance, coverage, evidence, and group ordering;
10. fail-closed behavior for exceptions, unsupported responses, impossible quantities, duplicates, and mismatched requests;
11. no writes, schema changes, registration, composition, UI, networking, ranking, recommendation, or financial-metric behavior.

## Next gate

After this boundary is merged, the next controlled build may implement only the read-only provider described here. That implementation must remain unregistered and uncomposed until a later separately approved composition boundary.