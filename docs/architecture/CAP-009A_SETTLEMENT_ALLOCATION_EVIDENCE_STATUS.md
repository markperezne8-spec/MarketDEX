# CAP-009A — Settlement Allocation Evidence Persistence + Fail-Closed Status Derivation

Status: DESIGN LOCK

## Parent authority

CAP-009A extends the permanent CAP-008A Settlement Evidence parent authority.

Every allocation group belongs to exactly one `settlement_evidence_id`.

Settlement Allocation Evidence is not the existing `marketplace_allocations` inventory reservation model and must not reuse that table as if the concepts were equivalent.

SETTLEMENT EVIDENCE != SETTLEMENT ALLOCATION != MARKETPLACE INVENTORY ALLOCATION != SETTLEMENT EXECUTION

## Build 498 canonical intake grain

The persistent intake grain is one allocation evidence line within one allocation group.

Canonical fields:

- `allocation_group_id` — immutable group identity.
- `allocation_line_id` — immutable line identity.
- `settlement_evidence_id` — required canonical CAP-008A parent identity.
- `linked_sale_id` — nullable evidence relationship. NULL means UNKNOWN and must not be inferred.
- `source_traceability` — required evidence/source traceability.
- `evidence_date` — required evidence date.
- `currency` — required canonical currency; initial accepted scope USD.
- `component_type` — required allocation component classification.
- `allocated_amount_minor` — nullable monetary evidence. NULL means UNKNOWN; zero is an evidenced numeric value.
- `notes` — operator evidence notes; blank text is permitted.
- `allocation_status` — derived canonical Build 498 status.
- `created_event_id` — stable event/audit relationship.
- `created_at` — immutable creation timestamp.

## Canonical status vocabulary

Only these values are accepted:

- `NOT READY`
- `PENDING EVIDENCE`
- `READY FOR CROSS-CHECK`
- `ALLOCATION EXCEPTION`
- `ALLOCATION CROSS-CHECKED`

CAP-009A derives only the Build 498 intake states. `ALLOCATION CROSS-CHECKED` is reserved for the later Build 499 cross-check authority and must not be produced by CAP-009A intake.

## Fail-closed status derivation

Status is derived by service authority; callers may not authoritatively supply it.

1. If the Settlement Evidence parent does not exist, persistence is blocked.
2. If required identity or source evidence is blank, status is `NOT READY` and no authoritative allocation evidence line is committed.
3. If `linked_sale_id` is NULL, status is `PENDING EVIDENCE`.
4. If `allocated_amount_minor` is NULL, status is `PENDING EVIDENCE`.
5. If a supplied `linked_sale_id` does not resolve to an existing sale, status is `ALLOCATION EXCEPTION`.
6. If parent marketplace evidence and linked sale marketplace evidence contradict, status is `ALLOCATION EXCEPTION`.
7. If required evidence is present, linked sale evidence resolves, marketplace evidence agrees, and allocated amount is known, status is `READY FOR CROSS-CHECK`.
8. CAP-009A never derives `ALLOCATION CROSS-CHECKED`.

Blank or missing allocated amount must never be coerced to zero.

## Persistence and immutability

Accepted allocation evidence lines are append-only.

Identical replay of one `allocation_line_id` is idempotent.

Contradictory evidence for an existing `allocation_line_id` fails closed.

One allocation group cannot change Settlement Evidence parent identity after its first accepted line.

Restart reconstruction must recover the same group, line, parent, nullable evidence, and derived status.

## Preservation rules

CAP-009A must not:

- change `marketplace_allocations` inventory reservation semantics;
- change M24 sale authority;
- change M30 SOLD conversion;
- change M39A settlement execution authority;
- execute Build 499 allocation totals, remainder, or cross-check authority;
- execute Build 500 sale-level settlement attribution readiness;
- infer a sale from marketplace, amount, date, or notes;
- automatically allocate settlement money;
- create tax authority;
- create order closure;
- add a second launcher or database authority;
- add UI in this delivery boundary.

## Acceptance contract

CAP-009A is accepted when automated tests prove:

1. Allocation evidence persists only against an existing Settlement Evidence parent.
2. Group and line identities reconstruct after restart.
3. NULL linked sale remains UNKNOWN and derives `PENDING EVIDENCE`.
4. NULL allocated amount remains UNKNOWN and derives `PENDING EVIDENCE`.
5. Zero allocated amount remains numeric zero and is not treated as blank.
6. Unresolved linked sale evidence derives `ALLOCATION EXCEPTION`.
7. Marketplace contradiction derives `ALLOCATION EXCEPTION`.
8. Complete agreeing intake derives `READY FOR CROSS-CHECK`.
9. CAP-009A cannot derive `ALLOCATION CROSS-CHECKED`.
10. Identical line replay is idempotent.
11. Contradictory line replay fails closed.
12. One group cannot be re-parented to another Settlement Evidence ID.
13. Existing marketplace inventory allocation behavior remains unchanged.
14. Existing M39A settlement behavior remains unchanged.
