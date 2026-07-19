# CAP-012C — Inventory Turnover Formula Vocabulary

**Status:** PLAN — formula and vocabulary decision only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #559  
**Baseline:** `main` at `55cab2bd8ad641fc1d739567b39d61c55f7995b9`

## Purpose

This record satisfies the next CAP-012B authority gate for the business question:

> **How quickly does business inventory turn over?**

It approves vocabulary and formula semantics for a future Inventory Turnover report. It does not authorize runtime code, a report definition, a query service, UI, charts, exports, schema changes, or automation.

## Approved formula identity

**Formula ID:** `inventory-turnover-units-v1`  
**Formula name:** Unit-based business inventory turnover  
**Formula family:** Reports / Analytics  
**Primary result:** turnover ratio for eligible business inventory units during an approved period

The formula is intentionally unit-based. It is not an accounting inventory-turnover formula, not revenue turnover, not profit turnover, not settlement completion, and not price performance.

## Approved plain-language definition

Inventory turnover answers:

> Of the eligible business inventory units held during the period, what portion converted into completed sale units during that same period?

A future report may express the result as a ratio and percentage when the numerator, denominator, source coverage, and evidence state are all valid.

## Approved mathematical vocabulary

For an approved period and approved scope:

```text
completed_sale_units_in_period
-------------------------------- = unit_inventory_turnover_ratio
average_eligible_inventory_units_in_period
```

Where:

```text
average_eligible_inventory_units_in_period =
(opening_eligible_inventory_units + closing_eligible_inventory_units) / 2
```

This formula may be computed only when both opening and closing eligible inventory units are reconstructable from approved Inventory and immutable-history evidence.

## Approved period semantics

A future request must use explicit date boundaries.

- `period_start` is inclusive.
- `period_end` is exclusive.
- The period must be fully closed before the report can return a final result.
- If the period is still in progress, the report must label the result as in-progress or return unavailable, depending on the later request contract.
- The report must state its `as_of` value and source coverage.

No default period is approved by this record. A later request contract must explicitly define whether the user, caller, or catalog provides the period.

## Approved population grain

The primary grain is **business inventory unit** grouped through canonical Inventory position evidence.

A future report may group results by product, product category, or other dimensions only when every included unit has an approved canonical linkage for that grouping.

A grouped result must fail closed for the affected group when linkage is missing or contradictory. It must not silently place rows into an invented or guessed group.

## Approved numerator

`completed_sale_units_in_period` means the quantity of eligible business inventory units that reached canonical completed-sale state during the approved period.

The numerator may include only:

- completed sale quantity;
- completed sale date or completed sale event timestamp;
- sale-to-inventory linkage;
- reversal, cancellation, or return evidence only when canonically recorded.

The numerator must not use:

- listing publication alone;
- listing intent;
- price guidance;
- revenue;
- profit;
- settlement verification;
- payment allocation;
- marketplace payout status;
- manual estimates;
- current inventory absence without a sale event.

## Approved denominator

`average_eligible_inventory_units_in_period` means the average of opening and closing eligible business inventory unit counts for the same approved scope.

The denominator may include only business inventory units that are:

- owned or controlled for business inventory purposes at the relevant boundary;
- linked to canonical Inventory evidence;
- not personal Collection-only assets;
- not excluded by approved archive, transfer, or non-sale lifecycle evidence;
- reconstructable at both period boundaries.

If opening or closing quantity cannot be reconstructed, the result is unavailable. The report must not replace the denominator with ending inventory, listing count, acquisition count, product count, sale count, current visible rows, or a best-effort estimate.

## Approved partial-sale semantics

Partial sales are allowed only when quantity evidence is explicit.

- Sold quantity contributes to the numerator in the completed-sale period.
- Remaining quantity continues to belong to the eligible inventory population when Inventory history supports it.
- If quantity split evidence is missing, contradictory, or not reconstructable, the affected unit or group must return unavailable or conflicting.

## Approved cancellation and return semantics

Canceled sales are not completed sale units.

Returns, reversals, and corrections may adjust the numerator only when canonical lifecycle evidence states the relationship to the original sale.

- Same-period reversal: subtract or exclude according to later report-contract wording, but the behavior must be deterministic.
- Cross-period reversal: must preserve source period, correction period, and adjustment reason.
- Missing reversal linkage: fail closed.

