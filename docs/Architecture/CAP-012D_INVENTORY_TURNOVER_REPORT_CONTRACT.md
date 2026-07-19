# CAP-012D — Inventory Turnover Report Contract

**Status:** PLAN — immutable report contract only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #561  
**Baseline:** `main` at `bebfabef7fc9002572ed6167e9f609cf2dcaeccc`

## Purpose

This record defines the future immutable, UI-free request/result contract for the approved CAP-012C formula:

```text
formula_id = inventory-turnover-units-v1
```

The contract exists so a later runtime build can add request and result objects without inventing formula semantics, source authority, outcome states, grouping behavior, or fail-closed rules.

This document does **not** authorize runtime code, a report catalog entry, a query service, provider logic, persistence, schema changes, UI, charts, exports, automation, alerts, or mutation authority.

## Business question

> **How quickly does business inventory turn over?**

The report answers this question only through the approved unit-based formula vocabulary from CAP-012C. It must not become an accounting turnover report, revenue report, profit report, settlement report, sales velocity report, sell-through report, or inventory age report.

## Contract boundaries

The future contract is limited to a deterministic read-only report request and read-only report result.

It may define:

- request identity;
- formula identity;
- period boundaries;
- requested scope;
- requested grouping;
- as-of and source coverage labels;
- result rows;
- outcome state;
- reason codes;
- provenance fields;
- deterministic ordering.

It must not define:

- data mutation;
- persistence tables;
- cache policy;
- user interface layout;
- report catalog registration;
- query implementation;
- chart configuration;
- export format;
- automated scheduling;
- business recommendations.

## Approved formula dependency

All future contract objects must preserve:

```text
formula_id: inventory-turnover-units-v1
```

No caller may substitute another formula ID. No fallback formula is approved.

A later runtime implementation must fail closed if the requested formula ID is missing, unknown, deprecated, or inconsistent with this report contract.

## Future request contract

A later runtime build may define an immutable request object with the following conceptual fields.

These names are approved as contract vocabulary, not yet as Python class fields.

| Field | Required | Meaning |
| --- | --- | --- |
| `report_id` | yes | Stable report identity for inventory turnover. |
| `formula_id` | yes | Must equal `inventory-turnover-units-v1`. |
| `period_start` | yes | Inclusive period boundary. |
| `period_end` | yes | Exclusive period boundary. |
| `scope` | yes | Approved business inventory scope. |
| `group_by` | no | Optional approved grouping dimension. |
| `as_of` | yes | Time at which source coverage is evaluated. |
| `include_in_progress_period` | no | Whether an in-progress period may return an in-progress outcome instead of unavailable. |
| `source_coverage_required` | yes | Required source-domain coverage labels. |

A request must be immutable once created. A change to any required field creates a different request identity.

## Request validation rules

A future runtime contract must reject or return unavailable for a request when:

- `formula_id` does not equal `inventory-turnover-units-v1`;
- `period_start` is missing;
- `period_end` is missing;
- `period_start` is not before `period_end`;
- the period boundary format cannot be parsed deterministically;
- `scope` is missing or unknown;
- `group_by` is not an approved grouping dimension;
- `as_of` is missing;
- required source coverage cannot be stated;
- an in-progress period is requested without approved in-progress semantics.

Invalid request shape is not a zero-result condition.

## Approved period semantics

The request must preserve these CAP-012C period rules:

- `period_start` is inclusive;
- `period_end` is exclusive;
- final results require a closed period;
- in-progress periods must be explicitly labeled or unavailable;
- every result must state `as_of` and source coverage.

No default period is approved by this contract. A later report catalog entry may choose a default only through a separate approved runtime slice.

## Approved scope vocabulary

The first approved conceptual scope is:

```text
business_inventory
```

This scope means eligible business inventory units, not personal Collection-only assets and not generic product registry rows.

A later runtime build may add stricter scope fields only if they preserve the Inventory authority boundary and do not infer eligibility from Pricing, Settlement, Listing intent, or current row visibility alone.

## Approved grouping vocabulary

Initial grouping may be absent, meaning a whole-scope result.

Potential grouping dimensions are contract placeholders only until implemented:

- `product_id`;
- `product_category`;
- `storage_location`;
- `purchase_source`.

A future grouped result may be returned only when every included unit has canonical linkage for the requested grouping. Missing or contradictory linkage must fail closed for the affected row or group.

No unknown bucket, guessed category, inferred product, or fallback grouping is approved.

## Future result contract

A later runtime build may define an immutable result object with these conceptual fields.

| Field | Required | Meaning |
| --- | --- | --- |
| `report_id` | yes | Stable report identity. |
| `formula_id` | yes | Must equal `inventory-turnover-units-v1`. |
| `request_id` | yes | Identity of the request that produced the result. |
| `period_start` | yes | Inclusive period boundary used. |
| `period_end` | yes | Exclusive period boundary used. |
| `scope` | yes | Scope used after validation. |
| `group_key` | no | Deterministic group identity when grouped. |
| `group_label` | no | Display-safe label when grouped. |
| `opening_eligible_inventory_units` | outcome-dependent | Opening denominator component. |
| `closing_eligible_inventory_units` | outcome-dependent | Closing denominator component. |
| `average_eligible_inventory_units` | outcome-dependent | Formula denominator. |
| `completed_sale_units` | outcome-dependent | Formula numerator. |
| `turnover_ratio` | outcome-dependent | Numeric ratio when valid. |
| `turnover_percentage` | outcome-dependent | Percentage representation when valid. |
| `outcome` | yes | Result state. |
| `reason` | yes | Machine-stable reason code or human-readable reason. |
| `source_domains` | yes | Source authorities consulted or required. |
| `source_coverage` | yes | Coverage statement for requested period and scope. |
| `evidence_state` | yes | Evidence quality state. |
| `as_of` | yes | Freshness timestamp or label. |
| `provenance` | yes | Source-field and source-domain traceability. |

