# CAP-006D — Permanent Collection CI Gate

**Status:** COMPLETE  
**Capability:** CAP-006 Collection  
**Requirement:** REQ-COL-001  
**Issue:** #734  
**Baseline:** `main` at `ead906a8aa53249aae47ce41d15b7cf9ea929a36`

## Purpose

Register the authorized CAP-006 read-only Collection Position contract as a dedicated permanent CI gate. CAP-006C strengthened the tests, and the repository workflow now invokes the Collection service and workspace suites directly.

## Protected contract

The Collection CI gate runs:

- `tests/test_cap006_collection_position_slice.py`;
- `tests/test_cap006_collection_position_workspace.py`;
- Collection navigation coverage in `tests/test_cap005c_product_registry_navigation.py`.

The gate protects deterministic ordering, bounded search, restart reconstruction, empty and unmatched behavior, zero mutation of Product Registry and Inventory authority, explicit absence of condition/grade and collector intent, read-only workspace behavior, and canonical shell registration.

## Verified workflow evidence

The `Collection` job is registered in `.github/workflows/ci.yml` and executes the three protected test paths.

CI [Run #1025](https://github.com/markperezne8-spec/MarketDEX/actions/runs/31927716466) passed for exact PR #733 head `a0bd78a4454ad7e9db722515f636aacb52867450`, including the dedicated Collection job.

## Authority boundary

This gate verifies the existing query-only projection. It does not authorize Collection persistence, CRUD, lifecycle commands, enums, valuation, grading, wishlist behavior, Portfolio, Reports, market data, or automatic Inventory conversion.

CAP-006 remains `Partial` and blocked on workbook-backed position grain, field vocabulary, evidence ownership, lifecycle, and Inventory transition authority.

## Completion rule

CAP-006D is complete because the dedicated `Collection` CI job is registered in `.github/workflows/ci.yml`, runs the protected test paths, and passed in CI.

## Verification

Documentation-only evidence reconciliation. No visual check is required.
