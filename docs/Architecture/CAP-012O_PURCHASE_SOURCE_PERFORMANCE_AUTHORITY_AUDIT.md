# CAP-012O — Purchase Source Performance Authority Audit

**Status:** PLAN — authority audit only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #596  
**Baseline:** `main` at `d6a18d911d8be2cdf58b31cc4defaa069acc47f4`

## Selected business question

> **Which purchase sources produce the strongest business outcomes?**

`WorkbookBlueprint.md` assigns purchase-source performance to Analytics. This record selects that question for authority analysis only. It does not authorize a formula, report definition, query, user interface, ranking, recommendation, chart, or export.

## Operator decision supported

A later approved report may help the operator decide where future inventory-acquisition effort and capital deserve attention. It must not imply that one source is universally better without approved period, product-mix, evidence-coverage, and outcome rules.

## Existing source authorities

### Inventory may provide

- canonical asset or inventory-position identity;
- purchase source exactly as recorded;
- acquisition date, quantity, and cost evidence;
- product/category linkage;
- current, archived, transferred, or sold status where canonically recorded.

### Confirmed sale completion may provide

- explicit operator-confirmed `SOLD` evidence;
- completed quantity and completion date;
- recorded revenue, marketplace fees, shipping cost, and packaging cost;
- the single authoritative inventory decrement and sales financial-history event.

### Pricing and profit may provide

- approved derived profit or cost-impact calculations only through their existing authority;
- no replacement for source identity, sale completion, or inventory lifecycle evidence.

### Audit and immutable history may provide

- replay-safe event identity and timestamps;
- historical source, inventory, and sale evidence where canonically preserved;
- contradiction evidence when current state and history disagree.

### Settlement may not be substituted

Settlement evidence is payment authority, not purchase-source or sale-completion authority. A source-performance report must not require settlement completion unless a later decision explicitly approves that dependency.

## Required distinctions

- **Purchase-source volume:** quantity or cost acquired from a source.
- **Purchase-source sell-through:** approved sold population relative to an approved acquired or available population.
- **Purchase-source profit:** approved financial outcome from sold inventory.
- **Purchase-source turnover:** period-based inventory conversion, not source profitability.
- **Sales-channel performance:** outcome by selling channel, not acquisition source.
- **Product/category performance:** outcome by product identity or category, which may confound source comparisons.

No label may be used interchangeably without an approved definition and focused tests.

## Blocked authority decisions

The following remain blocked and must not be invented in runtime code, schema, tests, or UI:

1. Measurement period and as-of semantics.
2. Population grain: asset, position, lot, unit, product, category, or source transaction.
3. Source identity normalization, aliases, blanks, and renamed sources.
4. Outcome definition: sold units, sell-through, revenue, gross profit, net profit, margin, turnover, or another measure.
5. Denominator: acquired units, acquired cost, available units, listed units, or another population.
6. Treatment of unsold and partially sold inventory.
7. Returns, cancellations, refunds, and reversals.
8. Archived, transferred, personal-collection, or written-off inventory.
9. Cross-period acquisition and sale treatment.
10. Product-mix and category normalization.
11. Minimum sample size and sparse-source handling.
12. Missing, conflicting, or stale evidence behavior.
13. Ranking, threshold, recommendation, and tie-breaking rules.
14. Currency, fee, shipping, packaging, and cost-basis semantics.

## Fail-closed requirements

Any later query must return an explicit unavailable or conflicting outcome rather than a ranking or numeric result when:

- purchase source is missing or ambiguous;
- required acquisition, quantity, cost, or sale evidence is missing;
- source aliases cannot be resolved deterministically;
- inventory and sale linkage is ambiguous;
- current state contradicts immutable history;
- partial-sale, return, cancellation, archive, or transfer treatment is unresolved;
- the approved numerator or denominator cannot be reconstructed;
- period coverage, freshness, or product-mix scope cannot be stated.

Missing evidence is not zero. Conflicting evidence is not a best-effort estimate. A source with no completed sales is not automatically an underperforming source.

## Candidate read-model boundary

A later immutable, UI-free contract may be considered only after the blocked decisions are approved. It would need to preserve at minimum:

- report and formula/version identity;
- period start, period end, and as-of date;
- source identity and normalization provenance;
- population grain and product/category scope;
- numerator, denominator, and financial-vocabulary meaning;
- source domains and coverage;
- evidence state and reason;
- explicit unavailable and conflicting outcomes;
- deterministic ordering and tie behavior for grouped results.

These are planning requirements, not approved implementation fields.

## Acceptance gate for a later implementation issue

Implementation may begin only when repository authority contains:

- approved source identity and normalization rules;
- approved outcome, denominator, grain, period, and as-of vocabulary;
- approved partial-sale, unsold, return, cancellation, archive, transfer, and correction semantics;
- exact query ownership for Inventory, sale completion, Pricing/profit, and audit evidence;
- explicit Settlement exclusions or dependencies;
- immutable request, result, provenance, grouping, and fail-closed contracts;
- focused verification requirements;
- a separately scoped GitHub issue and branch.

Until that gate is satisfied, Inventory Age Patterns and Inventory Turnover remain the only approved Reports runtime behavior.

## Non-goals

- runtime code or UI behavior;
- a new report catalog entry or query service;
- formula, threshold, ranking, recommendation, or classification logic;
- provider, persistence, schema, migration, cache, or duplicated reporting storage;
- chart, dashboard, export, scheduler, alert, notification, or automation;
- mutation of Inventory, Listing, Sales, Settlement, Pricing, or audit authority;
- dependency or CI workflow changes.
