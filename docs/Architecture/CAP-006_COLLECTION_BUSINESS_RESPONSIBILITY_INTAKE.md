# CAP-006 — Collection Business Responsibility Intake

**Status:** PLAN — awaiting Spreadsheet Design authority  
**Source boundary:** M19 authoritative workbook, `❤️ Collection` / `CALC V0 · BUILD 007`  
**Implementation status:** No Collection schema, service, repository, or UI is authorized

## Confirmed facts

The M19 workbook identifies the Collection worksheet as:

- a protected worksheet responsibility;
- a business interface that is not yet implemented;
- a surface protected from speculative formulas, fake metrics, and architecture redesign.

The permanent repository therefore has enough evidence to define the design questions, but not enough authority to invent Collection fields or lifecycle rules.

## Responsibility questions requiring approval

| Decision area | Question to resolve | Current status |
|---|---|---|
| Position identity | What stable identity represents one Collection Position, and how does it reference canonical `product_id`? | OPEN |
| Quantity | Is quantity held as one position quantity, lot-level quantities, or another workbook-defined grain? | OPEN |
| Acquisition evidence | Which acquisition, receiving, cost, and provenance fields are required for a Collection Position? | OPEN |
| Condition and grade | Which condition and grading fields are authoritative, optional, or derived? | OPEN |
| Collector intent | Which approved values represent keep, trade, sell willingness, favorite, never-sell, and collection goals? | OPEN |
| Custody and location | Which location and custody transitions must be recorded as evidence? | OPEN |
| Lifecycle | Which transitions are valid for acquire, adjust, transfer, archive, restore, and intent change? | OPEN |
| Inventory relationship | When may one product have both Inventory and Collection Positions, and what event or explicit operator decision relates them? | OPEN |
| Valuation | Is value a source observation, a derived read model, or outside the first Collection slice? | OPEN |
| History | Which mutations require append-only events, audit evidence, replay defense, and restart reconstruction? | OPEN |
| Overview | Which minimum read-only Collection Overview questions must the first workspace answer? | OPEN |

## Required design output

Spreadsheet Design should produce one accepted responsibility contract containing:

1. field vocabulary and ownership for Collection Position;
2. position grain and stable identity rules;
3. valid lifecycle and intent transitions;
4. Inventory and Product Registry relationship rules;
5. command, query, event, repository, persistence, and read-model boundaries;
6. examples for empty, unmatched, duplicate, conflicting, replayed, and restarted cases;
7. a first-workspace acceptance statement and metric ownership;
8. explicit non-goals for Portfolio, Reports & Insights, valuation, grading, wishlist, and market-data expansion.

## Implementation gate

CAP-006 may move from PLAN to BUILD only after the responsibility contract is accepted and recorded in repository authority. Until then:

- do not add Collection tables or migrations;
- do not copy Inventory tables into a Collection schema;
- do not promote placeholder `app/ui/` Collection surfaces into the root shell;
- do not infer enum values, transitions, metrics, or valuation formulas;
- do not create a second ownership authority.

## Next action

Resolve the OPEN decisions through Spreadsheet Design, then update this intake document with the accepted vocabulary and link it to the first implementation work order.
