# CAP-008A — Settlement Evidence Parent Grain Contract Reconciliation

Status: DESIGN LOCK

## Problem

The accepted desktop `SettlementService` and `settlement_executions` table model one SETTLED execution as belonging to exactly one completed sale. `sale_id` is required and unique, and expected payout is derived from that single sale's M24 financial history.

The accepted workbook Settlement Allocation Contract uses a different canonical parent grain: one marketplace Settlement Evidence ID may cover one sale, multiple sales, adjustments, reserves, refunds, or other marketplace-controlled financial movements. Allocation groups belong to one Settlement Evidence ID; sale linkage is optional evidence and blank means UNKNOWN.

CAP-009 cannot truthfully persist allocation groups against the existing single-sale `settlement_executions` row without creating a false parent relationship.

## Locked authority distinction

`SETTLEMENT EVIDENCE` is the canonical marketplace payout evidence parent.

`SETTLEMENT EXECUTION` remains the accepted M39A controlled SETTLED authority for the legacy single-sale exact-payout path.

`SETTLEMENT ALLOCATION` is a child attribution process of Settlement Evidence and may later establish sale-level attribution only after accepted cross-check authority.

These concepts must remain distinct:

SETTLEMENT EVIDENCE != SETTLEMENT EXECUTION != SETTLEMENT ALLOCATION != ORDER CLOSURE

## Smallest safe extension

Add an append-only `settlement_evidence` parent authority surface before CAP-009.

Canonical parent identity:

- `settlement_evidence_id` — immutable primary identifier.
- `marketplace` — canonical marketplace identity.
- `marketplace_settlement_reference` — traceable marketplace payout reference.
- `settlement_date` — evidence date.
- `settlement_currency` — canonical currency; initial accepted scope USD.
- `evidence_source_type` — MANUAL_ENTRY, MARKETPLACE_EXPORT, or MARKETPLACE_REPORT.
- `evidence_source_reference` — traceable source reference.
- `settlement_gross_minor` — nullable; blank is UNKNOWN.
- `settlement_fee_minor` — nullable; blank is UNKNOWN.
- `settlement_adjustment_minor` — nullable; blank is UNKNOWN.
- `settlement_net_minor` — required for verified settlement evidence parent authority.
- `evidence_status` — accepted settlement evidence lifecycle vocabulary.
- `verification_result` — accepted settlement verification vocabulary.
- `created_event_id` and timestamps — stable event/audit/restart reconstruction relationship.

Financial component nullability is intentional. NULL means UNKNOWN. Zero is an evidenced numeric value and must never be substituted for blank evidence.

## Preservation rules

CAP-008A must not redesign M24 sale authority.

CAP-008A must not change M30 SOLD conversion.

CAP-008A must not weaken or rewrite existing `settlement_executions` or `settlement_history` rows.

CAP-008A must not convert legacy single-sale settlement rows into multi-sale records by assumption.

CAP-008A must not create automatic sale matching, automatic allocation, reconciliation authority, tax authority, or settlement completion authority.

Existing M39A `SettlementService.execute_settlement()` remains accepted for its current single-sale exact-payout contract until a later explicitly accepted migration boundary changes that execution authority.

## Compatibility bridge

For every newly accepted M39A settlement execution, the same controlled transaction may ensure one canonical Settlement Evidence parent exists for `settlement_evidence_id` using the evidence already supplied to M39A, but only within the evidence actually known by that execution boundary.

The compatibility bridge may assert:

- Settlement Evidence ID.
- Marketplace.
- Evidence source identity represented by the accepted M39A evidence ID boundary.
- Settlement net amount equal to the accepted observed payout.
- Verified settlement evidence result because M39A already requires complete evidence and exact expected-net cross-check before SETTLED execution.

The bridge must leave unknown gross, fee, and adjustment evidence NULL. It must not infer those marketplace-reported components from M24 derived financial truth.

The bridge creates no second settlement execution and no second financial event.

## CAP-009 dependency release condition

CAP-009 may resume only after desktop persistence can reconstruct a canonical Settlement Evidence parent independently of `sale_id` and allocation groups can reference that parent identity without requiring a sale relationship.

## Acceptance contract

CAP-008A is accepted when automated tests prove:

1. Settlement Evidence parent identity persists independently of `sale_id`.
2. One Settlement Evidence parent can exist without sale-level attribution.
3. Nullable financial components remain NULL/UNKNOWN and are not coerced to zero.
4. Existing M39A settlement execution behavior remains exactly-once and replay protected.
5. Existing M39A execution creates or confirms one compatible Settlement Evidence parent without duplicate parent mutation.
6. Parent reconstruction survives restart.
7. Contradictory evidence for an existing Settlement Evidence ID fails closed.
8. Zero inventory mutation, zero second sale, zero second M24 financial event, and zero order closure are preserved.
9. CAP-009 can reference Settlement Evidence ID as its canonical parent without referencing `settlement_executions.sale_id`.
