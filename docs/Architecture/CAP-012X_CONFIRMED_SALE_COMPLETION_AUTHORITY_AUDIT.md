# CAP-012X Confirmed Sale-Completion Authority Audit

## Status

Planning-first authority checkpoint after CAP-012W. Purchase Source Performance provider implementation remains blocked unless MarketDEX exposes a permanent, read-only, fail-closed sale-completion authority with exact acquired-inventory linkage.

## Audit question

Does the permanent repository architecture define all of the following together:

- confirmed completed-sale unit quantity;
- authoritative completion date;
- stable sale identity;
- exact linkage from each completed unit to the acquired inventory identity;
- deterministic handling of partial, duplicate, superseded, reversed, or contradictory completion evidence?

## Repository-search result

Repository search did not surface a clear canonical path containing an exact `sale_id` to `inventory_id` completion relationship. Searches covering sale completion, completed timestamps, fulfillment, settlement allocation, and inventory linkage did not establish a permanent read model that satisfies the full CAP-012V evidence gate.

Existing settlement-allocation, audit, dashboard, report-contract, calculator, preview, and test surfaces may mention completed sales or sold units, but those references do not independently establish sale-completion authority. Settlement evidence proves financial allocation state; it must not be treated as proof that an exact acquired inventory unit completed a sale.

## Rejected inference paths

The following are not authoritative linkage and must never be used by the report provider:

- product name, SKU text, listing title, or marketplace label matching;
- price, fee, payout, settlement amount, or allocation similarity;
- temporal proximity between an inventory change and a marketplace event;
- source aliases, fuzzy matching, case folding, or punctuation folding;
- dashboard projections, report previews, calculators, fixtures, or tests;
- settlement or allocation records lacking exact inventory identity.

## Required permanent authority

A future sale-completion boundary must expose immutable read-only evidence containing:

1. stable sale identity;
2. stable acquired-inventory identity;
3. confirmed completed-unit quantity;
4. authoritative completion timestamp or date;
5. explicit lifecycle state distinguishing pending, completed, cancelled, refunded, reversed, or superseded evidence;
6. deterministic lineage for corrections and duplicate detection;
7. fail-closed outcomes for missing, partial, impossible, or contradictory records.

The identity relationship must be stored or derived from canonical persisted authority. It cannot be reconstructed from descriptive text or financial coincidence.

## Decision

CAP-012X does **not** authorize Purchase Source Performance provider implementation.

The repository currently lacks sufficiently proven sale-completion authority for exact acquired-inventory linkage. Missing completion evidence must remain unavailable or conflicting under the existing CAP-012R through CAP-012T contracts; it must not be converted into zero completed units.

## Next gate

The next controlled build must define a planning-only canonical sale-completion evidence contract before any schema, repository, service, provider, composition, registration, or UI work begins. That contract must define identity, lifecycle, quantities, dates, reversals, lineage, immutability, and fail-closed semantics.

## Explicitly unauthorized

- Purchase Source Performance provider implementation;
- ad hoc SQLite joins or cross-domain report queries;
- schema, persistence, repository, or service implementation;
- report registration, application composition, or live execution;
- UI, presenter, preview, chart, export, or operator workflow;
- settlement-to-sale inference;
- ranking, recommendation, revenue, cost, margin, return, or trend metrics;
- source aliasing, fuzzy matching, networking, polling, marketplace APIs, or writes.
