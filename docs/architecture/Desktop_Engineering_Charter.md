# MarketDEX OS Desktop Engineering Charter

## Status
Accepted foundation governance baseline.

## Roles
The Product Owner defines business priorities, performs acceptance testing, and approves product behavior. The Lead Software Architect defines technical structure, implementation boundaries, traceability, regression protection, and production increments.

## Delivery Model

- One controlled engineering boundary per branch.
- One pull request per delivery boundary.
- `main` remains releasable.
- Every completed sprint produces a tangible repository artifact.
- No partial operational workflow is considered complete.

## Definition of Done

1. Specification: behavior traces to the workbook business specification.
2. Implementation: the required architectural layers are complete for the delivery boundary.
3. Verification: automated tests or controlled regression evidence prove expected behavior.
4. Documentation: architecture and traceability records are updated when affected.

## Coding Rules

- One responsibility per class or module boundary.
- No authoritative business logic in PySide6 UI code.
- No SQL in UI code.
- Repository ports isolate persistence.
- Services orchestrate use cases.
- Domain code is independent of PySide6 and SQLite where practical.
- Production Python uses type hints.
- Unexpected failures are logged and surfaced through controlled application error handling.
- Schema evolution uses explicit versioning and migrations.

## Initial Release Sequence

1. Application Foundation
2. Inventory Vertical Slice
3. Product Registry
4. Collection
5. Dashboard and Reports
6. Settlement and Allocation Authority

## Permanent Codebase Rule
There is one permanent desktop codebase. Experimental work may occur on feature branches but must not create a competing long-lived application architecture.
