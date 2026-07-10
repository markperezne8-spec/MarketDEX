# CAP-009B — Allocation Group Cross-Check + Allocation Remainder

Status: DESIGN LOCK

## Repository classification

CAP-009 is Partial. CAP-009A delivered Build 498 settlement allocation evidence intake. Repository and merged-PR search found no existing Build 499 group total, allocation remainder, or cross-check authority. CAP-009B extends the existing Settlement Evidence parent and Settlement Allocation Evidence grain; it does not create a second allocation architecture.

## Canonical authority

One allocation group belongs to exactly one `settlement_evidence_id`.

Build 499 cross-check compares the sum of evidenced allocation line amounts for one allocation group against the canonical parent `settlement_evidence.settlement_net_minor`.

Canonical derived values:

- `allocation_group_total_minor` — sum of known `allocated_amount_minor` values for accepted group lines.
- `settlement_net_minor` — canonical CAP-008A parent net evidence.
- `allocation_remainder_minor` — `settlement_net_minor - allocation_group_total_minor`.
- `cross_check_status` — derived Build 499 authority result.

## Fail-closed rules

1. Missing allocation group blocks cross-check authority.
2. Missing Settlement Evidence parent blocks cross-check authority.
3. A group containing any `NOT READY`, `PENDING EVIDENCE`, or `ALLOCATION EXCEPTION` line is not cross-check eligible.
4. A group containing any NULL `allocated_amount_minor` is not cross-check eligible. NULL remains UNKNOWN and is never coerced to zero.
5. A group containing lines with contradictory Settlement Evidence parent identity is blocked.
6. The group total is derived only from persisted canonical allocation evidence lines. Callers cannot supply an authoritative group total.
7. Allocation remainder is derived only from canonical parent net evidence minus the derived group total. Callers cannot supply an authoritative remainder.
8. Remainder equal to zero derives `ALLOCATION CROSS-CHECKED`.
9. Non-zero remainder derives `ALLOCATION EXCEPTION` and preserves the signed remainder as evidence.
10. Cross-check authority never invents, edits, or redistributes allocation line amounts.
11. Cross-check authority never infers a sale relationship.
12. Build 499 does not execute Build 500 sale-level Settlement Attribution Readiness.

## Persistence

Build 499 results are append-only cross-check evidence at allocation-group grain.

Canonical result fields:

- `cross_check_id` — immutable result identity.
- `allocation_group_id` — canonical group identity.
- `settlement_evidence_id` — canonical parent identity.
- `allocation_group_total_minor` — derived group total.
- `settlement_net_minor` — parent net snapshot used by the cross-check.
- `allocation_remainder_minor` — signed derived remainder.
- `cross_check_status` — `ALLOCATION CROSS-CHECKED` or `ALLOCATION EXCEPTION`.
- `created_event_id` — stable event/audit relationship.
- `created_at` — immutable creation timestamp.

Identical replay of one `cross_check_id` is idempotent. Contradictory replay fails closed. A successfully persisted result reconstructs identically after restart.

Build 499 does not mutate append-only CAP-009A allocation lines. `ALLOCATION CROSS-CHECKED` is Build 499 result authority, not a retroactive rewrite of Build 498 line evidence.

## Preservation rules

CAP-009B must not change marketplace inventory allocation semantics, M24 sale authority, M30 SOLD conversion, M39A settlement execution, CAP-008A Settlement Evidence parent authority, or CAP-009A intake derivation.

CAP-009B must not automatically match sales, automatically allocate money, create tax authority, create settlement completion authority, create order closure, add UI, add a second launcher, or add a second database authority.

## Acceptance contract

Automated tests must prove:

1. Missing group fails closed.
2. Missing or inconsistent parent authority fails closed.
3. Pending, exception, or unknown-amount lines are not cross-check eligible.
4. Group total is derived from persisted canonical line evidence.
5. Zero remainder derives `ALLOCATION CROSS-CHECKED`.
6. Positive and negative non-zero remainder derive `ALLOCATION EXCEPTION` and preserve the signed remainder.
7. Caller cannot authoritatively supply group total, remainder, or status.
8. Cross-check does not mutate allocation evidence lines.
9. Identical replay is idempotent.
10. Contradictory replay fails closed.
11. Result reconstruction survives restart.
12. CAP-009A and M39A regression behavior remains unchanged.
13. Build 500 sale-level attribution readiness is not introduced.
