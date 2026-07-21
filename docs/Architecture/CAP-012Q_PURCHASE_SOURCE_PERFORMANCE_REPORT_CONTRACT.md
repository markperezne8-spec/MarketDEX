# CAP-012Q — Purchase Source Performance Report Contract

**Status:** PLAN — immutable report contract only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #600  
**Baseline:** `main` at `3255cee25dc5790bc6880e04da393821701a98fa`

## Purpose

This record defines the future immutable, UI-free request/result contract for the Purchase Source Performance vocabulary approved by CAP-012P.

The contract exists so a later runtime build can add request and result objects without inventing formula semantics, source authority, outcome states, grouping behavior, or fail-closed rules.

This document does **not** authorize runtime code, report catalog registration, provider logic, query execution, persistence, schema changes, UI, charts, exports, rankings, recommendations, or mutation authority.

## Business question

> **Which purchase sources produce the strongest business outcomes?**

The initial contract answers this question only through source-grouped unit sell-through. It must not be interpreted as revenue, profit, margin, settlement, return-on-investment, purchasing-quality, or recommendation authority.

## Approved identities

A later contract must preserve these stable identities:

```text
report_id = purchase-source-performance
formula_id = purchase-source-sell-through-units-v1
```

No fallback or alternate formula is approved. Unknown, missing, deprecated, or conflicting identities must fail closed.

## Contract boundary

The future contract is limited to a deterministic read-only request and read-only result collection.

It may define:

- request and formula identity;
- closed period boundaries;
- report as-of value;
- exact purchase-source grouping;
- acquired, completed-sale, and remaining-unit fields;
- explicit outcome and evidence states;
- reason codes and provenance;
- deterministic result ordering.

It must not define:

- source aliases or inferred source identity;
- ranking, winner, loser, recommendation, or threshold semantics;
- product-mix or category normalization;
- revenue, cost, fee, shipping, packaging, profit, margin, or settlement metrics;
- runtime queries, persistence, caching, UI, charts, exports, scheduling, or mutation.

## Future request contract

A later runtime build may define an immutable request object using this conceptual vocabulary:

| Field | Required | Meaning |
| --- | --- | --- |
| `report_id` | yes | Must equal `purchase-source-performance`. |
| `formula_id` | yes | Must equal `purchase-source-sell-through-units-v1`. |
| `period_start` | yes | Inclusive acquisition-period boundary. |
| `period_end` | yes | Exclusive acquisition-period boundary. |
| `as_of` | yes | Latest accepted evidence boundary; must be on or after `period_end`. |
| `scope` | yes | Must identify eligible business inventory. |
| `group_by` | yes | Must equal exact Inventory `purchase_source`. |
| `source_coverage_required` | yes | Required authority coverage labels. |

A request must be immutable once created. Changing any required field creates a different request identity.

No default period, source filter, source alias map, minimum sample threshold, financial metric, ranking mode, or recommendation mode is approved.

## Request validation

A future runtime contract must reject or return `invalid_request` when:

- `report_id` or `formula_id` is missing or does not match the approved identity;
- either period boundary is missing or cannot be parsed deterministically;
- `period_start` is not before `period_end`;
- `as_of` is missing or earlier than `period_end`;
- the requested period is not closed;
- `scope` is missing or unknown;
- `group_by` is absent or differs from exact Inventory `purchase_source`;
- required source coverage cannot be stated;
- the request asks for blocked ranking, recommendation, financial, normalization, chart, or export behavior.

Invalid request shape is not a zero-result condition.

## Approved grouping semantics

Each result group represents one exact non-blank Inventory `purchase_source` label after trimming surrounding whitespace only.

The contract must not merge labels by case, punctuation, spelling similarity, merchant identity, user preference, or inferred alias.

A blank source does not become an `unknown` bucket. It produces an explicit unavailable result or exclusion reason with provenance sufficient to identify the unresolved evidence.

## Future grouped result contract

A later runtime build may define an immutable grouped result object using this conceptual vocabulary:

| Field | Required | Meaning |
| --- | --- | --- |
| `report_id` | yes | Stable report identity. |
| `formula_id` | yes | Stable formula identity. |
| `request_id` | yes | Identity of the request that produced the result. |
| `purchase_source_label` | outcome-dependent | Exact trimmed Inventory source label. |
| `period_start` | yes | Inclusive acquisition boundary used. |
| `period_end` | yes | Exclusive acquisition boundary used. |
| `as_of` | yes | Evidence freshness boundary. |
| `acquired_units` | outcome-dependent | Units acquired from the source during the period. |
| `completed_sale_units` | outcome-dependent | Confirmed sold units from that acquisition population by `as_of`. |
| `remaining_unsold_units` | outcome-dependent | `acquired_units - completed_sale_units` when evidence is valid. |
| `sell_through_ratio` | outcome-dependent | `completed_sale_units / acquired_units`. |
| `sell_through_percentage` | outcome-dependent | Ratio multiplied by 100. |
| `outcome` | yes | Machine-stable result state. |
| `reason` | yes | Machine-stable reason code or deterministic explanation. |
| `source_domains` | yes | Authorities required or consulted. |
| `source_coverage` | yes | Coverage statement for period, scope, and as-of. |
| `evidence_state` | yes | Valid, unavailable, or conflicting evidence state. |
| `provenance` | yes | Source-field and source-domain traceability. |

