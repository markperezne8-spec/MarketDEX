# CAP-006D — Permanent Collection CI Gate

**Status:** BUILD

## Purpose

Register the authorized CAP-006 read-only Collection Position contract as a dedicated permanent CI gate. CAP-006C strengthened the tests, but the existing workflow did not invoke the Collection service and workspace suites directly.

## Protected contract

The Collection CI gate must run:

- `tests/test_cap006_collection_position_slice.py`;
- `tests/test_cap006_collection_position_workspace.py`;
- Collection navigation coverage in `tests/test_cap005c_product_registry_navigation.py`.

The gate protects deterministic ordering, bounded search, restart reconstruction, empty and unmatched behavior, zero mutation of Product Registry and Inventory authority, explicit absence of condition/grade and collector intent, read-only workspace behavior, and canonical shell registration.

## Authority boundary

This gate verifies the existing query-only projection. It does not authorize Collection persistence, CRUD, lifecycle commands, enums, valuation, grading, wishlist behavior, Portfolio, Reports, market data, or automatic Inventory conversion.

## Completion rule

CAP-006D is complete when the dedicated `Collection` CI job passes on the pull request and remains registered in `.github/workflows/ci.yml`.
