# CAP-012N — Next Reports Business-Question Authority Gate

**Status:** PLAN — approval gate only  
**Capability:** CAP-012 Reports  
**Requirement:** REQ-REP-001  
**Issue:** #732  
**Prior authority issue:** #593  
**Baseline:** `main` at `a7a632d39efd85fb2b3e34c502f326ca7d8812ac`

## Purpose

Define the mandatory approval gate before MarketDEX adds a fourth report, expands Purchase Source Performance beyond its delivered read-only boundary, or adds a live cross-domain query, chart, export, or report-specific persistence path.

This document approves no new business question and authorizes no implementation. It reconciles the current approved Reports set after the merged Purchase Source Performance delivery.

## Current approved Reports set

The current approved Reports capabilities are:

1. **Inventory Age Patterns** — the existing Inventory-sourced, read-only report boundary.
2. **Inventory Turnover** — the existing approved read-only report contract and presentation boundary.
3. **Purchase Source Performance** — the delivered local, read-only, composition-owned query and workspace presentation boundary.

Purchase Source Performance remains limited to its approved local read-only execution, explicit source coverage, provenance, unavailable/conflicting outcomes, and valid empty-result semantics. This gate does not authorize live execution, external providers, networking, exports, persistence, automation, or expanded analytics for that report.

## Candidate selection requirements

A later candidate or extension may proceed only when repository authority contains:

1. the exact workbook-backed business question or extension decision;
2. the operator decision the report or extension is intended to support;
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

A candidate or extension requiring multiple domains must define the read-only composition boundary and preserve the source provenance of every value.

## Fail-closed rule

A later implementation must return an explicit unavailable or conflicting outcome when required evidence, linkage, coverage, freshness, or authority cannot be proven.

Missing evidence is not zero. Conflicting evidence is not a best-effort estimate.

## Blocked until separately approved

- a fourth report definition;
- any expansion of Purchase Source Performance beyond its delivered read-only composition boundary;
- live cross-domain execution;
- charts, comparisons, thresholds, recommendations, or alerts;
- CSV, spreadsheet, PDF, or other exports;
- report-specific storage, cache, schema, or migration;
- background refresh, polling, scheduling, or notifications;
- mutation of any source domain.

## Acceptance gate for implementation

A later implementation issue may begin only after a candidate-specific authority audit records all selection requirements, cites its workbook authority, names its exact source contracts, and defines focused tests.

The implementation must use a separate issue and branch from this planning gate. CAP-012 remains `Partial` until its approved boundaries are expanded with implementation and verification evidence.

## Non-goals

- selecting a candidate by assumption;
- runtime code or UI behavior;
- provider, query, presentation, chart, export, persistence, or mutation work;
- dependency or CI workflow changes;
- changing CAP-006 Collection authority.

## Verification

Documentation-only authority reconciliation. No visual check is required.
