# CAP-010A — Allocation Evidence Revision and Supersession Desktop Boundary

## Authority

Build 502 / REQ-ALL-002.

Canonical workbook artifact:

`artifacts/calc/MarketDEX_Calc_V0_Build502_Allocation_Evidence_Revision_Supersession_Contract.ods`

Merged workbook preservation evidence: PR #115.

## Repository Classification

Workbook contract: Complete.

Desktop implementation: Missing.

CAP-009 Builds 498-500 remain complete and are the permanent allocation evidence and cross-check authority. CAP-010A must extend that architecture and must not create a second allocation architecture.

## Exact Build 502 Workbook Evidence

Direct ODS package inspection confirms the `Allocation Evidence Revisions` sheet contains exactly these seven contract columns:

1. `Allocation Evidence ID`
2. `Revision ID`
3. `Supersedes Revision ID`
4. `Current Revision Flag`
5. `Revision Status`
6. `Revision Conflict`
7. `Revision Authority Boundary`

The canonical workbook derivations are:

- `Revision Status`: `ACTIVE` when Current Revision Flag is `Y`; otherwise `REVISED` when Supersedes Revision ID is present; otherwise `INITIAL`.
- `Revision Conflict`: `CONFLICT` when more than one row for the same Allocation Evidence ID has Current Revision Flag `Y`; otherwise `NO CONFLICT`.
- `Revision Authority Boundary`: `ACTIVE REVISION AUTHORITY ONLY — NO TAX, RECONCILIATION, OR SETTLEMENT COMPLETION AUTHORITY` only when Current Revision Flag is `Y` and Revision Conflict is `NO CONFLICT`; otherwise `NO REVISION AUTHORITY — FAIL CLOSED`.

Canonical Build 502 vocabulary is therefore:

- Current Revision Flag: `Y` or non-`Y`/blank workbook state;
- Revision Status: `ACTIVE`, `REVISED`, `INITIAL`;
- Revision Conflict: `CONFLICT`, `NO CONFLICT`;
- Revision Authority Boundary: `ACTIVE REVISION AUTHORITY ONLY — NO TAX, RECONCILIATION, OR SETTLEMENT COMPLETION AUTHORITY`, `NO REVISION AUTHORITY — FAIL CLOSED`.

## Existing Desktop Support

- CAP-009 `settlement_allocation_evidence` preserves allocation line evidence append-only but has no revision identity or supersession lineage columns.
- `SettlementAllocationRepository` has no revision lineage persistence, current-revision query, or conflict query.
- `SettlementAllocationService` has no Build 502 revision authority derivation.
- Existing immutable triggers and transaction patterns are reusable.
- No direct Build 502 desktop contract tests exist.

## Smallest Missing Vertical Slice

Implement an append-only allocation evidence revision authority table in `core/schema.py`, extending the established runtime database authority. Extend `SettlementAllocationRepository` and `SettlementAllocationService` only enough to:

1. require explicit Allocation Evidence ID and Revision ID;
2. preserve optional explicit Supersedes Revision ID;
3. accept only canonical current-revision flag `Y` or blank;
4. derive `ACTIVE`, `REVISED`, or `INITIAL` exactly from workbook rules;
5. derive `CONFLICT` when multiple current revisions exist for one Allocation Evidence ID;
6. grant active revision authority only for a current revision with no conflict;
7. preserve every prior revision without update/delete;
8. make identical replay idempotent and contradictory replay fail closed;
9. reconstruct revision authority from persisted evidence after restart.

This slice does not mutate CAP-009 allocation evidence, revise settlement truth, execute settlement, or implement Build 503 locking.

## Prohibited Architecture

Do not mutate or overwrite prior allocation evidence.

Do not replace CAP-009 allocation evidence or cross-check authority.

Do not infer missing revision identity or supersession linkage.

Do not automatically match, allocate, redistribute, reconcile, complete settlement, or introduce tax authority.

Do not create a second launcher, application root, database authority, or competing allocation service.

## Implementation Gate

Exact workbook field and vocabulary evidence is now inspected and recorded. CAP-010A may proceed only through the smallest missing vertical slice above.