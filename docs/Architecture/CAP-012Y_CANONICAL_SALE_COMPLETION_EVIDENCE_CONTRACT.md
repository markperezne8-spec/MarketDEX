# CAP-012Y Canonical Sale-Completion Evidence Contract

## Status

Approved planning contract only. This document defines the minimum canonical evidence semantics required before MarketDEX may implement any permanent sale-completion persistence, repository, service, report provider, registration, composition, or UI path.

## Authority boundary

Sale completion is its own business authority. It is not established by settlement, payout, allocation, marketplace text, listing text, product text, SKU similarity, price similarity, timestamp proximity, dashboard projections, report previews, fixtures, or tests.

A valid sale-completion record must carry explicit canonical identity and lifecycle evidence. Descriptive or financial coincidence must never be used to reconstruct identity.

## Required immutable identity

Each sale-completion evidence record must expose:

- `sale_id`: stable identity for the sale lifecycle;
- `sale_completion_evidence_id`: stable identity for the immutable evidence record;
- `inventory_id`: stable identity of the acquired inventory record affected;
- `lineage_parent_evidence_id`: optional direct predecessor when the record corrects, reverses, or supersedes earlier evidence;
- `source_system`: exact authoritative domain that emitted the evidence;
- `recorded_at`: immutable timestamp when MarketDEX accepted the evidence.

Identity values must be persisted or supplied by canonical authority. They may not be synthesized from mutable descriptive fields.

## Quantity semantics

`completed_unit_quantity` must be a positive whole-unit quantity for a completed event and must identify the exact quantity belonging to the linked `inventory_id`.

The contract forbids:

- negative completed quantities;
- fractional quantities where the inventory grain is whole units;
- quantities exceeding the authoritative acquired or remaining allocable quantity without explicit conflict evidence;
- silent aggregation across different inventory identities;
- interpreting absence of completion evidence as zero.

A zero completed quantity is not a completed event. Valid zero for downstream reporting exists only when authoritative coverage proves no completed events for the requested identity and period.

## Completion-date authority

`completed_at` is the authoritative business timestamp at which the linked units entered the confirmed completed state.

`completed_at` must not be replaced by:

- settlement date;
- payout date;
- import date;
- listing date;
- order-created date;
- shipping date;
- local file modification time;
- nearest available timestamp.

When the source cannot provide authoritative completion time, the evidence is unavailable rather than approximated.

## Lifecycle vocabulary

The canonical lifecycle states are:

- `pending`;
- `completed`;
- `cancelled`;
- `refunded`;
- `reversed`;
- `superseded`.

Only `completed` evidence contributes completed units.

`cancelled` evidence contributes no completed units.

`refunded`, `reversed`, and `superseded` evidence must preserve immutable lineage to the prior evidence they negate or replace. Historical records are never overwritten in place.

## Correction and reversal lineage

Corrections must append new immutable evidence.

A correction, reversal, refund, or supersession must:

1. identify the exact predecessor evidence;
2. preserve the same canonical `sale_id` unless the source explicitly establishes a distinct sale;
3. preserve exact `inventory_id` linkage or fail closed;
4. state the resulting lifecycle effect explicitly;
5. produce deterministic lineage ordering.

Broken, cyclic, branching-without-authority, or multiply active lineage is conflicting evidence.

## Duplicate semantics

Duplicate detection must rely on canonical evidence identity and lineage, not descriptive similarity.

The following are conflicts unless the canonical source explicitly defines them as distinct:

- repeated active evidence with the same `sale_completion_evidence_id`;
- more than one active terminal record for the same authoritative lifecycle position;
- duplicated completed quantities for the same evidence identity;
- the same completed unit allocation linked to multiple inventory identities;
- overlapping active allocations that exceed authoritative inventory quantity.

No duplicate may be silently dropped when doing so could change completed-unit totals.

## Coverage semantics

A sale-completion read boundary must report the coverage actually evaluated, including:

- source domains consulted;
- sale identities evaluated;
- inventory identities evaluated;
- time range and as-of boundary;
- whether evidence was complete, unavailable, partial, or conflicting;
- deterministic evidence ordering.

Incomplete coverage must never be converted into a valid zero result.

## Fail-closed outcomes

The boundary must return unavailable or conflicting semantics when any of the following occurs:

- missing canonical `sale_id`;
- missing canonical `inventory_id`;
- missing authoritative `completed_at` for completed evidence;
- unsupported lifecycle state;
- impossible quantity;
- ambiguous active lineage;
- broken predecessor reference;
- duplicate authoritative evidence;
- conflicting inventory linkage;
- read exception;
- unsupported response type;
- incomplete coverage that could change totals.

The boundary must not guess, infer, backfill, alias, fuzzy match, rank, or silently omit evidence.

## Deterministic ordering

Evidence ordering must be stable and based on canonical immutable fields. At minimum, ordering must distinguish:

1. authoritative business timestamp when present;
2. `recorded_at`;
3. `sale_id`;
4. `inventory_id`;
5. `sale_completion_evidence_id`.

Equivalent input evidence must produce equivalent ordering across runs.

## Relationship to Purchase Source Performance

This contract does not itself authorize Purchase Source Performance provider implementation.

A future provider may consume sale-completion evidence only after a separately approved implementation establishes a permanent read-only boundary conforming to this contract and proves exact linkage to the Inventory acquisition authority required by CAP-012V through CAP-012X.

Missing completion evidence remains unavailable or conflicting under CAP-012R through CAP-012T. It must not be interpreted as zero completed units.

## Explicitly unauthorized

CAP-012Y does not authorize:

- schema or migration implementation;
- persistence tables or event stores;
- repository or service implementation;
- sale import or marketplace integration;
- Purchase Source Performance provider implementation;
- report registration or application composition;
- live execution, UI, preview, presenter, chart, or export;
- settlement-to-sale inference;
- text-, SKU-, product-, price-, marketplace-, or timestamp-based identity inference;
- financial metrics, ranking, recommendation, networking, polling, or writes.

## Next gate

The next controlled build may define only the implementation boundary for a permanent immutable sale-completion evidence model and read API conforming to this contract. Runtime implementation remains separately gated.