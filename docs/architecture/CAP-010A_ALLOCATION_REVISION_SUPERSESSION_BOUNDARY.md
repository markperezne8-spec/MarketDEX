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

## Verified Build 502 Contract Boundary

Repository evidence from merged PR #115 confirms Build 502 requires:

- immutable allocation evidence revision history;
- Allocation Evidence ID identity control;
- Revision ID identity control;
- Supersedes Revision linkage;
- current revision handling;
- revision conflict detection;
- fail-closed revision authority;
- preservation of historical evidence without overwriting prior records.

Build 502 explicitly does not introduce tax authority, reconciliation authority, settlement completion authority, automatic matching, or automatic allocation.

## Controlled Desktop Delivery Boundary

Before implementation, map the exact Build 502 workbook fields and canonical vocabulary against:

- `core/schema.py`;
- `repositories/settlement_allocation_repository.py`;
- `services/settlement_allocation_service.py`;
- CAP-009A/B/C contract tests;
- immutable audit/event infrastructure.

Then implement only the smallest missing vertical slice required to persist immutable revision lineage, identify the current revision deterministically, reject contradictory or invalid supersession, preserve prior allocation evidence, reconstruct authority after restart, and prove the behavior in Core Tests CI.

## Prohibited Architecture

Do not mutate or overwrite prior allocation evidence.

Do not replace CAP-009 allocation evidence or cross-check authority.

Do not infer missing revision identity or supersession linkage.

Do not automatically match, allocate, redistribute, reconcile, complete settlement, or introduce tax authority.

Do not create a second launcher, application root, database authority, or competing allocation service.

## Implementation Gate

No schema, repository, or service implementation begins until exact workbook field/vocabulary evidence is available for inspection. Repository truth must remain stronger than chat inference.
