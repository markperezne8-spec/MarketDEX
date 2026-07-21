# CAP-012N — Next Reports Business-Question Authority Gate

**Status:** PLAN — approval gate only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #593  
**Baseline:** `main` at `229e9749912a1ceb2a335f9dafd52a4b9e38dfad`

## Purpose

Define the mandatory approval gate before MarketDEX adds a third report, live cross-domain query, chart, export, or report-specific persistence path.

This document approves no new business question. Inventory Age Patterns and Inventory Turnover remain the only approved Reports capabilities.

## Candidate selection requirements

A later candidate may proceed only when repository authority contains:

1. the exact workbook-backed business question;
2. the operator decision the report is intended to support;
3. the approved population grain;
4. period, as-of, freshness, and correction semantics;
5. exact source-domain ownership for every required fact;
6. explicit exclusions so neighboring capabilities are not substituted;
7. unavailable, non-found, and conflicting evidence behavior;
8. approved formula or projection vocabulary;
9. deterministic ordering and presentation requirements;
10. focused verification and CI ownership.

## Source-authority rule

Each field must have one canonical owner. Inventory, Listing, Pricing, Settlement, Collection, Product Registry, Market Intelligence, and Audit facts must not be collapsed into a new reporting authority.

A candidate requiring multiple domains must define the read-only composition boundary and preserve the source provenance of every value.

## Fail-closed rule

A later implementation must return an explicit unavailable or conflicting outcome when required evidence, linkage, coverage, freshness, or authority cannot be proven.

Missing evidence is not zero. Conflicting evidence is not a best-effort estimate.

## Blocked until separately approved

- a third report definition;
- live cross-domain execution;
- charts, comparisons, thresholds, recommendations, or alerts;
- CSV, spreadsheet, PDF, or other exports;
- report-specific storage, cache, schema, or migration;
- background refresh, polling, scheduling, or notifications;
- mutation of any source domain.

## Acceptance gate for implementation

A later implementation issue may begin only after a candidate-specific authority audit records all selection requirements, cites its workbook authority, names its exact source contracts, and defines focused tests.

The implementation must use a separate issue and branch from this planning gate.

## Non-goals

- selecting a candidate by assumption;
- runtime code or UI behavior;
- provider, query, presentation, chart, export, persistence, or mutation work;
- dependency or CI workflow changes.
