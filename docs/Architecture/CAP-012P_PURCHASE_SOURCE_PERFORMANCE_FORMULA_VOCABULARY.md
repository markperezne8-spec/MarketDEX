# CAP-012P — Purchase Source Performance Formula Vocabulary

**Status:** APPROVED — planning and contract authority only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #598  
**Baseline:** `main` at `f9e4f6a5ca45682e0fc7429a851355b7845c047e`

## Approved business question

> **Which purchase sources produce the strongest business outcomes?**

This decision approves a conservative source-performance vocabulary for a later immutable, UI-free contract. It does not authorize runtime execution, a report catalog entry, ranking, recommendation, chart, or export.

## Approved comparison boundary

- **Grouping key:** the exact non-blank `purchase_source` value recorded by Inventory.
- **Normalization:** trim surrounding whitespace only. No alias merging, fuzzy matching, renaming, or inferred source identity.
- **Population grain:** inventory units.
- **Acquisition population:** units acquired from the grouped source whose acquisition date falls within the closed measurement period.
- **Completed-sale population:** units from that acquisition population with explicit canonical `SOLD` completion evidence by the report as-of date.
- **Period:** a closed, user-supplied start-inclusive/end-exclusive interval.
- **As-of:** must be on or after the period end and must identify the latest accepted evidence included.

## Approved primary metric

**Purchase-source sell-through percentage**

`completed_sale_units / acquired_units × 100`

Rules:

- `acquired_units` must be greater than zero.
- Zero completed-sale units with complete evidence produces a valid `0%` result.
- Missing or conflicting acquisition/source/sale evidence produces `unavailable` or `conflicting`, never zero.
- Partial sales contribute only the explicitly completed quantity.
- Unsold remaining units stay in the denominator.

## Approved supporting fields

Each grouped result may expose:

- exact purchase-source label;
- acquired units;
- completed-sale units;
- remaining unsold units;
- sell-through ratio and percentage;
- period start, period end, and as-of date;
- source-domain coverage;
- evidence state, reason, and provenance.

## Deterministic ordering

Grouped results must be ordered by:

1. evidence state: valid before unavailable before conflicting;
2. sell-through percentage descending for valid groups;
3. completed-sale units descending;
4. acquired units descending;
5. normalized purchase-source label ascending using deterministic case-folded comparison;
6. original source label ascending as the final tie breaker.

This ordering is presentation stability only. It is not an approved business ranking or recommendation.

## Fail-closed outcomes

Return `unavailable` when required evidence or coverage is absent, including blank purchase source, incomplete period coverage, or an unreconstructable denominator.

Return `conflicting` when canonical sources disagree, including ambiguous inventory-to-sale linkage, contradictory quantities, or current state that conflicts with immutable history.

No grouped result may fabricate a percentage, substitute another source, or silently discard unresolved units.

## Explicit exclusions

The baseline does not include:

- revenue, gross profit, net profit, margin, fees, shipping, packaging, or cost-basis comparison;
- settlement completion;
- returns, refunds, cancellations, transfers, write-offs, or cross-period corrections unless later authority defines them;
- source aliases or source-quality scoring;
- product/category normalization or minimum sample thresholds;
- winner/loser labels, rankings, thresholds, recommendations, charts, or exports.

Rows affected by an unresolved excluded lifecycle must fail closed rather than be estimated.

## Contract-entry gate

A later implementation issue may introduce immutable request/result contracts only when it preserves this exact vocabulary, explicit evidence outcomes, provenance, deterministic ordering, and no-ranking boundary. Provider, calculator, catalog, presentation, and UI work remain separately scoped.

## Non-goals

- runtime code or UI behavior;
- database, schema, migration, cache, or duplicated reporting storage;
- live cross-domain execution;
- report registration, chart, export, scheduler, alert, or automation;
- mutation of Inventory, Sales, Pricing, Settlement, or audit authority;
- dependency or CI workflow changes.
