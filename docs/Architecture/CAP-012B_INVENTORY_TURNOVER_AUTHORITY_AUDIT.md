# CAP-012B — Inventory Turnover Authority Audit

**Status:** PLAN — authority audit only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #557  
**Baseline:** `main` at `277ed5b7c74e4e1aeceda98edc928fb5be5e98cb`

## Selected business question

> **How quickly does business inventory turn over?**

`WorkbookBlueprint.md` identifies Inventory turnover as an Analytics responsibility. This record selects that business question for authority analysis only. It does not authorize a formula, report definition, query, user interface, threshold, recommendation, chart, or export.

## Why this is the next candidate

The delivered Inventory Age report answers how long one inventory position has been held as of a selected date. Inventory turnover is related but materially different: it requires a period-based relationship between business inventory held and completed sale evidence.

The candidate is useful because it may reveal whether inventory is converting into completed business outcomes efficiently. It is also authority-sensitive because Inventory, Listing/sale completion, Pricing, Settlement, and immutable history own different facts that must not be collapsed.

## Existing source authorities

### Inventory may provide

- canonical business-held asset or inventory-position identity;
- quantity and lifecycle state;
- acquisition date and source evidence;
- cost evidence already owned by Inventory;
- archive or current-state evidence where explicitly recorded;
- inventory-to-product linkage.

### Listing and sale-completion authority may provide

- listing-plan and publication lifecycle evidence;
- sale completion only when the canonical sale workflow records it as completed;
- completed quantity and completion date where explicitly available;
- reversals, cancellations, or other lifecycle evidence only when canonically recorded.

### Audit and immutable history may provide

- append-only event evidence needed to reconstruct approved period activity;
- event identity, timestamps, and replay-safe historical proof;
- contradiction evidence where current state and history disagree.

### Settlement may not be substituted

Settlement verification, allocation, revision, and lock evidence must not be treated as proof of inventory turnover unless a later authority decision explicitly requires settlement completion. A completed sale and a settled payment are separate business facts.

### Pricing and profit may not be substituted

Revenue, profit, price guidance, fees, and cost-impact calculations are not turnover authority. A turnover report must not silently become a profitability report.

## Required distinctions

A later design must preserve these differences:

- **Inventory age:** elapsed time for one position as of a date.
- **Inventory turnover:** period-based conversion of held business inventory into completed sale activity under an approved formula.
- **Sales velocity:** frequency or pace of sale events, which may use a different denominator.
- **Sell-through rate:** units sold relative to an approved available or listed population.
- **Settlement completion:** payment evidence after sale activity.
- **Revenue or profit performance:** financial outcomes owned by separate calculations.

No label may be used interchangeably without approved definitions and tests.

## Blocked authority decisions

The following remain **BLOCKED** and must not be invented in code, schema, tests, or UI:

1. **Measurement period** — daily, weekly, monthly, rolling, calendar, or user-selected boundaries.
2. **Turnover formula** — numerator, denominator, averaging method, and whether the result is a rate, ratio, days, or another unit.
3. **Population grain** — asset, inventory position, product, lot, unit, category, or another approved grain.
4. **Inventory denominator** — beginning inventory, ending inventory, average inventory, available inventory, listed inventory, cost basis, units, or another measure.
5. **Sale numerator** — completed units, completed positions, cost of goods sold, sale events, or another measure.
6. **Partial sales** — treatment of partially sold quantities and remaining positions.
7. **Returns and cancellations** — inclusion, reversal, and period reassignment rules.
8. **Archived or transferred inventory** — whether and when it remains in the population.
9. **Zero and unavailable evidence** — distinction between zero turnover and insufficient evidence.
10. **Cross-period corrections** — handling of late, revised, contradictory, or replayed events.
11. **Category aggregation** — whether product categories may be compared and under what normalization.
12. **Freshness and as-of semantics** — exact source coverage and current-versus-historical labeling.

## Fail-closed requirements

Any later query must return an explicit unavailable or conflicting outcome rather than a numeric result when:

- the approved period cannot be established;
- required Inventory or sale-completion evidence is missing;
- inventory-product or sale linkage is ambiguous;
- current state contradicts immutable history;
- partial-sale, return, cancellation, or archive treatment cannot be resolved;
- the approved numerator or denominator cannot be reconstructed;
- source coverage is incomplete or freshness cannot be stated.

Missing evidence is not zero. Conflicting evidence is not a best-effort estimate.

## Candidate read-model boundary

A later immutable, UI-free contract may be considered only after the blocked decisions are approved. The eventual read model would need to preserve at minimum:

- report and formula version identity;
- period start and end;
- population grain;
- numerator and denominator meaning;
- source domains and coverage;
- evidence state and reason;
- as-of and freshness labels;
- explicit unavailable and conflicting outcomes;
- deterministic ordering for any grouped results.

These are planning requirements, not approved implementation fields.

## Acceptance gate for CAP-012C

A later CAP-012C implementation issue may begin only when repository authority contains:

- an approved turnover formula and vocabulary;
- approved period and population-grain rules;
- approved partial-sale, return, cancellation, archive, and correction semantics;
- exact source-query ownership for Inventory and completed-sale evidence;
- explicit settlement and Pricing exclusions or dependencies;
- immutable request, result, provenance, and fail-closed contracts;
- focused verification requirements;
- a separately scoped GitHub issue and branch.

Until that gate is satisfied, the existing catalog-only Inventory Age report remains the maximum approved Reports runtime behavior.

## Non-goals

- runtime code or UI behavior;
- a new report definition or query service;
- formula, threshold, recommendation, or classification logic;
- provider, persistence, schema, migration, cache, or duplicated reporting storage;
- chart, dashboard, export, scheduler, alert, notification, or automation;
- mutation of Inventory, Listing, sale, Settlement, Pricing, or audit authority;
- dependency or CI workflow changes.
