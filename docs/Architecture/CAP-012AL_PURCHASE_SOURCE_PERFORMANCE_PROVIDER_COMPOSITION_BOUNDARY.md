# CAP-012AL — Purchase Source Performance Provider Composition Boundary

## Status
Planning authority only. Provider implementation remains unauthorized until this boundary is reviewed and merged.

## Purpose
Define the smallest read-only, constructor-injected provider boundary that can supply the existing `PurchaseSourcePerformanceQueryService` with deterministic evidence derived from canonical Inventory acquisition authority and the CAP-012AK sale-completion query consumer.

## Existing authority preserved

- `PurchaseSourcePerformanceRequest`, immutable evidence/result contracts, the pure calculator, and the fail-closed query service remain the report contract authority.
- Inventory remains the sole authority for acquired-inventory identity, acquired units, purchase date, and exact trim-only purchase-source label.
- `SaleCompletionQueryService` remains the application-service seam for canonical completed-sale evidence and preserves available, unavailable, conflict, diagnostic, and reason-code outcomes unchanged.
- Settlement and settlement-allocation evidence do not substitute for completed-sale authority.

## Required provider dependencies
A future provider must receive all dependencies through its constructor:

1. one read-only Inventory acquisition reader exposing canonical inventory identity, acquired units, purchase date, and purchase-source label;
2. one `SaleCompletionQueryService` instance;
3. no concrete SQLite imports, globals, service locators, fallback sources, caches, retries, networking, or hidden runtime construction.

The provider owns orchestration only. It does not own persistence, schema, domain mutation, repository lifecycle, report presentation, or application composition.

## Request translation

For one validated `PurchaseSourcePerformanceRequest`:

- `period_start` is inclusive;
- `period_end` is exclusive;
- `as_of` is the maximum evidence time and must not precede the reporting period;
- Inventory acquisition reads are restricted to canonical acquisitions inside the requested closed period;
- sale-completion reads are scoped only by the canonical inventory identities returned by the acquisition reader;
- the sale-completion query uses the same closed-period boundaries and converts report dates to explicit timezone-aware instants through one documented timezone policy;
- no sale or acquisition may be inferred from labels, descriptions, prices, marketplaces, timestamps, settlement rows, or financial coincidence.

## Identity and aggregation grain

- Canonical inventory identity is the join key between acquisition and sale-completion evidence.
- Purchase-source grouping uses the exact trimmed Inventory label.
- Case folding may be used only for deterministic ordering, never for grouping or aliasing.
- Acquired units are summed from authoritative Inventory acquisition rows.
- Completed-sale units are summed only from canonical active completed-sale evidence linked to those inventory identities and inside the same reporting period.
- Cancelled, refunded, reversed, superseded, conflicting, unavailable, or out-of-period evidence must not silently contribute units.

## Coverage reconciliation

The provider may return valid evidence only when both source domains prove complete coverage for the exact request and identity set.

- Inventory unavailable or incomplete coverage yields typed unavailable evidence.
- Sale-completion unavailable coverage yields typed unavailable evidence.
- Conflicting Inventory identity, quantity, label, date, or sale-completion evidence yields typed conflicting evidence.
- A successful complete read with no qualifying rows may return a deterministic empty or zero-result evidence set only as permitted by the existing CAP-012R through CAP-012T contracts.
- Partial success is prohibited. The provider must not drop problematic rows and continue as valid.

Diagnostics and reason codes from the sale-completion read must remain available in provider provenance or typed conflict/unavailable detail; they must not be replaced with a generic success state.

## Evidence mapping

For each exact purchase-source label, the provider creates one `PurchaseSourcePerformanceEvidence` value containing:

- exact purchase-source label;
- authoritative acquired-unit total;
- authoritative completed-sale-unit total;
- source domains covering Inventory acquisition and sale completion;
- explicit complete, unavailable, or conflicting coverage;
- deterministic provenance identifying both read boundaries and the request period;
- the matching evidence state and fail-closed reason when applicable.

The provider returns `PurchaseSourcePerformanceQueryResponse` for the unchanged request. The existing query service validates request identity and the existing calculator remains the only authority for `completed_sale_units / acquired_units × 100`.

## Deterministic ordering
Evidence is ordered by:

1. `purchase_source_label.casefold()`;
2. exact `purchase_source_label`;
3. evidence state.

Repository or database row order must never affect the response.

## Next implementation slice
After this boundary is merged, the next separately approved slice may implement one pure orchestration provider behind `PurchaseSourcePerformanceEvidenceProvider` with in-memory fakes and focused contract tests.

That implementation must remain UI-free and composition-free. Runtime registration, concrete Inventory adapter selection, application composition, catalog registration, presentation binding, and live workspace execution each require separate approval.

## Explicit exclusions
No schema, migration, persistence, writes, inventory mutation, sale mutation, settlement authority, report catalog registration, application composition, live execution, UI, chart, export, ranking, recommendation, financial metric, source aliasing, networking, polling, fallback, retry, cache, or background task is authorized.