Outcome-dependent numeric fields must be absent, null, or explicitly unavailable when the outcome is not valid for numeric calculation.

A conflict must never expose a best-effort numeric turnover value.

## Approved outcome states

A future result must use explicit outcome states. The minimum approved states are:

```text
valid
zero_turnover
no_eligible_inventory
in_progress
unavailable
conflict
invalid_request
```

### `valid`

Use when the numerator, denominator, period, source coverage, and evidence state are all valid and the denominator is greater than zero.

### `zero_turnover`

Use when the denominator is valid and greater than zero, and the completed sale units are valid and equal zero.

### `no_eligible_inventory`

Use when opening and closing eligible inventory units are both valid and equal zero, and completed sale units are also zero.

### `in_progress`

Use only when the request explicitly permits in-progress periods and the future runtime contract can state source coverage and freshness without pretending the period is final.

### `unavailable`

Use when required evidence, coverage, denominator reconstruction, numerator reconstruction, linkage, or freshness is missing.

### `conflict`

Use when evidence exists but contradicts required authority, lifecycle, quantity, linkage, grouping, correction, return, archive, transfer, or immutable-history rules.

### `invalid_request`

Use when the request itself cannot be interpreted according to this contract.

## Approved numeric field semantics

When outcome permits numeric calculation:

```text
average_eligible_inventory_units =
(opening_eligible_inventory_units + closing_eligible_inventory_units) / 2
```

```text
turnover_ratio =
completed_sale_units / average_eligible_inventory_units
```

```text
turnover_percentage =
turnover_ratio * 100
```

Numeric results require valid numerator and denominator evidence. The report must not divide by zero. The report must not substitute ending inventory, current visible rows, listing count, product count, acquisition count, sale count, revenue, cost basis, profit, settlement state, or estimates for denominator evidence.

## Source authority requirements

A future result must preserve source authority labels at minimum for:

- Inventory authority;
- completed-sale authority;
- immutable-history authority;
- Settlement exclusion or separately approved dependency;
- Pricing and profit exclusion.

The result must make it clear that Settlement and Pricing are not proof of turnover under `inventory-turnover-units-v1`.

## Provenance requirements

A future result must preserve provenance sufficient to explain:

- which source domains were required;
- which source domains were consulted;
- which source fields supported period boundaries;
- which source fields supported opening quantity;
- which source fields supported closing quantity;
- which source fields supported completed sale quantity;
- which source fields supported grouping;
- which source fields produced unavailable or conflict states;
- source freshness and `as_of` labeling.

Provenance must be visible to tests even if a later UI chooses a simplified display.

## Deterministic ordering

A future result collection must be deterministic.

For ungrouped output, there is one result row.

For grouped output, rows must be ordered by stable group key, not by dictionary order, database incidental order, UI order, or source arrival order.

Ties must be deterministic.

## Fail-closed requirements

A future contract must not return a numeric turnover result when:

- request validation fails;
- source coverage cannot be stated;
- opening eligible inventory units cannot be reconstructed;
- closing eligible inventory units cannot be reconstructed;
- completed sale units cannot be reconstructed;
- sale-to-inventory linkage is missing;
- grouping linkage is missing for a grouped result;
- partial-sale quantity is missing or contradictory;
- cancellation evidence contradicts completed sale evidence;
- return or reversal evidence cannot be linked to the original sale;
- archive reason is unknown or not tied to sale authority;
- transfer evidence is mistaken for sale evidence;
- current state contradicts immutable history;
- denominator is unavailable;
- numerator is unavailable;
- formula identity does not match.

The required response is `unavailable`, `conflict`, or `invalid_request` with a reason.

## Future verification requirements

A later runtime slice must include focused tests for:

- immutable request construction;
- formula ID rejection;
- invalid period rejection;
- valid positive turnover result;
- valid zero turnover result;
- no eligible inventory result;
- in-progress period labeling or unavailable behavior;
- missing opening quantity;
- missing closing quantity;
- missing completed sale evidence;
- missing sale-to-inventory linkage;
- partial-sale quantity preservation;
- cancellation exclusion;
- same-period return behavior;
- cross-period correction behavior;
- archive without sale failing closed;
- transfer without sale failing closed;
- grouped result with missing linkage failing closed;
- Settlement not used as turnover proof;
- Pricing not used as turnover proof;
- provenance fields present;
- deterministic ordering.

## Acceptance gate for later runtime work

A later runtime implementation may begin only after a separate issue approves one of these scopes:

1. immutable request/result dataclasses only;
2. report catalog registration only;
3. query boundary/provider contract only;
4. deterministic query implementation only;
5. read-only UI presentation only.

No later build may combine formula changes, source authority changes, query implementation, UI, charts, exports, and persistence into one uncontrolled slice.

## Non-goals

- runtime code;
- UI behavior;
- report catalog registration;
- query service or provider implementation;
- persistence, schema, migration, cache, or duplicate reporting storage;
- chart, dashboard, export, scheduler, alert, notification, or automation;
- mutation of Inventory, Listing, sale, Settlement, Pricing, or audit authority;
- revenue, profit, fee, price-guidance, settlement, or accounting turnover calculations;
- CI workflow or dependency changes.