Numeric fields must be absent, null, or explicitly unavailable when the outcome does not permit calculation.

A conflicting result must never expose a best-effort percentage.

## Approved formula semantics

For a valid group:

```text
sell_through_ratio = completed_sale_units / acquired_units
sell_through_percentage = sell_through_ratio * 100
remaining_unsold_units = acquired_units - completed_sale_units
```

Rules:

- `acquired_units` must be greater than zero;
- zero confirmed completed-sale units with complete evidence is valid zero sell-through;
- partial sales contribute only explicitly confirmed sold quantity;
- unsold units remain in the denominator;
- missing evidence is not zero;
- conflicting evidence is not resolved by estimation or source preference.

## Approved outcome states

The minimum approved outcomes are:

```text
valid
zero_sell_through
unavailable
conflict
invalid_request
```

### `valid`

Use when request shape, period, source label, acquisition population, completed-sale linkage, quantities, source coverage, and provenance are complete and non-conflicting, with `acquired_units > 0`.

### `zero_sell_through`

Use when the denominator is valid and greater than zero and confirmed completed-sale units equal zero.

### `unavailable`

Use when required acquisition, source, sale, linkage, period coverage, freshness, quantity, or immutable-history evidence is missing or cannot be reconstructed.

### `conflict`

Use when evidence exists but canonical sources contradict one another, including ambiguous inventory-to-sale linkage, contradictory quantities, or current state inconsistent with immutable history.

### `invalid_request`

Use when the request cannot be interpreted under this contract.

## Source authority requirements

A future result must preserve authority labels at minimum for:

- Inventory purchase source, acquisition date, quantity, cost, and product linkage;
- confirmed sale completion, sold quantity, revenue, fees, shipping, packaging, and inventory decrement;
- immutable history for lifecycle reconstruction and conflict detection;
- Pricing/profit exclusion from the approved unit sell-through formula;
- Settlement exclusion from proof of completed sale unless later authority explicitly changes that boundary.

Financial fields may appear in provenance only to identify excluded authority; they must not influence this formula.

## Provenance requirements

A future result must preserve provenance sufficient to explain:

- which Inventory fields supplied the purchase-source label, acquisition date, and acquired quantity;
- which confirmed-sale fields supplied completed sold quantity;
- how sale units were linked to the acquisition population;
- which immutable-history evidence was consulted;
- period and as-of coverage;
- why evidence was valid, unavailable, or conflicting;
- why any numeric field was withheld.

Provenance must remain test-visible even if later presentation is simplified.

## Deterministic ordering

A future result collection must preserve the CAP-012P ordering:

1. valid before unavailable before conflicting evidence;
2. sell-through percentage descending for valid groups;
3. completed-sale units descending;
4. acquired units descending;
5. normalized purchase-source label ascending using deterministic case-folded comparison;
6. original purchase-source label ascending as final tie breaker.

This ordering is presentation stability only. It is not business ranking or recommendation authority.

## Fail-closed requirements

A future contract must not return a numeric source-performance result when:

- request validation fails;
- source coverage or freshness cannot be stated;
- purchase source is blank or unresolved;
- acquisition date or acquired quantity is missing or contradictory;
- the acquisition population cannot be reconstructed;
- completed-sale evidence is missing or contradictory;
- sale-to-inventory linkage is missing or ambiguous;
- partial-sale quantity is missing or contradictory;
- an excluded return, refund, cancellation, transfer, write-off, or cross-period correction affects the row without later authority;
- current state conflicts with immutable history;
- acquired units are zero or unavailable;
- formula or report identity does not match.

The required response is `unavailable`, `conflict`, or `invalid_request` with a reason and provenance.

## Future verification requirements

A later runtime slice must include focused tests for:

- immutable request construction;
- report and formula identity rejection;
- invalid or open period rejection;
- `as_of` earlier than period end rejection;
- exact-label grouping with trim-only normalization;
- no alias or case merging;
- valid positive sell-through;
- valid zero sell-through;
- unsold units retained in the denominator;
- partial-sale quantity preservation;
- blank source failing closed;
- missing acquisition quantity;
- missing completed-sale evidence;
- missing or ambiguous sale-to-inventory linkage;
- contradictory quantities;
- current state conflicting with immutable history;
- excluded lifecycle evidence failing closed;
- Pricing, profit, and Settlement not used as formula proof;
- provenance fields present;
- deterministic ordering.

## Acceptance gate for later runtime work

A later implementation may begin only through a separate issue approving one isolated scope, such as:

1. immutable request/result dataclasses only;
2. report catalog registration only;
3. provider/query boundary only;
4. deterministic query implementation only;
5. read-only presentation only.

No later build may combine formula changes, authority changes, provider implementation, UI, charts, exports, recommendations, and persistence into one uncontrolled slice.

## Non-goals

- runtime code or UI behavior;
- report catalog registration;
- provider, calculator, query service, or live execution;
- persistence, schema, migration, cache, or duplicate reporting storage;
- ranking, recommendation, source scoring, aliases, or product-mix normalization;
- revenue, profit, margin, fee, shipping, packaging, settlement, or accounting calculations;
- chart, dashboard, export, scheduler, alert, notification, or automation;
- mutation of Inventory, Sales, Pricing, Settlement, or immutable-history authority;
- dependency or CI workflow changes.