No sale may be counted as completed and canceled at the same time.

## Approved archive and transfer semantics

Archive and transfer evidence must not be treated as sale evidence.

- Archive because of completed sale may be considered only when the completed sale event is authoritative.
- Archive for cleanup, deletion, personal move, damage, loss, or unknown reason does not count as turnover.
- Inventory transfer out of business inventory does not count as turnover unless separately tied to completed sale authority.

Unknown archive or transfer reason must fail closed for turnover.

## Approved zero, unavailable, and conflict semantics

The report must distinguish these states:

- **Zero turnover:** denominator is valid and greater than zero, numerator is valid and equals zero.
- **No eligible inventory:** denominator is valid and equals zero, numerator is also zero.
- **Unavailable:** required evidence is missing, period coverage is incomplete, or approved source reconstruction cannot be performed.
- **Conflict:** evidence exists but contradicts required authority, linkage, lifecycle, or quantity rules.

Missing evidence is not zero. Conflicting evidence is not a best-effort estimate.

## Approved exclusions

This formula does not answer:

- gross revenue;
- net revenue;
- profit;
- margin;
- fee impact;
- capital efficiency;
- settlement completion;
- cash-flow timing;
- listing conversion rate;
- sales velocity;
- inventory age;
- price movement;
- market demand.

Those may become separate reports only through separate authority records.

## Source authority boundaries

### Inventory authority

Inventory owns eligible business inventory identity, quantity, current state, lifecycle, acquisition evidence, archive evidence, and product linkage where those are already part of canonical Inventory behavior.

### Sale-completion authority

The completed-sale workflow owns sale completion state, completed quantity, sale-completion timestamp or date, and sale-to-inventory linkage.

### Audit and immutable-history authority

Immutable history supports period-boundary reconstruction, replay, correction detection, contradiction detection, and event provenance.

### Settlement exclusion

Settlement authority does not prove turnover. Settlement may later provide an optional reconciliation label only if a separate authority record approves it. This formula does not wait for payment settlement.

### Pricing and profit exclusion

Pricing, fees, cost guidance, revenue, and profit do not prove turnover. They must not be used as numerator, denominator, or fallback evidence.

## Fail-closed requirements

A future report must not return a numeric turnover result when:

- the period is invalid or ambiguous;
- opening eligible quantity is missing;
- closing eligible quantity is missing;
- completed-sale evidence is missing or contradictory;
- sale-to-inventory linkage is missing or contradictory;
- product or category grouping is requested without canonical linkage;
- partial-sale quantity cannot be reconstructed;
- cancellation, return, archive, or transfer treatment is unresolved;
- current state contradicts immutable history;
- source coverage or freshness cannot be stated;
- denominator is unavailable;
- numerator is unavailable.

The correct outcome in those cases is an explicit unavailable or conflict result with a reason.

## Minimum future report-contract requirements

A later CAP-012D report contract may define request and result objects only if it preserves:

- `formula_id` = `inventory-turnover-units-v1`;
- period start and end;
- scope and grouping;
- source coverage and `as_of` labels;
- opening eligible units;
- closing eligible units;
- average eligible units;
- completed sale units;
- turnover ratio;
- turnover percentage;
- outcome state;
- reason;
- source domains;
- evidence state;
- deterministic ordering;
- explicit unavailable and conflict behavior.

This record does not create those objects. It only authorizes the vocabulary that a later contract must preserve.

## Verification expectations for later runtime work

A later runtime implementation must include tests for:

- valid zero turnover;
- valid positive turnover;
- no eligible inventory;
- missing opening quantity;
- missing closing quantity;
- missing sale linkage;
- partial sale;
- cancellation;
- same-period return;
- cross-period correction;
- archive without sale;
- transfer without sale;
- category grouping with missing linkage;
- source freshness labeling;
- conflict between current state and immutable history;
- deterministic result ordering.

## Non-goals

- runtime code;
- UI behavior;
- a report catalog entry;
- query service logic;
- persistence, schema, migration, or cache;
- chart, dashboard, export, scheduler, alert, notification, or automation;
- mutation of Inventory, Listing, sale, Settlement, Pricing, or audit authority;
- revenue, profit, fee, price-guidance, settlement, or accounting turnover calculations;
- CI workflow or dependency changes.
