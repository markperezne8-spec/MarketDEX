# CAP-009C — Sale-Level Settlement Attribution Readiness

## Authority
Build 500 / REQ-ALL-001.

## Delivery Boundary
Derive and persist whether a sale-linked allocation line is ready for settlement attribution using only canonical persisted settlement evidence, allocation evidence, and the latest eligible Build 499 group cross-check result.

## Required Gate
A sale attribution readiness result may be READY only when:

1. the allocation group exists;
2. every evaluated allocation line is persisted and sale-linked;
3. the allocation line is `READY FOR CROSS-CHECK`;
4. allocated amount evidence is known;
5. the linked sale exists through canonical SOLD_CONVERSION lifecycle evidence;
6. the sale marketplace matches the Settlement Evidence parent marketplace;
7. an append-only group cross-check result exists for the same parent and allocation group;
8. that cross-check result is `ALLOCATION CROSS-CHECKED`;
9. the signed allocation remainder is exactly zero.

Any missing or contradictory authority fails closed as NOT READY. This capability does not execute settlement, close an order, mutate allocation evidence, revise evidence, redistribute money, or infer missing allocation values.

## Persistence Grain
Append-only sale + allocation group readiness evidence. Identical replay is idempotent. Contradictory replay is blocked. Restart reconstruction must use persisted authority only.

## Explicit Exclusions
Automatic matching; automatic allocation; redistribution; evidence revision or supersession; allocation locks; settlement execution/completion changes; order closure; tax authority; UI; second launcher; second database authority.
